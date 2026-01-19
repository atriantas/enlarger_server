"""
WiFi Station Mode Setup for Pico 2 W
Connects the device to an existing WiFi router as a client
"""

import network
import time
import asyncio


class WiFiSTA:
    """WiFi Station mode manager for Pico 2 W"""
    
    def __init__(self):
        """
        Initialize WiFi Station configuration
        """
        self.sta = None
        self.ip = None
        self.ssid = None
        
    async def connect(self, ssid, password, timeout_s=20):
        """
        Connect to WiFi network in STA mode
        
        Args:
            ssid (str): Network SSID
            password (str): Network password
            timeout_s (int): Connection timeout in seconds (default: 20)
            
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            # Create STA interface
            self.sta = network.WLAN(network.STA_IF)
            
            # Disable any existing STA
            self.sta.active(False)
            await asyncio.sleep(0.5)
            
            # Store SSID for status reporting
            self.ssid = ssid
            
            # Connect to network
            print(f"🔗 Connecting to '{ssid}'...")
            self.sta.active(True)
            self.sta.connect(ssid, password)
            
            # Wait for connection with timeout (non-blocking)
            start_time = time.time()
            last_print = -1
            while not self.sta.isconnected():
                elapsed = time.time() - start_time
                if elapsed > timeout_s:
                    print(f"❌ WiFi connection timeout after {timeout_s}s")
                    self.sta.active(False)
                    return False
                    
                # Show progress every 2 seconds
                if int(elapsed) != last_print and int(elapsed) % 2 == 0:
                    print(f"  Waiting... ({int(elapsed)}s/{timeout_s}s)")
                    last_print = int(elapsed)
                
                # Non-blocking sleep - allows other async tasks to run
                await asyncio.sleep(0.5)
            
            # Connection successful
            self.ip = self.sta.ifconfig()[0]
            print(f"✅ WiFi STA connected")
            print(f"   IP: {self.ip}")
            return True
            
        except Exception as e:
            print(f"❌ STA connection error: {e}")
            return False
            
    def is_connected(self):
        """
        Check if STA is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.sta:
            return self.sta.isconnected()
        return False
        
    def get_ip(self):
        """
        Get the STA IP address
        
        Returns:
            str: IP address, or None if not connected
        """
        if self.sta and self.sta.isconnected():
            return self.sta.ifconfig()[0]
        return None
        
    def status(self):
        """
        Get STA status information
        
        Returns:
            dict: Status information
        """
        if not self.sta:
            return {"connected": False}
            
        status = {
            "connected": self.sta.isconnected(),
            "ssid": self.ssid,
            "ip": None,
        }
        
        if self.sta.isconnected():
            try:
                ifconfig = self.sta.ifconfig()
                status.update({
                    "ip": ifconfig[0],
                    "subnet": ifconfig[1],
                    "gateway": ifconfig[2],
                    "dns": ifconfig[3]
                })
            except Exception:
                pass
                
        return status
        
    def disconnect(self):
        """Disconnect from WiFi network"""
        if self.sta:
            self.sta.active(False)
            print("WiFi STA disconnected")
            
    def print_info(self):
        """Print STA information to console"""
        if not self.sta or not self.sta.isconnected():
            print("❌ WiFi STA is not connected")
            return
            
        ip = self.get_ip()
        print("\n" + "=" * 60)
        print("✅ WiFi Station Connected")
        print("=" * 60)
        print(f"📡 SSID:     {self.ssid}")
        print(f"📍 IP:       {ip}")
        print("=" * 60)
        print(f"🌐 Access browser at: http://{ip}/")
        print("=" * 60)
        print()
