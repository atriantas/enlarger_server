"""
mDNS (Multicast DNS) Responder for MicroPython
Proper implementation for Raspberry Pi Pico 2 W

This library enables mDNS service discovery on MicroPython v1.27.0+
by running a continuous responder that answers .local hostname queries.

IMPORTANT: mDNS in AP mode has limitations - see notes below.
"""

import socket
import struct
import time
import network
import asyncio


# mDNS constants
MDNS_ADDR = "224.0.0.251"
MDNS_PORT = 5353
DNS_TYPE_A = 1
DNS_TYPE_PTR = 12
DNS_TYPE_SRV = 33
DNS_TYPE_TXT = 16
DNS_CLASS_IN = 1
DNS_CLASS_FLUSH = 0x8000


class MDNS:
    """
    mDNS Responder for MicroPython
    
    Listens for mDNS queries and responds with hostname → IP mapping.
    Works in both AP and STA modes.
    """
    
    def __init__(self, hostname=None, ip=None):
        """
        Initialize mDNS responder
        
        Args:
            hostname (str): Device hostname without .local (default: network.hostname())
            ip (str): IP address to advertise (default: auto-detect)
        """
        self.hostname = (hostname or self._get_hostname()).lower()
        self.ip = ip
        self.sock = None
        self.running = False
        self._task = None
        
    def _get_hostname(self):
        """Get current hostname"""
        try:
            return network.hostname()
        except:
            return "pico-w"
    
    def _get_ip(self):
        """Get IP address of active interface"""
        if self.ip:
            return self.ip
        
        try:
            # Try AP interface first (for AP mode)
            ap = network.WLAN(network.AP_IF)
            if ap.active():
                return ap.ifconfig()[0]
            
            # Try STA interface
            sta = network.WLAN(network.STA_IF)
            if sta.active() and sta.isconnected():
                return sta.ifconfig()[0]
        except Exception as e:
            print(f"mDNS: Error getting IP: {e}")
        
        return "192.168.4.1"  # Default AP IP
    
    def start(self, port=MDNS_PORT):
        """
        Start mDNS responder
        
        Returns:
            bool: True if started successfully
        """
        import time
        
        try:
            # Close any existing socket first
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
            
            # Give the OS a moment to release the port
            time.sleep(0.5)
            
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Allow reuse of socket address (helps with quick restarts)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to set SO_REUSEPORT if available (Linux/MicroPython)
            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except (AttributeError, OSError):
                # SO_REUSEPORT not available on this platform
                pass
            
            # Bind to all interfaces on mDNS port
            # Note: We bind to 0.0.0.0, not the multicast address
            self.sock.bind(('0.0.0.0', port))
            
            # Set socket to non-blocking for async operation
            self.sock.setblocking(False)
            
            self.running = True
            
            # Start the responder task
            self._task = asyncio.create_task(self._responder_loop())
            
            print(f"✅ mDNS responder started")
            print(f"   Hostname: {self.hostname}.local → {self._get_ip()}")
            
            return True
            
        except OSError as e:
            # Handle specific errors
            if e.args[0] == 98:  # EADDRINUSE
                print(f"⚠️  mDNS port {port} still in use after wait - try rebooting Pico")
            elif e.args[0] == 12:  # ENOMEM
                print(f"⚠️  mDNS skipped: Not enough memory")
            else:
                print(f"⚠️  mDNS start failed: {e}")
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
            return False
            
        except Exception as e:
            print(f"⚠️  mDNS start failed: {e}")
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
            return False
    
    def stop(self):
        """Stop mDNS responder"""
        self.running = False
        
        if self._task:
            self._task.cancel()
            self._task = None
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        
        print("mDNS responder stopped")
    
    async def _responder_loop(self):
        """Main responder loop - listens and responds to queries"""
        print(f"mDNS: Listening for queries for '{self.hostname}.local'...")
        
        while self.running:
            try:
                # Try to receive data (non-blocking)
                try:
                    data, addr = self.sock.recvfrom(512)
                    
                    # Check if it's a query for our hostname
                    if self._is_query_for_us(data):
                        print(f"mDNS: Query from {addr[0]} for {self.hostname}.local")
                        
                        # Send response
                        response = self._create_response()
                        
                        # Send to the querier directly AND to multicast
                        self.sock.sendto(response, addr)
                        self.sock.sendto(response, (MDNS_ADDR, MDNS_PORT))
                        
                        print(f"mDNS: Responded with {self._get_ip()}")
                        
                except OSError:
                    # No data available (EAGAIN) - this is normal
                    pass
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"mDNS responder error: {e}")
                await asyncio.sleep(1)
    
    def _is_query_for_us(self, data):
        """Check if this mDNS packet is a query for our hostname"""
        try:
            if len(data) < 12:
                return False
            
            # Parse DNS header
            flags = struct.unpack('>H', data[2:4])[0]
            
            # Check if it's a query (QR bit = 0)
            if flags & 0x8000:
                return False  # It's a response, not a query
            
            # Get question count
            qdcount = struct.unpack('>H', data[4:6])[0]
            if qdcount == 0:
                return False
            
            # Parse the query name (starting at offset 12)
            offset = 12
            query_name = self._parse_name(data, offset)
            
            if query_name is None:
                return False
            
            # Check if query matches our hostname.local
            expected = f"{self.hostname}.local"
            
            return query_name.lower() == expected.lower()
            
        except Exception as e:
            return False
    
    def _parse_name(self, data, offset):
        """Parse a DNS name from packet data"""
        try:
            labels = []
            
            while offset < len(data):
                length = data[offset]
                
                if length == 0:
                    # End of name
                    break
                elif length >= 192:
                    # Compression pointer - not handling for simplicity
                    break
                else:
                    offset += 1
                    if offset + length > len(data):
                        return None
                    label = data[offset:offset + length].decode('utf-8')
                    labels.append(label)
                    offset += length
            
            return '.'.join(labels) if labels else None
            
        except Exception:
            return None
    
    def _encode_name(self, name):
        """Encode a DNS name into wire format"""
        result = b''
        for label in name.split('.'):
            encoded = label.encode('utf-8')
            result += bytes([len(encoded)]) + encoded
        result += b'\x00'  # Null terminator
        return result
    
    def _create_response(self):
        """Create mDNS response packet"""
        ip = self._get_ip()
        ip_bytes = bytes(map(int, ip.split('.')))
        
        # DNS Header
        # ID = 0 for mDNS
        # Flags = 0x8400 (response, authoritative)
        # QDCOUNT = 0, ANCOUNT = 1, NSCOUNT = 0, ARCOUNT = 0
        header = struct.pack('>HHHHHH', 0, 0x8400, 0, 1, 0, 0)
        
        # Answer section
        # Name: hostname.local
        name = self._encode_name(f"{self.hostname}.local")
        
        # Type: A (1)
        # Class: IN (1) with cache-flush bit (0x8001)
        # TTL: 120 seconds
        # RDLENGTH: 4 (IPv4 address)
        # RDATA: IP address
        answer = name + struct.pack('>HHIH', DNS_TYPE_A, DNS_CLASS_IN | DNS_CLASS_FLUSH, 120, 4) + ip_bytes
        
        return header + answer
    
    def advertise(self):
        """
        Send unsolicited mDNS announcement
        
        Call this after starting to proactively announce presence.
        """
        if not self.running or not self.sock:
            return False
        
        try:
            response = self._create_response()
            
            # Send announcement to multicast group
            self.sock.sendto(response, (MDNS_ADDR, MDNS_PORT))
            
            print(f"mDNS: Announced {self.hostname}.local → {self._get_ip()}")
            return True
            
        except Exception as e:
            print(f"mDNS advertise error: {e}")
            return False


# Convenience function
def enable_mdns(hostname=None, ip=None):
    """
    Enable mDNS responder
    
    Args:
        hostname (str): Hostname without .local
        ip (str): IP address (auto-detect if None)
        
    Returns:
        MDNS: mDNS instance or None if failed
    """
    mdns = MDNS(hostname, ip)
    
    if mdns.start():
        # Send initial announcement
        mdns.advertise()
        return mdns
    
    return None


# Async convenience function
async def enable_mdns_async(hostname=None, ip=None):
    """
    Enable mDNS responder (async version)
    
    Args:
        hostname (str): Hostname without .local
        ip (str): IP address (auto-detect if None)
        
    Returns:
        MDNS: mDNS instance or None if failed
    """
    return enable_mdns(hostname, ip)


# Test function
async def test_mdns():
    """Test mDNS responder"""
    print("\n" + "=" * 60)
    print("mDNS Responder Test")
    print("=" * 60)
    
    # Get current hostname
    try:
        hostname = network.hostname()
    except:
        hostname = "test-device"
    
    print(f"Hostname: {hostname}")
    
    # Start mDNS
    mdns = MDNS(hostname)
    
    if mdns.start():
        print("✅ mDNS responder running")
        print(f"   Try: http://{hostname}.local")
        
        # Send announcement
        mdns.advertise()
        
        # Run for a while
        print("\nListening for 60 seconds...")
        await asyncio.sleep(60)
        
        mdns.stop()
    else:
        print("❌ Failed to start mDNS")


if __name__ == '__main__':
    asyncio.run(test_mdns())
