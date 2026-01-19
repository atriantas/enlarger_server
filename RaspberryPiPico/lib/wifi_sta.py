"""
WiFi Station Module for Raspberry Pi Pico 2 W
Connects to existing WiFi router
Saves/loads credentials from wifi_config.json
MicroPython v1.27.0 compatible
"""

import network
import time
import json

# Configuration file path
CONFIG_FILE = "wifi_config.json"

# Connection timeout (seconds)
CONNECT_TIMEOUT = 15

# mDNS hostname (will be accessible as darkroom.local)
MDNS_HOSTNAME = "darkroom"


class WiFiSTA:
    """
    WiFi Station manager for Pico 2 W.
    
    Connects to existing WiFi networks and manages credentials.
    """
    
    def __init__(self):
        """
        Initialize WiFi station interface.
        
        Note: mDNS hostname must be set BEFORE instantiating this class.
        """
        self.sta = network.WLAN(network.STA_IF)
        self.ssid = None
        self.password = None
        self._load_config()
    
    def _load_config(self):
        """Load saved WiFi credentials from file."""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.ssid = config.get('ssid')
                self.password = config.get('password')
                print(f"Loaded WiFi config: SSID={self.ssid}")
        except OSError:
            print("No saved WiFi config found")
        except Exception as e:
            print(f"Error loading WiFi config: {e}")
    
    def _save_config(self):
        """Save WiFi credentials to file."""
        try:
            config = {
                'ssid': self.ssid,
                'password': self.password
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            print(f"Saved WiFi config: SSID={self.ssid}")
            return True
        except Exception as e:
            print(f"Error saving WiFi config: {e}")
            return False
    
    def has_saved_credentials(self):
        """Check if credentials are saved."""
        return self.ssid is not None and self.password is not None
    
    async def connect_async(self, ssid=None, password=None, save=True):
        """
        Connect to WiFi network asynchronously.
        
        Args:
            ssid (str): Network name (uses saved if None)
            password (str): Network password (uses saved if None)
            save (bool): Save credentials on successful connection
            
        Returns:
            str: IP address if connected, None if failed
        """
        import asyncio
        
        # Use provided or saved credentials
        ssid = ssid or self.ssid
        password = password or self.password
        
        if not ssid or not password:
            print("No WiFi credentials available")
            return None
        
        try:
            # Activate station interface
            self.sta.active(True)
            
            # Disconnect if already connected
            if self.sta.isconnected():
                self.sta.disconnect()
                await asyncio.sleep(0.5)
            
            print(f"Connecting to WiFi: {ssid}")
            self.sta.connect(ssid, password)
            
            # Wait for connection with timeout
            timeout = CONNECT_TIMEOUT
            while not self.sta.isconnected() and timeout > 0:
                await asyncio.sleep(0.5)
                timeout -= 0.5
                # Check for connection failure
                status = self.sta.status()
                if status == network.STAT_WRONG_PASSWORD:
                    print("WiFi: Wrong password")
                    return None
                elif status == network.STAT_NO_AP_FOUND:
                    print("WiFi: Network not found")
                    return None
                elif status == network.STAT_CONNECT_FAIL:
                    print("WiFi: Connection failed")
                    return None
            
            if self.sta.isconnected():
                ip = self.sta.ifconfig()[0]
                print(f"WiFi connected: IP={ip}")
                
                # Save credentials on success
                if save:
                    self.ssid = ssid
                    self.password = password
                    self._save_config()
                
                return ip
            else:
                print("WiFi connection timeout")
                return None
                
        except Exception as e:
            print(f"WiFi connect error: {e}")
            return None
    
    def connect(self, ssid=None, password=None, save=True):
        """
        Connect to WiFi network synchronously.
        
        Args:
            ssid (str): Network name (uses saved if None)
            password (str): Network password (uses saved if None)
            save (bool): Save credentials on successful connection
            
        Returns:
            str: IP address if connected, None if failed
        """
        # Use provided or saved credentials
        ssid = ssid or self.ssid
        password = password or self.password
        
        if not ssid or not password:
            print("No WiFi credentials available")
            return None
        
        try:
            # Activate station interface
            self.sta.active(True)
            
            # Disconnect if already connected
            if self.sta.isconnected():
                self.sta.disconnect()
                time.sleep(0.5)
            
            print(f"Connecting to WiFi: {ssid}")
            self.sta.connect(ssid, password)
            
            # Wait for connection with timeout
            timeout = CONNECT_TIMEOUT
            while not self.sta.isconnected() and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
                # Check for connection failure
                status = self.sta.status()
                if status == network.STAT_WRONG_PASSWORD:
                    print("WiFi: Wrong password")
                    return None
                elif status == network.STAT_NO_AP_FOUND:
                    print("WiFi: Network not found")
                    return None
                elif status == network.STAT_CONNECT_FAIL:
                    print("WiFi: Connection failed")
                    return None
            
            if self.sta.isconnected():
                ip = self.sta.ifconfig()[0]
                print(f"WiFi connected: IP={ip}")
                
                # Save credentials on success
                if save:
                    self.ssid = ssid
                    self.password = password
                    self._save_config()
                
                return ip
            else:
                print("WiFi connection timeout")
                return None
                
        except Exception as e:
            print(f"WiFi connect error: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from WiFi network."""
        if self.sta:
            try:
                self.sta.disconnect()
                self.sta.active(False)
                print("WiFi disconnected")
            except Exception as e:
                print(f"WiFi disconnect error: {e}")
    
    def is_connected(self):
        """Check if connected to WiFi."""
        if self.sta:
            return self.sta.isconnected()
        return False
    
    def get_ip(self):
        """Get station IP address."""
        if self.sta and self.sta.isconnected():
            return self.sta.ifconfig()[0]
        return None
    
    def get_status(self):
        """
        Get connection status.
        
        Returns:
            dict: Connection status info
        """
        connected = self.is_connected()
        return {
            "connected": connected,
            "ssid": self.ssid if connected else None,
            "ip": self.get_ip(),
            "saved_ssid": self.ssid,
            "has_saved_credentials": self.has_saved_credentials()
        }
    
    def clear_credentials(self):
        """Clear saved WiFi credentials."""
        self.ssid = None
        self.password = None
        try:
            import os
            os.remove(CONFIG_FILE)
            print("WiFi credentials cleared")
        except:
            pass
    
    def get_rssi(self):
        """
        Get WiFi signal strength.
        
        Returns:
            int: RSSI value in dBm, or None if not connected
        """
        if self.sta and self.sta.isconnected():
            try:
                return self.sta.status('rssi')
            except:
                pass
        return None
