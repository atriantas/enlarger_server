"""
HTTP Server for Pico 2 W Darkroom Timer
Socket-based HTTP server serving darkroom timer API and HTML interface
"""

import socket
import json
import asyncio
import time as utime


class HTTPServer:
    """HTTP server for Pico 2 W darkroom timer"""
    
    CHUNK_SIZE = 512
    MAX_CONNECTIONS = 5
    
    # Relay pin to number mapping for API
    GPIO_TO_RELAY = {
        14: 1,  # Enlarger
        15: 2,  # Safelight
        16: 3,  # Ventilation
        17: 4   # White Light
    }
    
    def __init__(self, gpio_controller, timer_manager, port=80, wifi_ap=None, wifi_sta=None, ap_grace_s: int = 30):
        """
        Initialize HTTP server
        
        Args:
            gpio_controller: GPIOController instance
            timer_manager: TimerManager instance
            port (int): Port to listen on (default: 80)
        """
        self.gpio = gpio_controller
        self.timer = timer_manager
        self.port = port
        self.socket = None
        self.running = False
        # WiFi managers
        self.wifi_ap = wifi_ap
        self.wifi_sta = wifi_sta
        self.ap_grace_s = ap_grace_s
        
    async def start(self):
        """
        Start HTTP server
        
        Listens on all interfaces, accepts connections, and handles requests.
        
        Returns:
            bool: True if server started successfully
        """
        try:
            # Create server socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to bind to specified port
            try:
                self.socket.bind(('0.0.0.0', self.port))
                print(f"✓ HTTP Server bound to port {self.port}")
            except OSError as bind_error:
                print(f"⚠️  Failed to bind to port {self.port}: {bind_error}")
                print(f"   Attempting with port 8080...")
                self.port = 8080
                try:
                    self.socket.bind(('0.0.0.0', self.port))
                    print(f"✓ HTTP Server bound to port {self.port}")
                except OSError as bind_error2:
                    print(f"❌ Failed to bind to port 8080: {bind_error2}")
                    raise
            
            self.socket.listen(self.MAX_CONNECTIONS)
            self.socket.setblocking(False)
            
            print(f"\n✓ HTTP Server listening on port {self.port}")
            self.running = True
            
            # Main server loop
            while self.running:
                try:
                    # Accept connection with timeout
                    conn, addr = self.socket.accept()
                    print(f"📨 New connection from {addr[0]}:{addr[1]}")
                    
                    # Handle connection in background task
                    asyncio.create_task(self._handle_connection(conn, addr))
                    
                except OSError:
                    # No connection waiting (MicroPython raises OSError for non-blocking sockets)
                    pass
                    
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    
                # Yield control to other tasks
                await asyncio.sleep(0.01)
                
        except Exception as e:
            print(f"❌ Server error: {e}")
            # MicroPython doesn't have traceback module
            return False
            
    async def _handle_connection(self, conn, addr):
        """
        Handle a single client connection
        
        Args:
            conn: Socket connection
            addr: Client address tuple
        """
        try:
            # Set timeout - longer timeout for large file transfers (609KB+ HTML file)
            conn.settimeout(30.0)
            
            # Receive request
            request_data = b''
            while True:
                try:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    request_data += chunk
                    
                    # Check if we have complete header
                    if b'\r\n\r\n' in request_data:
                        break
                # MicroPython raises OSError for timeouts; CPython uses socket.timeout
                except OSError:
                    break
                    
            if not request_data:
                conn.close()
                return
            
            # Parse request
            try:
                # MicroPython decode does not support the 'errors' keyword, so fall back safely
                try:
                    request_str = request_data.decode('utf-8')
                except Exception:
                    try:
                        # Latin-1 never fails and preserves byte values
                        request_str = request_data.decode('latin-1')
                    except Exception:
                        request_str = str(request_data)
                lines = request_str.split('\r\n')
                
                if not lines:
                    conn.close()
                    return
                    
                # Parse request line
                parts = lines[0].split()
                if len(parts) < 2:
                    print(f"  ❌ Bad request line: {lines[0]}")
                    self._send_error(conn, 400, "Bad Request")
                    return
                    
                method = parts[0]
                path = parts[1]
                print(f"  📍 {method} {path}")
                
                # Handle OPTIONS for CORS preflight
                if method == 'OPTIONS':
                    self._send_response(conn, 200, "", "text/plain")
                    return
                    
                # Route request
                await self._route_request(conn, method, path)
                
            except Exception as e:
                print(f"  ⚠️  Request parsing error: {e}")
                self._send_error(conn, 400, "Bad Request")
                
        except Exception as e:
            print(f"  ⚠️  Connection handler error: {e}")
            
        finally:
            try:
                conn.close()
            except:
                pass
                
    async def _route_request(self, conn, method, path):
        """
        Route request to appropriate handler
        
        Args:
            conn: Socket connection
            method (str): HTTP method
            path (str): Request path (may include query string)
        """
        try:
            # Remove query string for routing
            clean_path = path.split('?')[0] if '?' in path else path
            
            # Route based on path
            if clean_path == '/':
                # HTTP 302 redirect to /index.html
                response = (
                    "HTTP/1.1 302 Found\r\n"
                    "Location: /index.html\r\n"
                    "Content-Length: 0\r\n"
                    f"Access-Control-Allow-Origin: *\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )
                conn.send(response.encode())
                
            elif clean_path == '/index.html':
                await self._handle_serve_html(conn)
                
            elif clean_path == '/ping':
                self._handle_ping(conn)
                
            elif clean_path == '/relay':
                await self._handle_relay(conn, path)
                
            elif clean_path == '/timer':
                await self._handle_timer(conn, path)
                
            elif clean_path == '/timer-status':
                self._handle_timer_status(conn)
                
            elif clean_path == '/status':
                self._handle_status(conn)
                
            elif clean_path == '/all':
                await self._handle_all(conn, path)

            # WiFi endpoints
            elif clean_path == '/wifi-status':
                self._handle_wifi_status(conn)
            elif clean_path == '/wifi-config':
                await self._handle_wifi_config(conn, path)
            elif clean_path == '/wifi-mode':
                await self._handle_wifi_mode(conn, path)
            elif clean_path == '/wifi-hostname':
                await self._handle_wifi_hostname(conn, path)
                
            else:
                self._send_error(conn, 404, "Not Found")
                
        except Exception as e:
            print(f"Routing error: {e}")
            self._send_error(conn, 500, "Internal Server Error")
            
    async def _handle_serve_html(self, conn):
        """Serve index.html file"""
        try:
            # Try to open and serve HTML file
            filename = 'index.html'
            
            try:
                # Get file size
                file_size = None
                try:
                    import os
                    file_size = os.stat(filename)[6]
                    print(f"  📄 Serving {filename} ({file_size} bytes)")
                except Exception as size_err:
                    print(f"  ⚠️  Could not get file size: {size_err}")
                    
                # Send headers
                headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                )
                
                if file_size:
                    headers += f"Content-Length: {file_size}\r\n"
                    
                headers += (
                    "Access-Control-Allow-Origin: *\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )
                
                # Use sendall to ensure all header bytes are sent
                await self._sendall(conn, headers.encode())
                
                # Send file in chunks with proper send verification
                try:
                    with open(filename, 'rb') as f:
                        bytes_sent = 0
                        chunk_count = 0
                        while True:
                            chunk = f.read(self.CHUNK_SIZE)
                            if not chunk:
                                break
                            # Use sendall to ensure all bytes of chunk are sent
                            await self._sendall(conn, chunk)
                            bytes_sent += len(chunk)
                            chunk_count += 1
                            # Yield control every 10 chunks to allow other tasks
                            if chunk_count % 10 == 0:
                                await asyncio.sleep(0.001)
                        print(f"  ✓ Sent {bytes_sent} bytes in {chunk_count} chunks")
                except OSError as e:
                    # OSError with errno 2 = file not found
                    if e.args[0] == 2:
                        print(f"  ❌ HTML file not found: {filename}")
                        self._send_error(conn, 404, "HTML file not found")
                    else:
                        raise
                        
            except OSError as e:
                # OSError with errno 2 = file not found
                if e.args[0] == 2:
                    print(f"  ❌ HTML file not found: {filename}")
                    self._send_error(conn, 404, "HTML file not found")
                else:
                    raise
                    
        except Exception as e:
            print(f"  ❌ Error serving HTML: {e}")
            # MicroPython doesn't have traceback module, just print the error
            try:
                self._send_error(conn, 500, "Internal Server Error")
            except:
                pass
            
    def _handle_ping(self, conn):
        """Handle /ping endpoint"""
        response_data = json.dumps({
            "status": "ok",
            "message": "Server is running"
        })
        self._send_json(conn, 200, response_data)
        
    async def _handle_relay(self, conn, path):
        """Handle /relay endpoint (on/off control)"""
        try:
            # Parse query parameters
            if '?' not in path:
                self._send_error(conn, 400, "Missing parameters")
                return
                
            query_string = path.split('?')[1]
            params = self._parse_query_params(query_string)
            
            # Get GPIO and state
            gpio = int(params.get('gpio', 14))
            state_str = params.get('state', 'off').lower()
            
            # Validate
            if gpio not in self.gpio.RELAY_PINS:
                response_data = json.dumps({
                    "error": f"Invalid GPIO pin: {gpio}. Valid pins: [14, 15, 16, 17]"
                })
                self._send_json(conn, 400, response_data)
                return
                
            if state_str not in ['on', 'off']:
                response_data = json.dumps({
                    "error": "Invalid state. Use 'on' or 'off'"
                })
                self._send_json(conn, 400, response_data)
                return
                
            # Set relay state
            state = state_str == 'on'
            success = self.gpio.set_relay_state(gpio, state)
            
            if success:
                relay_num = self.GPIO_TO_RELAY.get(gpio, 0)
                response_data = json.dumps({
                    "status": "success",
                    "gpio": gpio,
                    "relay": relay_num,
                    "state": state_str,
                    "name": self.gpio.RELAY_PINS[gpio]["name"]
                })
                self._send_json(conn, 200, response_data)
            else:
                self._send_error(conn, 500, "Failed to set relay state")
                
        except ValueError:
            self._send_error(conn, 400, "Invalid parameter format")
        except Exception as e:
            print(f"Relay handler error: {e}")
            self._send_error(conn, 500, "Internal Server Error")
            
    async def _handle_timer(self, conn, path):
        """Handle /timer endpoint - starts timer and returns immediately (non-blocking)"""
        try:
            # Parse query parameters
            if '?' not in path:
                self._send_error(conn, 400, "Missing parameters")
                return
                
            query_string = path.split('?')[1]
            params = self._parse_query_params(query_string)
            
            # Get GPIO and duration
            gpio = int(params.get('gpio', 14))
            duration = float(params.get('duration', 1.0))
            
            # Validate
            if gpio not in self.gpio.RELAY_PINS:
                response_data = json.dumps({
                    "error": f"Invalid GPIO pin: {gpio}. Valid pins: [14, 15, 16, 17]"
                })
                self._send_json(conn, 400, response_data)
                return
                
            if duration <= 0 or duration > 3600:
                response_data = json.dumps({
                    "error": "Duration must be between 0 and 3600 seconds"
                })
                self._send_json(conn, 400, response_data)
                return
                
            # Start timer in background (non-blocking)
            # Create timer task and return immediately
            task = self.timer.create_timer_task(gpio, duration)
            
            # Get start time for response
            start_time = utime.time()
            
            relay_num = self.GPIO_TO_RELAY.get(gpio, 0)
            response_data = json.dumps({
                "status": "started",
                "gpio": gpio,
                "relay": relay_num,
                "duration": duration,
                "name": self.gpio.RELAY_PINS[gpio]["name"],
                "message": f"Timer started for {duration}s",
                "start_time": start_time
            })
            self._send_json(conn, 200, response_data)
            
        except ValueError:
            self._send_error(conn, 400, "Invalid parameter format")
        except Exception as e:
            print(f"Timer handler error: {e}")
            self._send_error(conn, 500, "Internal Server Error")
            
    def _handle_status(self, conn):
        """Handle /status endpoint"""
        try:
            states = self.gpio.get_all_states()
            active_timers = self.timer.get_active_timers()
            
            response_data = json.dumps({
                "status": "success",
                "relays": states,
                "active_timers": len(active_timers),
                "timers": active_timers
            })
            self._send_json(conn, 200, response_data)
            
        except Exception as e:
            print(f"Status handler error: {e}")
            self._send_error(conn, 500, "Internal Server Error")
            
    def _handle_timer_status(self, conn):
        """Handle /timer-status endpoint - get status of all active timers"""
        try:
            active_timers = self.timer.get_active_timers()
            
            response_data = json.dumps({
                "status": "success",
                "timers": active_timers
            })
            self._send_json(conn, 200, response_data)
            
        except Exception as e:
            print(f"Timer status handler error: {e}")
            self._send_error(conn, 500, "Internal Server Error")
            
    async def _handle_all(self, conn, path):
        """Handle /all endpoint (control all relays)"""
        try:
            # Parse query parameters
            if '?' not in path:
                self._send_error(conn, 400, "Missing parameters")
                return
                
            query_string = path.split('?')[1]
            params = self._parse_query_params(query_string)
            
            # Get state
            state_str = params.get('state', 'off').lower()
            
            if state_str not in ['on', 'off']:
                response_data = json.dumps({
                    "error": "Invalid state. Use 'on' or 'off'"
                })
                self._send_json(conn, 400, response_data)
                return
                
            # Set all relays
            state = state_str == 'on'
            for gpio in self.gpio.RELAY_PINS:
                self.gpio.set_relay_state(gpio, state)
                
            states = self.gpio.get_all_states()
            response_data = json.dumps({
                "status": "success",
                "state": state_str,
                "relays": states,
                "message": f"All relays turned {state_str.upper()}"
            })
            self._send_json(conn, 200, response_data)
            
        except ValueError:
            self._send_error(conn, 400, "Invalid parameter format")
        except Exception as e:
            print(f"All handler error: {e}")
            self._send_error(conn, 500, "Internal Server Error")

    def _handle_wifi_status(self, conn):
        """Return WiFi status for AP and STA"""
        try:
            ap_active = False
            ap_ip = None
            ap_ssid = None
            ap_hostname = None
            if self.wifi_ap:
                try:
                    status = self.wifi_ap.get_status()
                    ap_active = bool(status.get('active'))
                    ap_ip = status.get('ip')
                    ap_ssid = status.get('ssid')
                    ap_hostname = status.get('hostname')
                except Exception:
                    pass

            sta_connected = False
            sta_ip = None
            sta_ssid = None
            sta_hostname = None
            if self.wifi_sta:
                try:
                    sta_connected = self.wifi_sta.is_connected()
                    sta_ip = self.wifi_sta.get_ip()
                    sta_status = self.wifi_sta.status()
                    sta_ssid = sta_status.get('ssid')
                    sta_hostname = sta_status.get('hostname')
                except Exception:
                    pass

            mode = 'ap'
            if sta_connected and ap_active:
                mode = 'dual'
            elif sta_connected:
                mode = 'sta'

            data = json.dumps({
                "status": "success",
                "mode": mode,
                "ap_active": ap_active,
                "ap_ip": ap_ip,
                "ap_ssid": ap_ssid,
                "ap_hostname": ap_hostname,
                "sta_connected": sta_connected,
                "sta_ip": sta_ip,
                "sta_ssid": sta_ssid,
                "sta_hostname": sta_hostname,
            })
            self._send_json(conn, 200, data)
        except Exception as e:
            print(f"WiFi status error: {e}")
            self._send_error(conn, 500, "Internal Server Error")

    async def _handle_wifi_config(self, conn, path):
        """Accept SSID/password and attempt STA connect; keep AP briefly"""
        try:
            if '?' not in path:
                self._send_error(conn, 400, "Missing parameters")
                return
            params = self._parse_query_params(path.split('?')[1])
            ssid = params.get('ssid')
            password = params.get('password')
            if not ssid or password is None:
                self._send_error(conn, 400, "ssid and password required")
                return

            # Load existing config to preserve hostname
            existing_hostname = "darkroom-timer"
            try:
                with open('wifi_config.json', 'r') as f:
                    existing = json.loads(f.read())
                    existing_hostname = existing.get('hostname', "darkroom-timer")
            except Exception:
                pass
            
            # Persist credentials (including hostname)
            try:
                with open('wifi_config.json', 'w') as f:
                    f.write(json.dumps({
                        "ssid": ssid,
                        "password": password,
                        "hostname": existing_hostname
                    }))
            except Exception as e:
                print(f"WiFi config save error: {e}")

            # Attempt STA connect
            connected = False
            if self.wifi_sta:
                connected = await self.wifi_sta.connect(ssid, password, timeout_s=20)

            # On success: schedule AP stop after grace period
            if connected:
                ap_ip = None
                if self.wifi_ap:
                    try:
                        ap_ip = self.wifi_ap.get_ip()
                    except Exception:
                        pass
                    # Keep AP for a short grace period
                    asyncio.create_task(self._stop_ap_after_grace())

                sta_ip = self.wifi_sta.get_ip() if self.wifi_sta else None
                data = json.dumps({
                    "status": "success",
                    "message": "Connected to router",
                    "mode": "dual",  # initially both active during grace
                    "ap_ip": ap_ip,
                    "sta_ip": sta_ip,
                    "grace_seconds": self.ap_grace_s,
                })
                self._send_json(conn, 200, data)
            else:
                data = json.dumps({
                    "status": "error",
                    "message": "STA connection failed; staying in AP",
                })
                self._send_json(conn, 200, data)
        except Exception as e:
            print(f"WiFi config error: {e}")
            self._send_error(conn, 500, "Internal Server Error")

    async def _handle_wifi_mode(self, conn, path):
        """Switch WiFi mode: ap|sta using saved credentials"""
        try:
            if '?' not in path:
                self._send_error(conn, 400, "Missing parameters")
                return
            params = self._parse_query_params(path.split('?')[1])
            value = (params.get('value') or '').lower()
            if value not in ('ap', 'sta'):
                self._send_error(conn, 400, "value must be 'ap' or 'sta'")
                return

            if value == 'ap':
                # Start AP
                if self.wifi_ap:
                    try:
                        self.wifi_ap.start()
                    except Exception as e:
                        print(f"AP start error: {e}")
                data = json.dumps({
                    "status": "success",
                    "message": "AP started",
                    "mode": "ap",
                    "ap_ip": self.wifi_ap.get_ip() if self.wifi_ap else None,
                })
                self._send_json(conn, 200, data)
                return

            # STA mode: load saved credentials and attempt connect
            ssid = None
            password = None
            try:
                with open('wifi_config.json', 'r') as f:
                    saved = json.loads(f.read())
                    ssid = saved.get('ssid')
                    password = saved.get('password')
            except Exception as e:
                print(f"WiFi config load error: {e}")

            if not ssid or password is None:
                self._send_error(conn, 400, "No saved credentials")
                return

            connected = False
            if self.wifi_sta:
                connected = await self.wifi_sta.connect(ssid, password, timeout_s=20)
            if connected:
                ap_ip = None
                if self.wifi_ap:
                    ap_ip = self.wifi_ap.get_ip()
                    asyncio.create_task(self._stop_ap_after_grace())
                sta_ip = self.wifi_sta.get_ip() if self.wifi_sta else None
                data = json.dumps({
                    "status": "success",
                    "message": "STA connected",
                    "mode": "dual",
                    "ap_ip": ap_ip,
                    "sta_ip": sta_ip,
                    "grace_seconds": self.ap_grace_s,
                })
                self._send_json(conn, 200, data)
            else:
                data = json.dumps({
                    "status": "error",
                    "message": "STA connection failed; staying in AP",
                })
                self._send_json(conn, 200, data)

        except Exception as e:
            print(f"WiFi mode error: {e}")
            self._send_error(conn, 500, "Internal Server Error")

    async def _stop_ap_after_grace(self):
        """Stop AP after configured grace period"""
        try:
            await asyncio.sleep(self.ap_grace_s)
            if self.wifi_ap:
                try:
                    self.wifi_ap.stop()
                except Exception as e:
                    print(f"AP stop error: {e}")
        except Exception as e:
            print(f"Grace timer error: {e}")
            
    async def _handle_wifi_hostname(self, conn, path):
        """Set hostname for WiFi interfaces (STA and AP)"""
        try:
            if '?' not in path:
                self._send_error(conn, 400, "Missing parameters")
                return
            params = self._parse_query_params(path.split('?')[1])
            hostname = params.get('hostname')
            
            if not hostname:
                self._send_error(conn, 400, "hostname parameter required")
                return
                
            # Validate hostname (32 chars max, alphanumeric and hyphens only)
            if len(hostname) > 32:
                self._send_error(conn, 400, "Hostname too long (max 32 characters)")
                return
                
            if not all(c.isalnum() or c == '-' for c in hostname):
                self._send_error(conn, 400, "Hostname must contain only alphanumeric characters and hyphens")
                return
                
            # Update WiFi managers with new hostname
            if self.wifi_ap:
                self.wifi_ap.hostname = hostname
            if self.wifi_sta:
                self.wifi_sta.hostname = hostname
                
            # Persist hostname to wifi_config.json
            try:
                # Load existing config
                existing_ssid = None
                existing_password = None
                try:
                    with open('wifi_config.json', 'r') as f:
                        existing = json.loads(f.read())
                        existing_ssid = existing.get('ssid')
                        existing_password = existing.get('password')
                except Exception:
                    pass
                
                # Save with new hostname
                with open('wifi_config.json', 'w') as f:
                    f.write(json.dumps({
                        "ssid": existing_ssid,
                        "password": existing_password,
                        "hostname": hostname
                    }))
            except Exception as e:
                print(f"Hostname config save error: {e}")
                self._send_error(conn, 500, "Failed to save hostname")
                return
                
            data = json.dumps({
                "status": "success",
                "message": "Hostname updated",
                "hostname": hostname,
                "note": "Changes will take effect after WiFi restart"
            })
            self._send_json(conn, 200, data)
            
        except Exception as e:
            print(f"WiFi hostname error: {e}")
            self._send_error(conn, 500, "Internal Server Error")
            
    def _url_decode(self, text):
        """
        Simple URL decoder for MicroPython (replaces urllib.parse.unquote)
        
        Args:
            text (str): URL-encoded text
            
        Returns:
            str: Decoded text
        """
        # Handle + as space
        text = text.replace('+', ' ')
        
        # Handle %XX hex encoding
        result = []
        i = 0
        while i < len(text):
            if text[i] == '%' and i + 2 < len(text):
                try:
                    # Convert hex to character
                    hex_val = text[i+1:i+3]
                    char = chr(int(hex_val, 16))
                    result.append(char)
                    i += 3
                except:
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)
    
    def _parse_query_params(self, query_string):
        """
        Parse URL-encoded query parameters
        
        Args:
            query_string (str): Query string (e.g., "gpio=14&state=on")
            
        Returns:
            dict: Parsed parameters
        """
        params = {}
        try:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    try:
                        # Decode URL-encoded values
                        params[key] = self._url_decode(value)
                    except:
                        params[key] = value
        except:
            pass
        return params
        
    def _send_json(self, conn, status_code, data):
        """
        Send JSON response
        
        Args:
            conn: Socket connection
            status_code (int): HTTP status code
            data (str): JSON data string
        """
        try:
            status_text = "OK" if status_code == 200 else "ERROR"
            response = (
                f"HTTP/1.1 {status_code} {status_text}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(data)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Access-Control-Allow-Methods: GET, OPTIONS\r\n"
                f"Access-Control-Allow-Headers: Content-Type\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"{data}"
            )
            conn.send(response.encode())
        except OSError as e:
            # EBADF (9) = Bad file descriptor - socket is closed
            if e.args[0] == 9:
                print(f"Socket closed before response could be sent")
            else:
                print(f"Error sending JSON: {e}")
        except Exception as e:
            print(f"Error sending JSON: {e}")
    
    async def _sendall(self, conn, data):
        """
        Send all bytes over socket, retrying if TCP buffer is full.
        
        MicroPython's socket.send() may not send all bytes if the
        TCP buffer is full. This method loops until all bytes are sent.
        
        Args:
            conn: Socket connection
            data: Bytes to send
        """
        total_sent = 0
        data_len = len(data)
        retries = 0
        max_retries = 100  # Prevent infinite loops
        
        while total_sent < data_len and retries < max_retries:
            try:
                sent = conn.send(data[total_sent:])
                if sent == 0:
                    # Socket closed
                    raise OSError("Socket connection closed")
                total_sent += sent
            except OSError as e:
                # EBADF (9) = Bad file descriptor - socket is closed
                if e.args[0] == 9:
                    print(f"Socket closed during send")
                    return  # Don't raise, just return
                # EAGAIN/EWOULDBLOCK - buffer full, wait and retry
                elif "EAGAIN" in str(e) or retries < max_retries:
                    await asyncio.sleep(0.01)
                    retries += 1
                else:
                    raise
        
        if total_sent < data_len:
            raise OSError(f"Failed to send all bytes: {total_sent}/{data_len}")
            
    def _send_response(self, conn, status_code, data, content_type="text/plain"):
        """
        Send generic response
        
        Args:
            conn: Socket connection
            status_code (int): HTTP status code
            data (str): Response body
            content_type (str): Content-Type header
        """
        try:
            status_text = "OK" if status_code == 200 else "ERROR"
            response = (
                f"HTTP/1.1 {status_code} {status_text}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(data)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Access-Control-Allow-Methods: GET, OPTIONS\r\n"
                f"Access-Control-Allow-Headers: Content-Type\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"{data}"
            )
            conn.send(response.encode())
        except OSError as e:
            # EBADF (9) = Bad file descriptor - socket is closed
            if e.args[0] == 9:
                print(f"Socket closed before response could be sent")
            else:
                print(f"Error sending response: {e}")
        except Exception as e:
            print(f"Error sending response: {e}")
            
    def _send_error(self, conn, status_code, message):
        """
        Send error response
        
        Args:
            conn: Socket connection
            status_code (int): HTTP status code
            message (str): Error message
        """
        data = json.dumps({"error": message})
        self._send_json(conn, status_code, data)
        
    async def stop(self):
        """Stop HTTP server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("HTTP Server stopped")
