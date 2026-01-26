"""
WiFi Access Point Module for Raspberry Pi Pico 2 W
Creates a hotspot for direct device connection
MicroPython v1.27.0 compatible
"""

import network
import time

# Default AP Configuration
DEFAULT_SSID = "DarkroomTimer"
DEFAULT_PASSWORD = "darkroom123"
DEFAULT_CHANNEL = 6

# AP IP Configuration
AP_IP = "192.168.4.1"
AP_SUBNET = "255.255.255.0"
AP_GATEWAY = "192.168.4.1"
AP_DNS = "192.168.4.1"

# mDNS hostname (will be accessible as darkroom.local)
MDNS_HOSTNAME = "darkroom"


class WiFiAP:
    """
    WiFi Access Point manager for Pico 2 W.
    
    Creates a hotspot that clients can connect to directly.
    """
    
    def __init__(self, ssid=DEFAULT_SSID, password=DEFAULT_PASSWORD, channel=DEFAULT_CHANNEL):
        """
        Initialize WiFi AP.
        
        Args:
            ssid (str): Network name
            password (str): Network password (min 8 characters)
            channel (int): WiFi channel (1-11)
        
        Note: mDNS hostname must be set BEFORE instantiating this class.
        """
        self.ssid = ssid
        self.password = password
        self.channel = channel
        self.ap = None
    
    def start(self):
        """
        Start the access point.
        
        Returns:
            str: IP address of the AP, or None if failed
        """
        try:
            # Create AP interface
            self.ap = network.WLAN(network.AP_IF)
            
            # Configure AP
            self.ap.config(
                essid=self.ssid,
                password=self.password,
                channel=self.channel
            )
            
            # Set static IP configuration
            self.ap.ifconfig((AP_IP, AP_SUBNET, AP_GATEWAY, AP_DNS))
            
            # Activate AP
            self.ap.active(True)
            
            # Wait for AP to be active
            timeout = 10
            while not self.ap.active() and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
            
            if self.ap.active():
                ip = self.ap.ifconfig()[0]
                print(f"AP started: SSID={self.ssid}, IP={ip}")
                return ip
            else:
                print("Failed to start AP")
                return None
                
        except Exception as e:
            print(f"AP start error: {e}")
            return None
    
    def stop(self):
        """Stop the access point."""
        if self.ap:
            try:
                self.ap.active(False)
                print("AP stopped")
            except Exception as e:
                print(f"AP stop error: {e}")
    
    def is_active(self):
        """Check if AP is active."""
        if self.ap:
            return self.ap.active()
        return False
    
    def get_ip(self):
        """Get AP IP address."""
        if self.ap and self.ap.active():
            return self.ap.ifconfig()[0]
        return None
    
    def get_config(self):
        """Get AP configuration."""
        return {
            "ssid": self.ssid,
            "ip": self.get_ip(),
            "active": self.is_active(),
            "channel": self.channel
        }
    
    def get_connected_clients(self):
        """
        Get number of connected clients.
        Note: MicroPython may not support this on all builds.
        
        Returns:
            int: Number of connected clients, or -1 if not supported
        """
        if self.ap and hasattr(self.ap, 'status'):
            try:
                # This may vary by MicroPython version
                return self.ap.status('stations')
            except:
                pass
        return -1

