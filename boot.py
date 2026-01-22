"""
Darkroom Timer - Main Boot Script for Raspberry Pi Pico 2 W
MicroPython v1.27.0

Boot sequence:
1. Initialize GPIO (relays OFF)
2. Try saved WiFi credentials (STA mode)
3. If STA succeeds: wait 5 seconds, disable AP
4. If STA fails: run in AP-only mode
5. Start HTTP server on port 80

mDNS is handled natively by MicroPython v1.27.0 via network.hostname()
Set before WiFi activation - accessible at darkroom.local
"""

import asyncio
import gc
import time

# Import modules from lib folder
from lib.gpio_control import GPIOControl
from lib.timer_manager import TimerManager
from lib.temperature_sensor import TemperatureSensor
from lib.light_sensor import LightSensor
from lib.light_meter_manager import LightMeterManager
from lib.wifi_ap import WiFiAP
from lib.wifi_sta import WiFiSTA
from lib.http_server import HTTPServer

# Configuration
AP_GRACE_PERIOD = 5  # Seconds to wait before disabling AP after STA connects


class DarkroomTimer:
    """
    Main application class for Darkroom Timer.
    
    Manages WiFi, GPIO, and HTTP server lifecycle.
    """
    
    def __init__(self):
        """Initialize all components."""
        print("=" * 50)
        print("Darkroom Timer v1.0 - Pico 2 W")
        print("=" * 50)
        
        # Initialize GPIO first (safety)
        print("\nInitializing GPIO...")
        self.gpio = GPIOControl()
        
        # Initialize temperature sensor
        print("\nInitializing temperature sensor...")
        self.temperature = TemperatureSensor(pin_num=18)
        
        # Initialize light sensor (TSL2591X on I2C0: GP0=SDA, GP1=SCL)
        print("\nInitializing light sensor...")
        self.light_sensor = LightSensor(sda_pin=0, scl_pin=1)
        
        # Initialize light meter manager
        print("\nInitializing light meter manager...")
        self.light_meter = LightMeterManager(self.light_sensor)
        
        # Initialize timer manager with temperature sensor
        print("\nInitializing timer manager...")
        self.timer = TimerManager(self.gpio, self.temperature)
        
        # Set mDNS hostname BEFORE any WiFi initialization
        # This MUST be done before creating WLAN interfaces
        import network
        network.hostname("darkroom")
        print("\nSet mDNS hostname: darkroom.local")
        
        # Initialize WiFi modules
        print("\nInitializing WiFi...")
        self.wifi_ap = WiFiAP()
        self.wifi_sta = WiFiSTA()
        
        # HTTP server (initialized later)
        self.http = None
        
        # State tracking
        self.sta_connected = False
        self.current_ip = None
    
    async def setup_wifi(self):
        """
        Setup WiFi with fallback logic.
        
        1. Start AP immediately (for initial access)
        2. Try saved STA credentials
        3. If STA connects, wait grace period then disable AP
        4. If STA fails, keep AP running
        """
        # Always start AP first for immediate access
        print("\nStarting WiFi Access Point...")
        ap_ip = self.wifi_ap.start()
        
        if ap_ip:
            print(f"AP active: SSID=DarkroomTimer, IP={ap_ip}")
            self.current_ip = ap_ip
        
        # Try saved WiFi credentials
        if self.wifi_sta.has_saved_credentials():
            print(f"\nTrying saved WiFi: {self.wifi_sta.ssid}")
            sta_ip = await self.wifi_sta.connect_async()
            
            if sta_ip:
                self.sta_connected = True
                self.current_ip = sta_ip
                print(f"STA connected: IP={sta_ip}")
                
                # Wait grace period before disabling AP
                print(f"\nAP will disable in {AP_GRACE_PERIOD} seconds...")
                print("Connect to router network now if needed.")
                await asyncio.sleep(AP_GRACE_PERIOD)
                
                # Disable AP to save memory
                print("Disabling AP to save memory...")
                self.wifi_ap.stop()
                
                return sta_ip
            else:
                print("STA connection failed, keeping AP active")
        else:
            print("\nNo saved WiFi credentials")
            print("Configure WiFi via the web interface")
        
        return ap_ip
    
    async def setup_http(self):
        """Setup HTTP server."""
        print("\nStarting HTTP server...")
        self.http = HTTPServer(
            self.gpio,
            self.timer,
            self.wifi_ap,
            self.wifi_sta,
            self.light_meter
        )
        self.http.start()
    
    async def run(self):
        """Main application loop."""
        try:
            # Setup WiFi
            ip = await self.setup_wifi()
            
            if not ip:
                print("\nERROR: No network connection!")
                print("Please check WiFi configuration")
                return
            
            # Setup HTTP server
            await self.setup_http()
            
            # Print access info
            print("\n" + "=" * 50)
            print("SYSTEM READY")
            print("=" * 50)
            
            if self.sta_connected:
                print(f"  Router mode: http://{self.current_ip}/")
            else:
                print(f"  Hotspot mode: http://192.168.4.1/")
                print(f"  WiFi: SSID=DarkroomTimer, Password=darkroom123")
            
            print(f"  mDNS: http://darkroom.local/")
            print("=" * 50)
            
            # Create async tasks
            tasks = [
                asyncio.create_task(self.http.run_async()),
                asyncio.create_task(self.timer.start_heating_control())
            ]
            
            # Run forever
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"\nFatal error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup all resources."""
        print("\nCleaning up...")
        
        # Stop timers
        if self.timer:
            self.timer.stop_all_timers()
        
        # Stop HTTP server
        if self.http:
            self.http.stop()
        
        # Stop WiFi
        if self.wifi_sta:
            self.wifi_sta.disconnect()
        if self.wifi_ap:
            self.wifi_ap.stop()
        
        # Cleanup GPIO (turn off all relays)
        if self.gpio:
            self.gpio.cleanup()
        
        print("Cleanup complete")


def main():
    """Main entry point."""
    app = DarkroomTimer()
    
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure cleanup happens
        app.cleanup()


# Run when imported as main
if __name__ == "__main__":
    main()
