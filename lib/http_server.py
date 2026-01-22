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
    
    def __init__(self, gpio_control, timer_manager, wifi_ap=None, wifi_sta=None, light_meter=None):
        """
        Initialize HTTP server.
        
        Args:
            gpio_control: GPIOControl instance
            timer_manager: TimerManager instance
            wifi_ap: WiFiAP instance (optional)
            wifi_sta: WiFiSTA instance (optional)
            light_meter: LightMeterManager instance (optional)
        """
        self.gpio = gpio_control
        self.timer = timer_manager
        self.wifi_ap = wifi_ap
        self.wifi_sta = wifi_sta
        self.light_meter = light_meter
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
    
    # ===== LIGHT METER ENDPOINTS =====
    
    async def _handle_meter_read(self, conn, params):
        """Handle /meter/read endpoint - take a single lux reading."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            reading = self.light_meter.read_lux()
            response = self._json_response(reading)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to read light meter: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_add_reading(self, conn, params):
        """Handle /meter/add-reading endpoint - add reading to multi-point average."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            reading_type = params.get('type', '').lower()
            
            if reading_type not in ('shadow', 'highlight'):
                response = self._json_response({
                    "error": "type parameter required (shadow or highlight)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            result = self.light_meter.add_reading(reading_type)
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to add reading: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_get_average(self, conn, params):
        """Handle /meter/get-average endpoint - get current average for a reading type."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            reading_type = params.get('type', '').lower()
            
            if reading_type not in ('shadow', 'highlight'):
                response = self._json_response({
                    "error": "type parameter required (shadow or highlight)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            result = self.light_meter.get_average(reading_type)
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to get average: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_capture(self, conn, params):
        """Handle /meter/capture endpoint - finalize capture using averaged value."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            reading_type = params.get('type', '').lower()
            
            if reading_type not in ('shadow', 'highlight'):
                response = self._json_response({
                    "error": "type parameter required (shadow or highlight)"
                }, 400)
                await self._sendall(conn, response)
                return
            
            result = self.light_meter.capture(reading_type)
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to capture: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_calculate(self, conn, params):
        """Handle /meter/calculate endpoint - calculate exposure/grade/split."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            mode = params.get('mode', 'exposure').lower()
            profile = params.get('profile', '')
            
            # Set profile if specified
            if profile:
                self.light_meter.set_current_profile(profile)
            
            if mode not in ('exposure', 'grade', 'split'):
                response = self._json_response({
                    "error": "mode must be 'exposure', 'grade', or 'split'"
                }, 400)
                await self._sendall(conn, response)
                return
            
            result = self.light_meter.calculate(mode)
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to calculate: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_gain(self, conn, params):
        """Handle /meter/gain endpoint - control sensor gain (fixed or auto)."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            action = params.get('action', '').lower()
            
            if action == 'auto':
                # Enable auto-gain
                self.light_meter.light_sensor.enable_auto_gain()
                response = self._json_response({
                    "message": "Auto-gain enabled",
                    "auto_gain": True,
                    "gain": "auto"
                })
            elif action == 'disable':
                # Disable auto-gain (keep current gain)
                self.light_meter.light_sensor.disable_auto_gain()
                response = self._json_response({
                    "message": "Auto-gain disabled",
                    "auto_gain": False,
                    "gain": self.light_meter.light_sensor.gain
                })
            elif action in ('1x', '25x', '428x', '9876x', 'low', 'med', 'high', 'max'):
                # Set manual gain
                gain_map = {
                    '1x': 0x00, 'low': 0x00,
                    '25x': 0x10, 'med': 0x10,
                    '428x': 0x20, 'high': 0x20,
                    '9876x': 0x30, 'max': 0x30
                }
                gain_level = gain_map[action]
                success = self.light_meter.light_sensor.set_manual_gain(gain_level)
                
                if success:
                    response = self._json_response({
                        "message": f"Gain set to {action}",
                        "auto_gain": False,
                        "gain": action
                    })
                else:
                    response = self._json_response({
                        "error": f"Failed to set gain to {action}"
                    }, 400)
            else:
                response = self._json_response({
                    "error": "action required: 'auto', 'disable', or gain level (1x, 25x, 428x, 9876x)"
                }, 400)
            
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to control gain: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_response_mode(self, conn, params):
        """Handle /meter/response-mode endpoint - control sensor update speed."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            mode = params.get('mode', '').lower()
            
            mode_map = {
                'stable': 0,
                'balanced': 1,
                'fast': 2
            }
            
            if mode in mode_map:
                mode_num = mode_map[mode]
                success = self.light_meter.light_sensor.set_response_mode(mode_num)
                
                if success:
                    response = self._json_response({
                        "message": f"Response mode set to {mode}",
                        "mode": mode,
                        "description": {
                            "stable": "Full filtering - slow but smooth",
                            "balanced": "Medium filtering - good balance (default)",
                            "fast": "Minimal filtering - fast but noisier"
                        }[mode]
                    })
                else:
                    response = self._json_response({
                        "error": f"Failed to set response mode to {mode}"
                    }, 400)
            else:
                response = self._json_response({
                    "error": "mode required: 'stable', 'balanced', or 'fast'"
                }, 400)
            
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to set response mode: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_calibrate(self, conn, params):
        """Handle /meter/calibrate endpoint - set calibration."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            method = params.get('method', '').lower()
            
            if method == 'absolute':
                iso_p = params.get('iso_p', '')
                if not iso_p:
                    response = self._json_response({
                        "error": "iso_p parameter required for absolute calibration"
                    }, 400)
                    await self._sendall(conn, response)
                    return
                
                result = self.light_meter.calibrate_absolute(float(iso_p))
                
            elif method == 'perfect':
                lux = params.get('lux', '')
                time_val = params.get('time', '')
                
                if not lux or not time_val:
                    response = self._json_response({
                        "error": "lux and time parameters required for perfect print calibration"
                    }, 400)
                    await self._sendall(conn, response)
                    return
                
                result = self.light_meter.calibrate_perfect_print(float(lux), float(time_val))
                
            else:
                response = self._json_response({
                    "error": "method must be 'absolute' or 'perfect'"
                }, 400)
                await self._sendall(conn, response)
                return
            
            response = self._json_response(result)
            await self._sendall(conn, response)
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameter value: {e}"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to calibrate: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_profiles(self, conn, params):
        """Handle /meter/profiles endpoint - list all paper profiles."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            result = self.light_meter.get_profiles()
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to get profiles: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_profile(self, conn, params):
        """Handle /meter/profile endpoint - get or set specific profile."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            name = params.get('name', '')
            
            if not name:
                response = self._json_response({
                    "error": "name parameter required"
                }, 400)
                await self._sendall(conn, response)
                return
            
            # Check if setting current profile
            set_current = params.get('set', '').lower() in ('true', '1')
            
            if set_current:
                result = self.light_meter.set_current_profile(name)
            else:
                result = self.light_meter.get_profile(name)
            
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to handle profile: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_clear(self, conn, params):
        """Handle /meter/clear endpoint - clear readings."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            reading_type = params.get('type', 'all').lower()
            
            if reading_type not in ('shadow', 'highlight', 'all'):
                response = self._json_response({
                    "error": "type must be 'shadow', 'highlight', or 'all'"
                }, 400)
                await self._sendall(conn, response)
                return
            
            result = self.light_meter.clear_readings(reading_type)
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to clear readings: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_settings(self, conn, params):
        """Handle /meter/settings endpoint - get or set meter settings."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            # Check if setting values
            flare = params.get('flare', '')
            enlarger = params.get('enlarger', '')
            
            if flare or enlarger:
                flare_val = float(flare) if flare else None
                result = self.light_meter.set_settings(flare=flare_val, enlarger=enlarger or None)
            else:
                result = self.light_meter.get_settings()
            
            response = self._json_response(result)
            await self._sendall(conn, response)
        except ValueError as e:
            response = self._json_response({
                "error": f"Invalid parameter value: {e}"
            }, 400)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to handle settings: {e}"
            }, 500)
            await self._sendall(conn, response)
    
    async def _handle_meter_status(self, conn, params):
        """Handle /meter/status endpoint - get complete meter status."""
        if not self.light_meter:
            response = self._json_response({
                "error": "Light meter not configured"
            }, 400)
            await self._sendall(conn, response)
            return
        
        try:
            result = self.light_meter.get_status()
            response = self._json_response(result)
            await self._sendall(conn, response)
        except Exception as e:
            response = self._json_response({
                "error": f"Failed to get status: {e}"
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
            # Light meter endpoints
            elif path == '/meter/read':
                await self._handle_meter_read(conn, params)
            elif path == '/meter/add-reading':
                await self._handle_meter_add_reading(conn, params)
            elif path == '/meter/get-average':
                await self._handle_meter_get_average(conn, params)
            elif path == '/meter/capture':
                await self._handle_meter_capture(conn, params)
            elif path == '/meter/calculate':
                await self._handle_meter_calculate(conn, params)
            elif path == '/meter/gain':
                await self._handle_meter_gain(conn, params)
            elif path == '/meter/response-mode':
                await self._handle_meter_response_mode(conn, params)
            elif path == '/meter/calibrate':
                await self._handle_meter_calibrate(conn, params)
            elif path == '/meter/profiles':
                await self._handle_meter_profiles(conn, params)
            elif path == '/meter/profile':
                await self._handle_meter_profile(conn, params)
            elif path == '/meter/clear':
                await self._handle_meter_clear(conn, params)
            elif path == '/meter/settings':
                await self._handle_meter_settings(conn, params)
            elif path == '/meter/status':
                await self._handle_meter_status(conn, params)
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
