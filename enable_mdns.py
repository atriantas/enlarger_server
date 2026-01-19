"""
mDNS Enable Script for MicroPython v1.27.0 on Pico 2 W

This script enables mDNS support for network discovery.
"""

import network
import time
import socket

def enable_mdns_on_ap(ssid="DarkroomTimer", hostname="darkroom-timer"):
    """
    Enable mDNS on Access Point mode for MicroPython v1.27.0
    
    Args:
        ssid: WiFi SSID for the AP
        hostname: Device hostname for mDNS
    """
    
    print("\n" + "=" * 60)
    print("mDNS Enable Script for MicroPython v1.27.0")
    print("=" * 60)
    
    # Step 1: Set hostname (required for mDNS)
    print(f"\n1. Setting hostname to: {hostname}")
    try:
        network.hostname(hostname)
        print(f"   ✅ Hostname set: {network.hostname()}")
    except Exception as e:
        print(f"   ❌ Failed to set hostname: {e}")
        return False
    
    # Step 2: Create and configure AP
    print(f"\n2. Creating Access Point: {ssid}")
    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        time.sleep(0.5)
        
        # Configure AP
        ap.config(essid=ssid, password="darkroom123", channel=6)
        
        # Activate AP
        ap.active(True)
        time.sleep(3)
        
        if ap.active():
            ip = ap.ifconfig()[0]
            print(f"   ✅ AP started on IP: {ip}")
        else:
            print("   ❌ Failed to start AP")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creating AP: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Try to enable mDNS service (if available)
    print("\n3. Attempting to enable mDNS service...")
    try:
        # Try to import and use mDNS module (if available in v1.27.0)
        import mdns
        print("   ✅ mdns module found!")
        
        # Create mDNS service
        mdns_service = mdns.Server()
        mdns_service.hostname = hostname
        mdns_service.start()
        print(f"   ✅ mDNS service started: {hostname}.local")
        
    except ImportError:
        print("   ⚠️  mdns module not available in standard build")
        print("   This is normal - mDNS may need custom firmware")
        
    except Exception as e:
        print(f"   ⚠️  mDNS service error: {e}")
        print("   Continuing without mDNS service...")
    
    # Step 4: Test mDNS resolution
    print("\n4. Testing mDNS resolution...")
    try:
        # Try to resolve the hostname
        resolved = socket.getaddrinfo(f"{hostname}.local", 80)
        print(f"   ✅ mDNS resolved to: {resolved[0][4][0]}")
        print("   mDNS is working!")
        
    except Exception as e:
        print(f"   ❌ mDNS resolution failed: {e}")
        print("   mDNS may not be enabled or supported")
        print("   Use IP address instead: http://" + ip)
    
    # Step 5: Show connection info
    print("\n" + "=" * 60)
    print("Connection Information")
    print("=" * 60)
    print(f"📡 SSID:     {ssid}")
    print(f"🔑 Password: darkroom123")
    print(f"🏷️  Hostname: {hostname}")
    print(f"📍 IP:       {ip}")
    print("=" * 60)
    print(f"🌐 Connect to '{ssid}' from your phone")
    print(f"🔗 Open browser to: http://{ip}")
    print(f"🔗 Try mDNS: http://{hostname}.local")
    print("=" * 60)
    
    return True

def test_mdns_support():
    """Test if mDNS is supported on current MicroPython build"""
    
    print("\n" + "=" * 60)
    print("mDNS Support Test")
    print("=" * 60)
    
    # Test 1: Check for mdns module
    print("\n1. Checking for mdns module...")
    try:
        import mdns
        print("   ✅ mdns module available")
        print(f"   Available functions: {dir(mdns)}")
    except ImportError:
        print("   ❌ mdns module not available")
        print("   This is common - mDNS may need custom firmware")
    
    # Test 2: Check network.hostname()
    print("\n2. Testing network.hostname()...")
    try:
        test_hostname = "test-device"
        network.hostname(test_hostname)
        current = network.hostname()
        print(f"   ✅ network.hostname() works: {current}")
    except Exception as e:
        print(f"   ❌ network.hostname() failed: {e}")
    
    # Test 3: Check socket.getaddrinfo for .local
    print("\n3. Testing socket.getaddrinfo for .local...")
    try:
        # This will fail if mDNS is not working
        resolved = socket.getaddrinfo("test.local", 80)
        print(f"   ✅ mDNS resolution works: {resolved[0][4][0]}")
    except Exception as e:
        print(f"   ❌ mDNS resolution failed: {e}")
        print("   mDNS is not working on this network/build")
    
    # Test 4: Check for mDNS constants
    print("\n4. Checking network module for mDNS support...")
    try:
        import network
        attrs = dir(network)
        mdns_related = [a for a in attrs if 'mdns' in a.lower() or 'multicast' in a.lower()]
        if mdns_related:
            print(f"   ✅ mDNS-related attributes: {mdns_related}")
        else:
            print("   ⚠️  No mDNS-specific attributes found")
    except Exception as e:
        print(f"   ❌ Error checking network module: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print("\nRECOMMENDATIONS:")
    print("1. If mdns module is available, use it for full mDNS support")
    print("2. If not, hostname() still works for DHCP identification")
    print("3. Use IP address for reliable access: http://192.168.4.1")
    print("4. Consider custom MicroPython build with mDNS enabled")
    print("=" * 60)

if __name__ == '__main__':
    # Run test first
    test_mdns_support()
    
    # Then try to enable mDNS on AP
    print("\n\n")
    enable_mdns_on_ap()
