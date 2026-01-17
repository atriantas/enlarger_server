import network
import socket
import time
import os
from machine import Pin

# WiFi Hotspot Configuration
AP_SSID = "PicoHotspot"
AP_PASSWORD = "password123"

def setup_ap():
    """Setup WiFi Access Point"""
    print("Setting up WiFi Access Point...")
    
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    time.sleep(0.5)
    
    # Configure AP
    try:
        ap.config(essid=AP_SSID, password=AP_PASSWORD)
    except:
        try:
            ap.config(essid=AP_SSID)
            ap.config(password=AP_PASSWORD)
        except:
            pass
    
    ap.active(True)
    time.sleep(3)
    
    if ap.active():
        print(f"✅ Access Point '{AP_SSID}' is active!")
        print(f"📱 Connect your phone to: {AP_SSID}")
        print(f"🔑 Password: {AP_PASSWORD}")
        print(f"🌐 IP Address: {ap.ifconfig()[0]}")
        return ap
    else:
        print("❌ Failed to start Access Point")
        return None

def send_file_chunked(conn, filename, chunk_size=512):
    """Stream file directly from flash storage in chunks"""
    try:
        # Check if file exists
        if filename not in os.listdir():
            print(f"❌ File {filename} not found")
            return False
        
        # Get file size
        file_size = os.stat(filename)[6]
        print(f"📦 Streaming {filename} ({file_size} bytes)")
        
        # Send HTTP headers first
        headers = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {file_size}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        conn.send(headers)
        
        # Stream file in chunks
        with open(filename, 'rb') as f:
            bytes_sent = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                conn.send(chunk)
                bytes_sent += len(chunk)
                time.sleep_ms(5)  # Small delay to prevent overwhelming connection
        
        print(f"✅ Successfully sent {bytes_sent} bytes")
        return True
        
    except Exception as e:
        print(f"❌ File streaming error: {e}")
        return False

def handle_led_control(path):
    """Handle LED control requests"""
    action = path.split('/')[-1]
    led = Pin("LED", Pin.OUT)
    
    if action == 'on':
        led.value(1)
        return "LED turned ON"
    elif action == 'off':
        led.value(0)
        return "LED turned OFF"
    elif action == 'toggle':
        led.toggle()
        return f"LED toggled to {'ON' if led.value() else 'OFF'}"
    else:
        return "Unknown action"

def handle_request(request, conn):
    """Handle HTTP requests"""
    try:
        # Parse request
        request_line = request.split('\r\n')[0]
        parts = request_line.split()
        
        if len(parts) < 2:
            conn.send("HTTP/1.1 400 Bad Request\r\n\r\nBad Request")
            return
        
        method = parts[0]
        path = parts[1]
        
        print(f"Request: {method} {path}")
        
        # LED control
        if path.startswith('/led/'):
            response_text = handle_led_control(path)
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{response_text}"
            conn.send(response)
        
        # Serve HTML file
        elif path == '/' or path == '/index.html':
            if not send_file_chunked(conn, 'index.html'):
                # Fallback: send minimal HTML if file not found
                fallback_html = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Pico 2 W Server</h1><p>HTML file not found on flash storage!</p><p>Please save 'index.html' to the Pico using the setup script.</p><button onclick="fetch('/led/toggle')">Toggle LED</button></body></html>"""
                conn.send(fallback_html)
        
        # 404 for other paths
        else:
            conn.send("HTTP/1.1 404 Not Found\r\n\r\nNot Found")
            
    except Exception as e:
        print(f"Error handling request: {e}")
        try:
            conn.send("HTTP/1.1 500 Internal Server Error\r\n\r\nServer Error")
        except:
            pass

def start_server():
    """Start the HTTP server"""
    print("\nStarting HTTP Server...")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(5)
    
    print("✅ HTTP Server started on port 80")
    print("🌐 Access from phone browser at http://192.168.4.1")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        while True:
            try:
                conn, addr = s.accept()
                print(f"\nConnection from: {addr}")
                conn.settimeout(5.0)
                
                try:
                    request = conn.recv(1024).decode('utf-8')
                    if request:
                        handle_request(request, conn)
                except Exception as e:
                    print(f"Request error: {e}")
                finally:
                    conn.close()
                    
            except OSError as e:
                if e.errno != 11:  # Not "resource temporarily unavailable"
                    raise
                    
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    finally:
        s.close()
        print("Socket closed")

def main():
    """Main function"""
    print("=" * 60)
    print("Raspberry Pi Pico 2 W - File Streaming Server")
    print("=" * 60)
    
    # LED feedback
    try:
        led = Pin("LED", Pin.OUT)
        led.value(1)
        time.sleep(1)
        led.value(0)
    except:
        pass
    
    # Check for HTML file
    try:
        files = os.listdir()
        print(f"📁 Files in flash storage: {files}")
        
        if 'index.html' in files:
            file_size = os.stat('index.html')[6]
            print(f"✅ Found index.html ({file_size} bytes)")
        else:
            print("⚠️ index.html not found!")
            print("   Run 'create_html_file.py' to generate it")
    except Exception as e:
        print(f"⚠️ Could not check files: {e}")
    
    # Setup AP
    ap = setup_ap()
    
    if ap:
        start_server()
    else:
        print("❌ Failed to start Access Point")

if __name__ == "__main__":
    main()
