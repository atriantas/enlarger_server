"""
mDNS Diagnostic Script for Pico 2 W
Run this to check if mDNS is supported on your MicroPython version
"""

import network
import time
import socket

def test_mdns_support():
    """Test mDNS support on Pico 2 W"""
    
    print("\n" + "=" * 60)
    print("mDNS Diagnostic Test")
    print("=" * 60)
    
    # Test 1: Check if network.hostname() is available
    print("\n1. Testing network.hostname() function...")
    try:
        # Set a test hostname
        test_hostname = "test-mdns-device"
        network.hostname(test_hostname)
        print(f"   ✅ network.hostname() works")
        
        # Get current hostname
        current = network.hostname()
        print(f"   ✅ Current hostname: {current}")
        
    except Exception as e:
        print(f"   ❌ network.hostname() failed: {e}")
        print("   This MicroPython port may not support hostname setting")
        return False
    
    # Test 2: Check if mDNS is broadcasting
    print("\n2. Testing mDNS broadcast...")
    try:
        # Create AP
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        time.sleep(0.5)
        
        # Configure AP with hostname
        ap.config(essid="TestAP", password="test12345", channel=6)
        ap.active(True)
        time.sleep(3)
        
        if ap.active():
            ip = ap.ifconfig()[0]
            print(f"   ✅ AP started on IP: {ip}")
            print(f"   📡 Try accessing: http://{test_hostname}.local")
            print(f"   📡 Or use IP: http://{ip}")
            
            # Try to resolve mDNS
            print("\n3. Testing mDNS resolution...")
            try:
                # Try to resolve the hostname
                resolved_ip = socket.getaddrinfo(f"{test_hostname}.local", 80)
                print(f"   ✅ mDNS resolved to: {resolved_ip[0][4][0]}")
            except Exception as e:
                print(f"   ❌ mDNS resolution failed: {e}")
                print("   mDNS may not be supported on this network or device")
                print("   Use IP address instead: http://" + ip)
        else:
            print("   ❌ Failed to start AP")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check network module capabilities
    print("\n4. Checking network module capabilities...")
    try:
        import network
        print(f"   Network module: {dir(network)}")
        
        # Check for mDNS-related constants
        if hasattr(network, 'AP_IF'):
            print("   ✅ AP_IF constant available")
        if hasattr(network, 'STA_IF'):
            print("   ✅ STA_IF constant available")
            
    except Exception as e:
        print(f"   ❌ Error checking network module: {e}")
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)
    print("\nRECOMMENDATIONS:")
    print("1. If mDNS doesn't work, use IP address directly")
    print("2. Check your smartphone's mDNS support")
    print("3. Some networks block mDNS (try different network)")
    print("4. Update MicroPython if hostname() is not available")
    print("=" * 60)

if __name__ == '__main__':
    test_mdns_support()
