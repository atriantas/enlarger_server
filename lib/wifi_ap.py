"""
WiFi Access Point Setup for Pico 2 W
Configures the device as a WiFi hotspot for darkroom timer clients
"""

import network
import time


class WiFiAP:
    """WiFi Access Point manager for Pico 2 W"""
    
    def __init__(self, ssid="DarkroomTimer", password="darkroom123", channel=6):
        """
        Initialize WiFi AP configuration
        
        Args:
            ssid (str): Network SSID (default: "DarkroomTimer")
            password (str): Network password (default: "darkroom123")
            channel (int): WiFi channel 1-11 (default: 6)
        """
        self.ssid = ssid
        self.password = password
        self.channel = channel
        self.ap = None
        self.ip = None
        
    def start(self):
        """
        Start WiFi Access Point
        
        Returns:
            bool: True if AP started successfully, False otherwise
        """
        try:
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
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error starting WiFi AP: {e}")
            return False
            
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
        print(f"📍 IP:       {self.ip}")
        print("=" * 60)
        print(f"🌐 Connect to '{self.ssid}' from your phone")
        print(f"🔗 Open browser to: http://{self.ip}")
        print("=" * 60)
        print()
        
    def stop(self):
        """Stop WiFi Access Point"""
        if self.ap:
            self.ap.active(False)
            print("WiFi AP stopped")
