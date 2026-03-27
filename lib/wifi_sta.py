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
    
    # ── Shared connection helpers ─────────────────────────────────────
    
    def _prepare_connection(self, ssid, password):
        """Resolve credentials, activate interface, disable power-saving.
        
        Returns:
            tuple: (ssid, password) on success, (None, None) if no credentials.
        """
        ssid = ssid or self.ssid
        password = password or self.password
        if not ssid or not password:
            print("No WiFi credentials available")
            return None, None
        self.sta.active(True)
        # Disable power saving mode (can cause connectivity issues)
        try:
            self.sta.config(pm=0xa11140)
        except:
            pass  # Older firmware may not support this
        return ssid, password
    
    def _check_connection_status(self):
        """Return an error string if WLAN reports a terminal failure, else None."""
        status = self.sta.status()
        if status == network.STAT_WRONG_PASSWORD:
            return "WiFi: Wrong password"
        if status == network.STAT_NO_AP_FOUND:
            return "WiFi: Network not found"
        if status == network.STAT_CONNECT_FAIL:
            return "WiFi: Connection failed"
        return None
    
    def _handle_connected(self, ssid, password, save):
        """Log connection info and optionally save credentials.
        
        Returns:
            str: IP address.
        """
        ifcfg = self.sta.ifconfig()
        ip = ifcfg[0]
        gateway = ifcfg[2]
        dns = ifcfg[3]
        try:
            mac_bytes = self.sta.config('mac')
            mac = ':'.join(['%02X' % b for b in mac_bytes])
            print(f"WiFi connected: IP={ip}")
            print(f"  Gateway: {gateway}, DNS: {dns}")
            print(f"  MAC: {mac}")
        except:
            print(f"WiFi connected: IP={ip}")
            print(f"  Gateway: {gateway}, DNS: {dns}")
        if save:
            self.ssid = ssid
            self.password = password
            self._save_config()
        return ip
    
    # ── Public connect methods ────────────────────────────────────────
    
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
        ssid, password = self._prepare_connection(ssid, password)
        if not ssid:
            return None
        try:
            if self.sta.isconnected():
                self.sta.disconnect()
                await asyncio.sleep(0.5)
            print(f"Connecting to WiFi: {ssid}")
            self.sta.connect(ssid, password)
            timeout = CONNECT_TIMEOUT
            while not self.sta.isconnected() and timeout > 0:
                await asyncio.sleep(0.5)
                timeout -= 0.5
                error = self._check_connection_status()
                if error:
                    print(error)
                    return None
            if self.sta.isconnected():
                return self._handle_connected(ssid, password, save)
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
        ssid, password = self._prepare_connection(ssid, password)
        if not ssid:
            return None
        try:
            if self.sta.isconnected():
                self.sta.disconnect()
                time.sleep(0.5)
            print(f"Connecting to WiFi: {ssid}")
            self.sta.connect(ssid, password)
            timeout = CONNECT_TIMEOUT
            while not self.sta.isconnected() and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
                error = self._check_connection_status()
                if error:
                    print(error)
                    return None
            if self.sta.isconnected():
                return self._handle_connected(ssid, password, save)
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

