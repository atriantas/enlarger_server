"""
Darkroom Timer System for Raspberry Pi Pico 2 W
MicroPython bootloader with WiFi AP and HTTP server
"""

import asyncio
import sys

# Add lib directory to path
sys.path.insert(0, '/lib')

from wifi_ap import WiFiAP
from wifi_sta import WiFiSTA
from http_server import HTTPServer
from gpio_control import GPIOController
from timer_manager import TimerManager


async def main():
    """
    Main entry point for darkroom timer system
    Initializes WiFi AP, GPIO, and HTTP server
    """
    
    print("\n" + "=" * 60)
    print("DARKROOM TIMER - Raspberry Pi Pico 2 W")
    print("=" * 60)
    
    # Configuration
    WIFI_SSID = "DarkroomTimer"
    WIFI_PASSWORD = "darkroom123"
    HTTP_PORT = 80
    AP_GRACE_SECONDS = 30  # Option A: short grace period
    
    try:
        # Step 1: Initialize GPIO
        print("\n📍 Initializing GPIO pins...")
        gpio = GPIOController()
        if not gpio.initialize():
            print("❌ Failed to initialize GPIO")
            return False
            
        # Step 2: Initialize WiFi managers
        print("\n📡 Initializing WiFi...")
        wifi_ap = WiFiAP(ssid=WIFI_SSID, password=WIFI_PASSWORD)
        wifi_sta = WiFiSTA()

        # Attempt STA first using saved credentials (Option A)
        sta_connected = False
        saved_ssid = None
        saved_password = None
        try:
            with open('wifi_config.json', 'r') as f:
                saved = __import__('json').loads(f.read())
                saved_ssid = saved.get('ssid')
                saved_password = saved.get('password')
        except Exception:
            pass

        if saved_ssid and (saved_password is not None):
            print(f"🔗 Attempting STA connect to '{saved_ssid}'...")
            try:
                sta_connected = await wifi_sta.connect(saved_ssid, saved_password, timeout_s=20)
            except Exception as e:
                print(f"STA connect error: {e}")

        if sta_connected:
            # Start AP for a short grace period, then stop
            print("✅ STA connected. Starting AP for grace period...")
            wifi_ap.start()
            wifi_ap.print_info()
            # Schedule AP stop in background
            async def stop_ap_after_grace():
                await asyncio.sleep(AP_GRACE_SECONDS)
                wifi_ap.stop()
                print("AP stopped after grace period.")
            asyncio.create_task(stop_ap_after_grace())
        else:
            # STA not connected: start AP for captive portal
            print("❌ STA not connected. Starting AP for configuration...")
            if not wifi_ap.start():
                print("❌ Failed to start WiFi AP")
                return False
            wifi_ap.print_info()
        
        # Step 3: Initialize timer manager
        print("⏱️  Initializing timer manager...")
        timer = TimerManager(gpio)
        print("✓ Timer manager ready")
        
        # Step 4: Start HTTP server
        print(f"🌐 Starting HTTP server on port {HTTP_PORT}...")
        server = HTTPServer(gpio, timer, port=HTTP_PORT, wifi_ap=wifi_ap, wifi_sta=wifi_sta, ap_grace_s=AP_GRACE_SECONDS)
        server_task = asyncio.create_task(server.start())
        
        print("\n" + "=" * 60)
        print("✅ SYSTEM READY")
        print("=" * 60)
        # Show available access paths
        ap_ip = wifi_ap.get_ip()
        sta_ip = wifi_sta.get_ip()
        if sta_ip:
            print(f"🌐 Router IP: http://{sta_ip}/")
        if ap_ip:
            print(f"📡 AP IP:     http://{ap_ip}/ (grace {AP_GRACE_SECONDS}s)")
        print("=" * 60)
        
        # Run server forever
        try:
            await server_task
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            await server.stop()
            
        # Cleanup
        print("🔧 Cleaning up...")
        await timer.cleanup()
        gpio.cleanup()
        wifi_ap.stop()
        
        print("✓ Shutdown complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        # Run main async function
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
