"""
Async HTTP Server for Raspberry Pi Pico 2 W
Socket-based server with CORS support and chunked file serving
MicroPython v1.27.0 compatible
"""

import socket
import asyncio
import json
import time
import gc
import os

# Server Configuration
HTTP_PORT = 80
CHUNK_SIZE = 512
SOCKET_TIMEOUT = 30

# HTML file to serve
HTML_FILE = "index.html"


class HTTPServer:
    """
    Lightweight async HTTP server for Pico 2 W.
    
    Features:
    - Chunked file serving for large HTML files
    - CORS headers on all responses
    - REST API endpoints for relay control
    - WiFi configuration endpoint
    """
    
    def __init__(self, gpio_control, timer_manager, wifi_ap=None, wifi_sta=None, light_meter=None, update_manager=None):
        """
        Initialize HTTP server.
        
        Args:
            gpio_control: GPIOControl instance
            timer_manager: TimerManager instance
            wifi_ap: WiFiAP instance (optional)
            wifi_sta: WiFiSTA instance (optional)
            light_meter: DarkroomLightMeter instance (optional)
            update_manager: UpdateManager instance (optional)
        """
        self.gpio = gpio_control
        self.timer = timer_manager
        self.wifi_ap = wifi_ap
        self.wifi_sta = wifi_sta
        self.light_meter = light_meter
        self.update_manager = update_manager
        self.sock = None
        self.running = False
    
    def _cors_headers(self):
        """Return CORS headers string."""
        return (
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
            "Access-Control-Max-Age: 86400\r\n"
        )
    
    def _json_response(self, data, status=200):
        """Build JSON response."""
        body = json.dumps(data)
        status_text = "OK" if status == 200 else "Bad Request" if status == 400 else "Internal Server Error"
        
        response = (
            f"HTTP/1.1 {status} {status_text}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"{self._cors_headers()}"
            f"Connection: close\r\n"
            f"\r\n"
            f"{body}"
        )
        return response.encode()
    
    def _url_decode(self, s):
        """Decode URL-encoded string."""
        result = []
        i = 0
        while i < len(s):
            if s[i] == '%' and i + 2 < len(s):
                try:
                    result.append(chr(int(s[i+1:i+3], 16)))
                    i += 3
                    continue
                except:
                    pass
            elif s[i] == '+':
                result.append(' ')
                i += 1
                continue
            result.append(s[i])
            i += 1
        return ''.join(result)
    
    def _parse_query_string(self, query):
        """Parse query string into dictionary."""
        params = {}
        if not query:
            return params
        
        for pair in query.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[self._url_decode(key)] = self._url_decode(value)
            else:
                params[self._url_decode(pair)] = ''
        
        return params
    
    def _parse_request(self, data):
        """Parse HTTP request."""
        try:
            # Decode request
            request = data.decode('utf-8')
            lines = request.split('\r\n')
            
            if not lines:
                return None, None, None, None
            
            # Parse request line
            parts = lines[0].split(' ')
            if len(parts) < 2:
                return None, None, None, None
            
            method = parts[0]
            path_with_query = parts[1]
            
            # Parse path and query string
            if '?' in path_with_query:
                path, query = path_with_query.split('?', 1)
            else:
                path = path_with_query
                query = ''
            
            params = self._parse_query_string(query)
            
            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
                elif line == '':
                    break
            
            return method, path, params, headers
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None, None, None, None
    
    async def _sendall(self, conn, data):
        """Send all data with retry logic for buffer management."""
        total_sent = 0
        while total_sent < len(data):
            try:
                sent = conn.send(data[total_sent:])
                if sent == 0:
                    await asyncio.sleep_ms(10)
                    continue
                total_sent += sent
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN
                    await asyncio.sleep_ms(10)
                else:
                    raise
    
    async def _serve_html(self, conn):
        """Serve HTML file in chunks."""
        try:
            # Get file size
            stat = os.stat(HTML_FILE)
            file_size = stat[6]
            
            # Send headers
            headers = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {file_size}\r\n"
                f"{self._cors_headers()}"
                f"Connection: close\r\n"
                f"\r\n"
            )
            await self._sendall(conn, headers.encode())
            
            # Stream file in chunks
            chunk_count = 0
            with open(HTML_FILE, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    await self._sendall(conn, chunk)
                    chunk_count += 1
                    
                    # Yield periodically for other tasks
                    if chunk_count % 10 == 0:
                        await asyncio.sleep_ms(1)
            
            return True
            
        except OSError as e:
            print(f"File serve error: {e}")
            # Send 404
            response = self._json_response({"error": "HTML file not found"}, 404)
            await self._sendall(conn, response)
            return False
    
    async def _handle_ping(self, conn, params):
        """Handle /ping endpoint."""
        response = self._json_response({
            "status": "ok",
            "message": "Server is running",
            "timestamp": time.ticks_ms()
        })
        await self._sendall(conn, response)
    
    async def _handle_relay(self, conn, params):
        """Handle /relay endpoint."""
        try:
            gpio = int(params.get('gpio', 14))
            state = params.get('state', 'off').lower()
            
            if not self.gpio.is_valid_pin(gpio):
                response = self._json_response({
                    "error": f"Invalid GPIO pin: {gpio}. Valid pins: 14, 15, 16, 17"
                }, 400)
                await self._sendall(conn, response)
                return
            
            if state not in ('on', 'off'):
                response = self._json_response({
                    "error": "State must be 'on' or 'off'"
                }, 400)
                await self._sendall(conn, response)
                return
            
            # Set relay state
            relay_state = state == 'on'
            success = self.gpio.set_relay_state(gpio, relay_state)
            
            # Stop any timer for this pin if turning off
            if not relay_state:
                self.timer.stop_timer(gpio)
            
            if success:
                response = self._json_response({
                    "status": "success",
                    "gpio": gpio,
                    "state": state,
                    "name": self.gpio.get_pin_name(gpio),
                    "timestamp": time.ticks_ms()
                })
            else:
                response = self._json_response({
                    "error": "Failed to set relay state"
                }, 500)
            
            await self._sendall(conn, response)
            
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameter: {e}"
            }, 400)
            await self._sendall(conn, response)
    
    async def _handle_timer(self, conn, params):
        """Handle /timer endpoint."""
        try:
            gpio = int(params.get('gpio', 14))
            duration = float(params.get('duration', 1.0))
            
            if not self.gpio.is_valid_pin(gpio):
                response = self._json_response({
                    "error": f"Invalid GPIO pin: {gpio}. Valid pins: 14, 15, 16, 17"
                }, 400)
                await self._sendall(conn, response)
                return
            
            if duration <= 0:
                response = self._json_response({
                    "error": "Duration must be positive"
                }, 400)
                await self._sendall(conn, response)
                return
            
            if duration > 3600:
                response = self._json_response({
                    "error": "Duration too long (max 3600s)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            # Start timer with scheduled start for synchronization
            timer_info = self.timer.start_timer(gpio, duration, scheduled=True)
            
            response = self._json_response({
                "status": "success",
                "gpio": gpio,
                "duration": duration,
                "name": self.gpio.get_pin_name(gpio),
                "message": f"Timer started for {duration}s",
                "start_at": timer_info["start_at"],
                "sync_delay_ms": timer_info["sync_delay_ms"],
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameters: {e}"
            }, 400)
            await self._sendall(conn, response)
    
    async def _handle_status(self, conn, params):
        """Handle /status endpoint."""
        states = self.gpio.get_all_states()
        timers = self.timer.get_all_timer_status()
        
        response = self._json_response({
            "status": "success",
            "relays": states,
            "active_timers": self.timer.get_active_count(),
            "timer_details": timers,
            "timestamp": time.ticks_ms()
        })
        await self._sendall(conn, response)
    
    async def _handle_all(self, conn, params):
        """Handle /all endpoint."""
        state = params.get('state', 'off').lower()
        
        if state not in ('on', 'off'):
            response = self._json_response({
                "error": "State must be 'on' or 'off'"
            }, 400)
            await self._sendall(conn, response)
            return
        
        if state == 'on':
            self.gpio.all_on()
        else:
            self.gpio.all_off()
            self.timer.stop_all_timers()
        
        response = self._json_response({
            "status": "success",
            "state": state,
            "results": self.gpio.get_all_states(),
            "timestamp": time.ticks_ms()
        })
        await self._sendall(conn, response)
    
    async def _handle_wifi_status(self, conn, params):
        """Handle /wifi-status endpoint."""
        status = {
            "ap": None,
            "sta": None
        }
        
        if self.wifi_ap:
            status["ap"] = self.wifi_ap.get_config()
        
        if self.wifi_sta:
            status["sta"] = self.wifi_sta.get_status()
        
        response = self._json_response({
            "status": "success",
            "wifi": status,
            "timestamp": time.ticks_ms()
        })
        await self._sendall(conn, response)
    
    async def _handle_wifi_config(self, conn, params):
        """Handle /wifi-config endpoint."""
        if not self.wifi_sta:
            response = self._json_response({
                "error": "WiFi STA not available"
            }, 400)
            await self._sendall(conn, response)
            return
        
        ssid = params.get('ssid', '').strip()
        password = params.get('password', '').strip()
        
        if not ssid:
            response = self._json_response({
                "error": "SSID is required"
            }, 400)
            await self._sendall(conn, response)
            return
        
        if len(password) < 8:
            response = self._json_response({
                "error": "Password must be at least 8 characters"
            }, 400)
            await self._sendall(conn, response)
            return
        
        # Attempt connection
        ip = await self.wifi_sta.connect_async(ssid, password, save=True)
        
        if ip:
            response = self._json_response({
                "status": "success",
                "message": f"Connected to {ssid}",
                "ip": ip,
                "timestamp": time.ticks_ms()
            })
        else:
            response = self._json_response({
                "error": f"Failed to connect to {ssid}"
            }, 400)
        
        await self._sendall(conn, response)
    
    async def _handle_wifi_ap_force(self, conn, params):
        """Handle /wifi-ap-force endpoint - force AP (hotspot) mode."""
        try:
            # Disconnect from STA if connected
            if self.wifi_sta:
                print("Disconnecting from WiFi router...")
                self.wifi_sta.disconnect()
                await asyncio.sleep(0.5)
            
            # Ensure AP is running
            ap_ip = "192.168.4.1"
            if self.wifi_ap:
                if not self.wifi_ap.ap or not self.wifi_ap.ap.active():
                    print("Starting WiFi AP...")
                    ap_ip = self.wifi_ap.start() or "192.168.4.1"
                else:
                    ap_ip = self.wifi_ap.ap.ifconfig()[0]
                    print(f"AP already active: {ap_ip}")
            
            response = self._json_response({
                "status": "success",
                "message": "Switched to AP (hotspot) mode",
                "ap_ip": ap_ip,
                "timestamp": time.ticks_ms()
            })
        except Exception as e:
            print(f"Force AP error: {e}")
            response = self._json_response({
                "error": f"Failed to switch to AP mode: {e}"
            }, 500)
        
        await self._sendall(conn, response)
    
    async def _handle_wifi_clear(self, conn, params):
        """Handle /wifi-clear endpoint - clear saved WiFi credentials."""
        try:
            import os
            config_file = "wifi_config.json"
            
            # Try to delete the config file
            try:
                os.remove(config_file)
                message = "WiFi credentials cleared successfully"
                print(f"Deleted {config_file}")
            except OSError:
                message = "No saved credentials found (already cleared)"
                print(f"No {config_file} to delete")
            
            # Clear in-memory credentials if wifi_sta exists
            if self.wifi_sta:
                self.wifi_sta.ssid = None
                self.wifi_sta.password = None
            
            response = self._json_response({
                "status": "success",
                "message": message,
                "timestamp": time.ticks_ms()
            })
        except Exception as e:
            print(f"Clear credentials error: {e}")
            response = self._json_response({
                "error": f"Failed to clear credentials: {e}"
            }, 500)
        
        await self._sendall(conn, response)
    
    async def _handle_temperature(self, conn, params):
        """Handle /temperature endpoint - get current temperature reading."""
        if not self.timer.temperature_sensor:
            response = self._json_response({
                "error": "Temperature sensor not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            status = self.timer.get_heating_status()
            response = self._json_response({
                "status": "success",
                "temperature": status.get("temperature"),
                "target": status.get("target"),
                "relay_on": status.get("relay_on"),
                "connected": status.get("connected"),
                "enabled": status.get("enabled"),
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to read temperature: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_temperature_control(self, conn, params):
        """Handle /temperature-control endpoint - set target temperature."""
        if not self.timer.temperature_sensor:
            response = self._json_response({
                "error": "Temperature sensor not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            target_str = params.get('target', '').strip()
            
            if not target_str:
                response = self._json_response({
                    "error": "Target temperature is required (query param: ?target=X)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            target = float(target_str)
            
            # Validate range (18°C to 40°C for photo chemicals)
            if target < 15 or target > 50:
                response = self._json_response({
                    "error": f"Target temperature out of range. Valid range: 15°C - 50°C"
                }, 400)
                await self._sendall(conn, response)
                return
            
            # Set target temperature
            self.timer.set_target_temperature(target)
            
            response = self._json_response({
                "status": "success",
                "message": f"Target temperature set to {target}°C",
                "target": target,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except ValueError:
            response = self._json_response({
                "error": f"Invalid target temperature: {params.get('target')}. Must be a number."
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to set temperature: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_temperature_enable(self, conn, params):
        """Handle /temperature-enable endpoint - enable or disable temperature control."""
        if not self.timer.temperature_sensor:
            response = self._json_response({
                "error": "Temperature sensor not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            enabled_str = params.get('enabled', '').strip().lower()
            
            if enabled_str not in ('true', 'false', '1', '0'):
                response = self._json_response({
                    "error": "enabled parameter required (true/false)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            enabled = enabled_str in ('true', '1')
            self.timer.set_heating_enabled(enabled)
            
            response = self._json_response({
                "status": "success",
                "enabled": enabled,
                "message": f"Temperature control {'enabled' if enabled else 'disabled'}",
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to set temperature enable: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_papers(self, conn, params):
        """
        Handle /papers endpoint - get list of available papers and their metadata.
        
        Returns:
            papers: List of paper objects with id, display_name, manufacturer, and filters
        """
        try:
            from lib.paper_database import get_paper_list, get_paper_data, get_paper_display_name
            
            papers = []
            for paper_id in get_paper_list():
                paper_data = get_paper_data(paper_id)
                if paper_data:
                    manufacturer = paper_data.get('manufacturer', '')
                    
                    # Build filter metadata for UI use
                    # Include factor, iso_r, and gamma for client calculations
                    # while keeping response size manageable for MicroPython
                    filters = {}
                    for grade, data in paper_data.get('filters', {}).items():
                        if grade in ('', 'none'):
                            name = 'No Filter'
                        elif 'ilford' in manufacturer.lower():
                            name = f"Grade {grade}"
                        else:
                            foma_names = {
                                '2xY': '2xY (Soft)',
                                'Y': 'Y',
                                'M1': 'M1',
                                '2xM1': '2xM1',
                                'M2': 'M2',
                                '2xM2': '2xM2 (Hard)'
                            }
                            name = foma_names.get(grade, grade)
                        
                        filters[grade] = {
                            'factor': data.get('factor', 1.0),
                            'name': name,
                            'iso_r': data.get('iso_r'),
                            'gamma': data.get('gamma')
                        }
                    
                    # Only include essential fields to minimize response size for MicroPython
                    papers.append({
                        'id': paper_id,
                        'display_name': get_paper_display_name(paper_id),
                        'filters': filters
                    })
            
            # Build response with minimal data
            print(f"Built papers list with {len(papers)} papers")
            
            # Try to serialize JSON - might fail if too large for MicroPython
            try:
                import gc
                gc.collect()  # Free memory before JSON serialization
                
                response_data = {
                    "status": "success",
                    "papers": papers,
                    "count": len(papers)
                }
                response = self._json_response(response_data)
                await self._sendall(conn, response)
                
            except MemoryError:
                print("ERROR: Out of memory while building /papers response")
                response = self._json_response({
                    "error": "Response too large - memory error"
                }, 500)
                await self._sendall(conn, response)
            
        except Exception as e:
            print(f"ERROR in _handle_papers: {e}")
            response = self._json_response({
                "error": f"Failed to get papers: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_paper(self, conn, params):
        """
        Handle /light-meter-paper endpoint - get/set current paper selection.
        
        GET: Returns current paper ID
        Query params for GET:
            (none)
        
        Query params for SET:
            paper_id: Paper identifier from paper_database (e.g., 'ilford_cooltone')
        
        Returns current paper information.
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            paper_id = params.get('paper_id')
            
            if paper_id:
                # SET paper
                self.light_meter.set_current_paper(paper_id)
            
            # GET current paper
            from lib.paper_database import get_paper_data, get_paper_display_name
            current_paper_id = self.light_meter.get_current_paper()
            paper_data = get_paper_data(current_paper_id)
            
            if not paper_data:
                response = self._json_response({
                    "error": f"Invalid current paper: {current_paper_id}"
                }, 500)
                await self._sendall(conn, response)
                return
            
            response = self._json_response({
                "status": "success",
                "paper_id": current_paper_id,
                "display_name": get_paper_display_name(current_paper_id),
                "manufacturer": paper_data['manufacturer'],
                "paper_type": paper_data.get('paper_type', ''),
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid paper_id: {e}"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to get/set paper: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter(self, conn, params):
        """
        Handle /light-meter endpoint - take a light measurement.
        
        Query params:
            samples: Number of samples to average (default: 5)
            calibration: Calibration constant for exposure calc (optional)
            filter: Filter grade for exposure calc (optional)
            paper_id: Paper ID to use for filter factors (optional, defaults to current paper)
        
        Returns lux reading and calculated exposure time.
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            samples = int(params.get('samples', 5))
            calibration = params.get('calibration')
            filter_grade = params.get('filter')
            paper_id = params.get('paper_id')
            
            if calibration:
                calibration = float(calibration)
            
            # Take measurement
            result = await self.light_meter.measure_lux_async(samples=samples)
            
            if result.get('lux') is None:
                response = self._json_response({
                    "error": result.get('error', "Failed to read sensor"),
                    "sensor_status": self.light_meter.sensor.get_status()
                }, 500)
                await self._sendall(conn, response)
                return
            
            # Calculate exposure time using current or specified paper
            exposure_time = self.light_meter.calculate_exposure_time(
                result['lux'],
                calibration=calibration,
                filter_grade=filter_grade,
                paper_id=paper_id
            )
            
            # Get current paper info
            from lib.paper_database import get_paper_display_name
            current_paper_id = paper_id or self.light_meter.get_current_paper()
            
            response = self._json_response({
                "status": "success",
                "lux": result['lux'],
                "min_lux": result.get('min'),
                "max_lux": result.get('max'),
                "samples": result.get('samples'),
                "variance": result.get('variance'),
                "exposure_time": exposure_time,
                "filter": filter_grade,
                "paper_id": current_paper_id,
                "paper_name": get_paper_display_name(current_paper_id),
                "calibration": calibration or self.light_meter.default_calibration,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameters: {e}"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Light meter error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_highlight(self, conn, params):
        """
        Handle /light-meter-highlight endpoint - measure highlight area.
        
        Stores the reading for contrast analysis.
        Place sensor at brightest area of projected image.
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            samples = int(params.get('samples', 5))
            
            result = await self.light_meter.measure_highlight_async(samples=samples)
            
            if result.get('lux') is None:
                response = self._json_response({
                    "error": result.get('error', "Failed to read sensor")
                }, 500)
                await self._sendall(conn, response)
                return
            
            response = self._json_response({
                "status": "success",
                "type": "highlight",
                "lux": result['lux'],
                "samples": result.get('samples'),
                "variance": result.get('variance'),
                "stored_highlight": self.light_meter.highlight_lux,
                "stored_shadow": self.light_meter.shadow_lux,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except Exception as e:
            response = self._json_response({
                "error": f"Highlight measurement error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_shadow(self, conn, params):
        """
        Handle /light-meter-shadow endpoint - measure shadow area.
        
        Stores the reading for contrast analysis.
        Place sensor at darkest area of projected image.
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            samples = int(params.get('samples', 5))
            
            result = await self.light_meter.measure_shadow_async(samples=samples)
            
            if result.get('lux') is None:
                response = self._json_response({
                    "error": result.get('error', "Failed to read sensor")
                }, 500)
                await self._sendall(conn, response)
                return
            
            response = self._json_response({
                "status": "success",
                "type": "shadow",
                "lux": result['lux'],
                "samples": result.get('samples'),
                "variance": result.get('variance'),
                "stored_highlight": self.light_meter.highlight_lux,
                "stored_shadow": self.light_meter.shadow_lux,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except Exception as e:
            response = self._json_response({
                "error": f"Shadow measurement error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_contrast(self, conn, params):
        """
        Handle /light-meter-contrast endpoint - get contrast analysis.
        
        Query params:
            paper_id: Paper ID to use for analysis (optional, defaults to current paper)
            calibration: Calibration constant from client (optional, uses server-side if not provided)
        
        Returns ΔEV, recommended filter grade, and split-grade calculations
        based on stored highlight and shadow readings.
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            paper_id = params.get('paper_id')
            
            # Get calibration from request (takes priority over server-side)
            calibration_str = params.get('calibration')
            calibration = None
            if calibration_str:
                try:
                    calibration = float(calibration_str)
                except (ValueError, TypeError):
                    pass
            analysis = self.light_meter.get_contrast_analysis(
                paper_id=paper_id,
                calibration=calibration,
            )
            
            if 'error' in analysis:
                response = self._json_response({
                    "error": analysis['error'],
                    "highlight_lux": analysis.get('highlight_lux'),
                    "shadow_lux": analysis.get('shadow_lux')
                }, 400)
                await self._sendall(conn, response)
                return
            
            # Get current paper info
            from lib.paper_database import get_paper_display_name
            current_paper_id = paper_id or self.light_meter.get_current_paper()
            
            response = self._json_response({
                "status": "success",
                "highlight_lux": analysis['highlight_lux'],
                "shadow_lux": analysis['shadow_lux'],
                "delta_ev": analysis['delta_ev'],
                "recommended_grade": analysis['recommended_grade'],
                "split_grade": analysis['split_grade'],
                "exposure_times": analysis.get('exposure_times'),
                "paper_id": current_paper_id,
                "paper_name": get_paper_display_name(current_paper_id),
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except Exception as e:
            response = self._json_response({
                "error": f"Contrast analysis error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_split_grade_heiland(self, conn, params):
        """
        Handle /light-meter-split-grade-heiland endpoint - calculate Heiland-like split-grade.
        
        Query params:
            highlight: Highlight lux reading
            shadow: Shadow lux reading
            calibration: Calibration constant (lux·s)
            paper_id: Paper ID (e.g., 'ilford_cooltone', 'foma_fomaspeed')
            system: (deprecated) Legacy filter system parameter
        
        Returns Heiland-like split-grade calculation with dynamic filter selection.
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            highlight_lux = float(params.get('highlight', 0))
            shadow_lux = float(params.get('shadow', 0))
            calibration = float(params.get('calibration', self.light_meter.default_calibration))
            
            # Accept paper_id (new) or system (legacy fallback)
            paper_id = params.get('paper_id')
            if not paper_id:
                # Fallback to system for backward compatibility
                paper_id = params.get('system', self.light_meter.current_paper_id or self.light_meter.filter_system)
            
            if highlight_lux <= 0 or shadow_lux <= 0:
                response = self._json_response({
                    "error": "Invalid lux readings (must be positive)",
                    "highlight_lux": highlight_lux,
                    "shadow_lux": shadow_lux
                }, 400)
                await self._sendall(conn, response)
                return

            # Calculate Heiland-like split-grade with paper_id
            result = self.light_meter.calculate_split_grade_heiland(
                highlight_lux=highlight_lux,
                shadow_lux=shadow_lux,
                calibration=calibration,
                system=paper_id,  # Pass paper_id as system parameter for now
            )
            
            if result is None:
                response = self._json_response({
                    "error": "Failed to calculate Heiland split-grade",
                    "highlight_lux": highlight_lux,
                    "shadow_lux": shadow_lux
                }, 500)
                await self._sendall(conn, response)
                return
            
            response = self._json_response({
                "status": "success",
                "result": result,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameters: {e}"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Heiland split-grade calculation error: {e}"
            }, 500)
            await self._sendall(conn, response)

    async def _handle_light_meter_virtual_proof(self, conn, params):
        """
        Handle /light-meter-virtual-proof endpoint - map lux to zones and preview density.

        Query params:
            lux: Lux reading for the sample
            reference_lux: Optional reference lux (Zone V)
            calibration: Calibration constant (optional)
            paper_id: Paper ID to use for curves and filter data
            filter: Filter grade for gamma selection (optional)
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return

        try:
            lux = float(params.get('lux', 0))
            ref = params.get('reference_lux')
            reference_lux = float(ref) if ref else None
            calibration = params.get('calibration')
            calibration = float(calibration) if calibration else None
            paper_id = params.get('paper_id')
            filter_grade = params.get('filter')

            result = self.light_meter.calculate_virtual_proof_sample(
                lux,
                reference_lux=reference_lux,
                paper_id=paper_id,
                filter_grade=filter_grade,
                calibration=calibration,
            )

            if result.get('error'):
                response = self._json_response({
                    "error": result['error']
                }, 400)
                await self._sendall(conn, response)
                return

            response = self._json_response({
                "status": "success",
                "result": result,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)

        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameters: {e}"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Virtual proof error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_calibrate(self, conn, params):
        """
        Handle /light-meter-calibrate endpoint - set calibration.
        
        Query params:
            paper_id: Paper identifier (e.g., 'ilford_mg4_rc')
            constant: Calibration constant (lux × seconds)
            set_default: If 'true', set as default calibration
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            paper_id = params.get('paper_id', '').strip()
            constant_str = params.get('constant', '').strip()
            set_default = params.get('set_default', '').lower() == 'true'
            
            if not constant_str:
                response = self._json_response({
                    "error": "Calibration constant required (?constant=X)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            constant = float(constant_str)
            
            if constant <= 0:
                response = self._json_response({
                    "error": "Calibration constant must be positive"
                }, 400)
                await self._sendall(conn, response)
                return
            
            if paper_id:
                self.light_meter.set_calibration(paper_id, constant)
            
            if set_default or not paper_id:
                self.light_meter.default_calibration = constant
            
            response = self._json_response({
                "status": "success",
                "paper_id": paper_id or "default",
                "calibration": constant,
                "is_default": set_default or not paper_id,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except ValueError:
            response = self._json_response({
                "error": "Invalid calibration value"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Calibration error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_light_meter_config(self, conn, params):
        """
        Handle /light-meter-config endpoint - configure light meter.
        
        Query params:
            paper_id: Paper/filter system ID (e.g., 'ilford_cooltone', 'foma_fomaspeed')
            filter_system: (deprecated) Legacy filter system parameter - use paper_id instead
            gain: 'low', 'med', 'high', 'max', or 'auto'
            integration: 100, 200, 300, 400, 500, or 600 (ms)
            clear: 'true' to clear stored highlight/shadow readings
        """
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            paper_id = params.get('paper_id', '').strip().lower()
            filter_system = params.get('filter_system', '').strip().lower()
            gain = params.get('gain', '').strip().lower()
            integration = params.get('integration', '').strip()
            clear = params.get('clear', '').lower() == 'true'
            
            changes = []
            
            # Set paper (paper_id takes precedence over legacy filter_system)
            if paper_id:
                from lib.paper_database import get_paper_data
                try:
                    paper_data = get_paper_data(paper_id)
                    self.light_meter.set_current_paper(paper_id)
                    changes.append(f"paper_id={paper_id}")
                except (KeyError, ValueError):
                    from lib.paper_database import get_paper_list
                    valid_papers = get_paper_list()
                    response = self._json_response({
                        "error": f"Invalid paper_id. Use: {valid_papers}"
                    }, 400)
                    await self._sendall(conn, response)
                    return
            elif filter_system:
                # Legacy fallback: support old filter_system param for backward compatibility
                valid_systems = [
                    'ilford', 'foma_fomaspeed', 'foma_fomatone',
                    'foma_fomapastel_mg', 'fomatone_mg_classic_variant',
                    'ilford_cooltone', 'ilford_iv_rc_portfolio',
                    'ilford_multigrade_rc_deluxe_new', 'ilford_multigrade_rc_portfolio_new',
                    'ilford_fb_classic', 'ilford_fb_warmtone', 'ilford_fb_cooltone',
                    'foma_fomabrom', 'ilford_mg_iv', 'ilford_warmtone'
                ]
                if filter_system in valid_systems:
                    self.light_meter.set_filter_system(filter_system)
                    changes.append(f"filter_system={filter_system} (legacy)")
                else:
                    response = self._json_response({
                        "error": f"Invalid filter_system. Use paper_id param instead. Valid: {valid_systems}"
                    }, 400)
                    await self._sendall(conn, response)
                    return
            
            # Set gain
            if gain:
                from lib.light_sensor import TSL2591
                gain_map = {
                    'low': TSL2591.GAIN_LOW,
                    'med': TSL2591.GAIN_MED,
                    'high': TSL2591.GAIN_HIGH,
                    'max': TSL2591.GAIN_MAX
                }
                
                if gain == 'auto':
                    self.light_meter.sensor.auto_gain()
                    changes.append("gain=auto")
                elif gain in gain_map:
                    self.light_meter.sensor.set_gain(gain_map[gain])
                    changes.append(f"gain={gain}")
                else:
                    response = self._json_response({
                        "error": "Invalid gain. Use: low, med, high, max, auto"
                    }, 400)
                    await self._sendall(conn, response)
                    return
            
            # Set integration time
            if integration:
                from lib.light_sensor import TSL2591
                int_map = {
                    '100': TSL2591.INTEGRATIONTIME_100MS,
                    '200': TSL2591.INTEGRATIONTIME_200MS,
                    '300': TSL2591.INTEGRATIONTIME_300MS,
                    '400': TSL2591.INTEGRATIONTIME_400MS,
                    '500': TSL2591.INTEGRATIONTIME_500MS,
                    '600': TSL2591.INTEGRATIONTIME_600MS
                }
                
                if integration in int_map:
                    self.light_meter.sensor.set_integration_time(int_map[integration])
                    changes.append(f"integration={integration}ms")
                else:
                    response = self._json_response({
                        "error": "Invalid integration. Use: 100, 200, 300, 400, 500, 600"
                    }, 400)
                    await self._sendall(conn, response)
                    return
            
            # Clear readings
            if clear:
                self.light_meter.clear_readings()
                changes.append("readings_cleared")
            
            # Return current status
            status = self.light_meter.get_status()
            
            response = self._json_response({
                "status": "success",
                "changes": changes,
                "light_meter": status,
                "timestamp": time.ticks_ms()
            })
            await self._sendall(conn, response)
            
        except Exception as e:
            response = self._json_response({
                "error": f"Configuration error: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_options(self, conn):
        """Handle OPTIONS preflight request."""
        response = (
            f"HTTP/1.1 200 OK\r\n"
            f"{self._cors_headers()}"
            f"Content-Length: 0\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        await self._sendall(conn, response.encode())
    
    async def _handle_request(self, conn, addr):
        """Handle incoming HTTP request."""
        try:
            # Set socket timeout
            conn.settimeout(SOCKET_TIMEOUT)
            
            # Receive request
            data = conn.recv(2048)
            if not data:
                return
            
            # Parse request
            method, path, params, headers = self._parse_request(data)
            
            if not method:
                return
            
            print(f"{method} {path} from {addr[0]}")
            
            # Handle OPTIONS preflight
            if method == 'OPTIONS':
                await self._handle_options(conn)
                return
            
            # Route request
            if path in ('/', '/index.html'):
                await self._serve_html(conn)
            elif path == '/ping':
                await self._handle_ping(conn, params)
            elif path == '/relay':
                await self._handle_relay(conn, params)
            elif path == '/timer':
                await self._handle_timer(conn, params)
            elif path == '/status':
                await self._handle_status(conn, params)
            elif path == '/all':
                await self._handle_all(conn, params)
            elif path == '/temperature':
                await self._handle_temperature(conn, params)
            elif path == '/temperature-control':
                await self._handle_temperature_control(conn, params)
            elif path == '/temperature-enable':
                await self._handle_temperature_enable(conn, params)
            elif path == '/wifi-status':
                await self._handle_wifi_status(conn, params)
            elif path == '/wifi-config':
                await self._handle_wifi_config(conn, params)
            elif path == '/wifi-ap-force':
                await self._handle_wifi_ap_force(conn, params)
            elif path == '/wifi-clear':
                await self._handle_wifi_clear(conn, params)
            elif path == '/papers':
                await self._handle_papers(conn, params)
            elif path == '/light-meter-paper':
                await self._handle_light_meter_paper(conn, params)
            elif path == '/light-meter':
                await self._handle_light_meter(conn, params)
            elif path == '/light-meter-highlight':
                await self._handle_light_meter_highlight(conn, params)
            elif path == '/light-meter-shadow':
                await self._handle_light_meter_shadow(conn, params)
            elif path == '/light-meter-contrast':
                await self._handle_light_meter_contrast(conn, params)
            elif path == '/light-meter-split-grade-heiland':
                await self._handle_light_meter_split_grade_heiland(conn, params)
            elif path == '/light-meter-virtual-proof':
                await self._handle_light_meter_virtual_proof(conn, params)
            elif path == '/light-meter-calibrate':
                await self._handle_light_meter_calibrate(conn, params)
            elif path == '/light-meter-config':
                await self._handle_light_meter_config(conn, params)
            elif path == '/update-check':
                await self._handle_update_check(conn, params)
            elif path == '/favicon.ico':
                # Return empty response for favicon
                response = "HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n"
                await self._sendall(conn, response.encode())
            else:
                # 404 Not Found
                response = self._json_response({
                    "error": f"Not found: {path}"
                }, 404)
                await self._sendall(conn, response)
                
        except Exception as e:
            print(f"Request error: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
    
    def start(self, port=HTTP_PORT):
        """Start HTTP server (creates socket)."""
        try:
            # Cleanup memory before starting
            gc.collect()
            
            # Create socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind and listen
            self.sock.bind(('0.0.0.0', port))
            self.sock.listen(5)
            
            # Set non-blocking
            self.sock.setblocking(False)
            
            self.running = True
            print(f"HTTP server started on port {port}")
            
        except Exception as e:
            print(f"HTTP server start error: {e}")
            self.sock = None
    
    def stop(self):
        """Stop HTTP server."""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        print("HTTP server stopped")
    
    async def _handle_update_check(self, conn, params):
        """Handle GET /update-check - Check for available updates from GitHub."""
        try:
            if not self.update_manager:
                response = self._json_response({
                    'success': False,
                    'error': 'UpdateManager not initialized'
                }, 400)
                await self._sendall(conn, response)
                return
            
            # Check for updates and download if available
            result = await self.update_manager.check_and_download()
            
            # Determine HTTP status
            status = 200 if result.get('success', False) else 400
            
            response = self._json_response(result, status)
            await self._sendall(conn, response)
            
            # If update succeeded and restart is required, schedule restart
            if result.get('success') and result.get('restart_required'):
                print("[HTTPServer] Update successful, scheduling restart in 3 seconds...")
                asyncio.create_task(self.update_manager.trigger_restart(delay_ms=3000))
        
        except Exception as e:
            print(f"[HTTPServer] Error in /update-check: {e}")
            response = self._json_response({
                'success': False,
                'error': str(e)
            }, 500)
            await self._sendall(conn, response)
    
    async def run_async(self):
        """Run HTTP server loop asynchronously."""
        if not self.sock:
            self.start()
        
        if not self.sock:
            return
        
        while self.running:
            try:
                # Try to accept connection
                try:
                    conn, addr = self.sock.accept()
                    # Handle request in background
                    asyncio.create_task(self._handle_request(conn, addr))
                except OSError:
                    # No connection available (EAGAIN)
                    await asyncio.sleep_ms(10)
                    
            except Exception as e:
                print(f"Server loop error: {e}")
                await asyncio.sleep_ms(100)

