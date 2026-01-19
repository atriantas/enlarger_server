"""
WiFi Access Point Setup for Pico 2 W
Configures the device as a WiFi hotspot for darkroom timer clients
"""

import network
import time


class WiFiAP:
    """WiFi Access Point manager for Pico 2 W"""
    
    def __init__(self, ssid="DarkroomTimer", password="darkroom123", channel=6, hostname="darkroom-timer"):
        """
        Initialize WiFi AP configuration
        
        Args:
            ssid (str): Network SSID (default: "DarkroomTimer")
            password (str): Network password (default: "darkroom123")
            channel (int): WiFi channel 1-11 (default: 6)
            hostname (str): Device hostname for mDNS/DHCP (default: "darkroom-timer")
        """
        self.ssid = ssid
        self.password = password
        self.channel = channel
        self.hostname = hostname
        self.ap = None
        self.ip = None
        self.mdns = None  # mDNS responder instance
        
    def start(self):
        """
        Start WiFi Access Point
        
        Returns:
            bool: True if AP started successfully, False otherwise
        """
        try:
            # Set hostname BEFORE activating WiFi (required for mDNS/DHCP)
            print(f"Setting hostname to: {self.hostname}")
            network.hostname(self.hostname)
            
            # Verify hostname was set
            try:
                current_hostname = network.hostname()
                print(f"Hostname verified: {current_hostname}")
            except Exception as e:
                print(f"Warning: Could not verify hostname: {e}")
            
            # Create AP interface
            self.ap = network.WLAN(network.AP_IF)
            
            # Disable any existing AP
            self.ap.active(False)
            time.sleep(0.5)
            
            # Configure AP
            self.ap.config(essid=self.ssid, password=self.password, channel=self.channel)
            
            # Enable AP
            self.ap.active(True)
            time.sleep(3)  # Wait for AP to stabilize
            
            # Get IP address
            if self.ap.active():
                self.ip = self.ap.ifconfig()[0]
                
                # Start mDNS responder for .local hostname resolution
                self._start_mdns()
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error starting WiFi AP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _start_mdns(self):
        """Start mDNS responder if available"""
        try:
            # Run garbage collection to free memory before starting mDNS
            import gc
            print("🧹 Running garbage collection before mDNS...")
            gc.collect()
            
            # Try to import and use umdns library
            print("📦 Attempting to import umdns library...")
            import umdns
            print("✅ umdns library found, starting mDNS responder...")
            
            # Create mDNS responder with our hostname and IP
            print(f"🔧 Creating MDNS object for {self.hostname} on {self.ip}...")
            self.mdns = umdns.MDNS(self.hostname, self.ip)
            
            # Start mDNS responder (runs as async task)
            print("🚀 Starting mDNS responder...")
            if self.mdns.start():
                print(f"✅ mDNS responder started: {self.hostname}.local → {self.ip}")
                
                # Send initial announcement
                self.mdns.advertise()
                print("   Sent mDNS announcement")
            else:
                print("⚠️  mDNS responder failed to start (check console above for errors)")
                print("   Use IP address instead: http://" + self.ip)
                self.mdns = None
                
        except ImportError as e:
            print(f"⚠️  umdns library not available: {e}")
            print("   Copy umdns.py to Pico root, or use IP: http://" + self.ip)
            self.mdns = None
            
        except OSError as e:
            # Handle memory errors (ENOMEM = errno 12)
            if e.args[0] == 12:  # ENOMEM
                print(f"⚠️  mDNS skipped: Not enough memory (ENOMEM)")
            else:
                print(f"⚠️  mDNS OSError: {e}")
            print(f"   Use IP address instead: http://{self.ip}")
            self.mdns = None
            
        except Exception as e:
            print(f"⚠️  mDNS exception: {type(e).__name__}: {e}")
            print(f"   Use IP address instead: http://{self.ip}")
            self.mdns = None
    
    def get_ip(self):
        """
        Get the AP IP address
        
        Returns:
            str: IP address (usually "192.168.4.1"), or None if not active
        """
        if self.ap and self.ap.active():
            return self.ap.ifconfig()[0]
        return None
        
    def get_status(self):
        """
        Get AP status information
        
        Returns:
            dict: Status information
        """
        if not self.ap:
            return {"active": False}
            
        status = {
            "active": self.ap.active(),
            "ssid": self.ssid,
            "channel": self.channel,
            "hostname": self.hostname,
            "ip": self.ip if self.ap.active() else None,
        }
        
        if self.ap.active():
            # Get additional info
            ifconfig = self.ap.ifconfig()
            status.update({
                "ip": ifconfig[0],
                "subnet": ifconfig[1],
                "gateway": ifconfig[2],
                "dns": ifconfig[3]
            })
            
        return status
        
    def print_info(self):
        """Print AP information to console"""
        if not self.ap or not self.ap.active():
            print("❌ WiFi AP is not active")
            return
            
        print("\n" + "=" * 60)
        print("✅ WiFi Access Point Started")
        print("=" * 60)
        print(f"📡 SSID:     {self.ssid}")
        print(f"🔑 Password: {self.password}")
        print(f"🏷️  Hostname: {self.hostname}")
        print(f"📍 IP:       {self.ip}")
        print("=" * 60)
        print(f"🌐 Connect to '{self.ssid}' from your phone")
        print(f"🔗 Open browser to: http://{self.ip}")
        
        # Show mDNS status
        if self.mdns:
            print(f"🔗 Or use mDNS: http://{self.hostname}.local")
            print("   (mDNS responder is running)")
        else:
            print("⚠️  mDNS not available - use IP address")
            print("   (Copy umdns.py to Pico root)")
        
        print("=" * 60)
        print()
        
    def stop(self):
        """Stop WiFi Access Point"""
        if self.ap:
            self.ap.active(False)
            print("WiFi AP stopped")
        
        # Stop mDNS responder
        if self.mdns:
            self.mdns.stop()
            self.mdns = None
