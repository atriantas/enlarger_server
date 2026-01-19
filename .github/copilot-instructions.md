# Darkroom Timer - Raspberry Pi Pico 2 W

> **Project**: Professional darkroom timer running on Raspberry Pi Pico 2 W with MicroPython v1.27.0.  
> **Branch**: `Back_Up` | **Repository**: `atriantas/enlarger_server`

## Architecture Overview

```
Phone/Tablet Browser ──WiFi Hotspot──► Pico 2 W (192.168.4.1:80)
     │                                      │
     │ HTTP Requests                        ├── boot.py (entry point, async loop)
     │                                      ├── lib/http_server.py (socket HTTP)
     ▼                                      ├── lib/gpio_control.py (relay control)
 index.html                                 ├── lib/timer_manager.py (async timers)
 (web client)                               ├── lib/wifi_ap.py (hotspot)
                                            └── lib/wifi_sta.py (router connection)
```

## Essential Files

| File                                         | Purpose           | Key Details                                            |
| -------------------------------------------- | ----------------- | ------------------------------------------------------ |
| [boot.py](boot.py)                           | Main entry point  | Async event loop, WiFi setup, component initialization |
| [lib/gpio_control.py](lib/gpio_control.py)   | Relay control     | Active-LOW logic, pins GP14-17                         |
| [lib/http_server.py](lib/http_server.py)     | HTTP server       | Socket-based, CORS, 512-byte chunked file serving      |
| [lib/timer_manager.py](lib/timer_manager.py) | Timer management  | Async non-blocking, scheduled start for sync           |
| [lib/wifi_ap.py](lib/wifi_ap.py)             | WiFi hotspot      | SSID: DarkroomTimer, IP: 192.168.4.1                   |
| [lib/wifi_sta.py](lib/wifi_sta.py)           | Router connection | Saves credentials to wifi_config.json                  |
| [index.html](index.html)                     | Web client        | Single-file app with all UI/logic (~610KB)             |

## GPIO Pin Mapping (Active-LOW)

```python
# lib/gpio_control.py - Pin.value(0) = ON, Pin.value(1) = OFF
RELAY_PINS = {
    14: "Enlarger Timer",  # Primary exposure relay
    15: "Safelight",       # Auto-off during exposure
    16: "Ventilation",
    17: "White Light"
}
```

## API Endpoints

```bash
GET /ping                          # Connection test
GET /relay?gpio=14&state=on        # Control relay (on/off)
GET /timer?gpio=14&duration=10.5   # Timed activation (returns start_at for sync)
GET /status                        # All relay states
GET /all?state=off                 # Control all relays
GET /wifi-config?ssid=X&password=Y # Configure WiFi
GET /wifi-status                   # WiFi connection status
```

## Critical Patterns

### 1. Timer Synchronization

Server returns `start_at` timestamp (current + 150ms) so client countdown starts synchronized:

```python
# lib/timer_manager.py
def calculate_start_at(self):
    return time.ticks_add(self.get_current_time_ms(), SYNC_DELAY_MS)  # 150ms
```

### 2. MicroPython Constraints

- **No urllib.parse** - use `_url_decode()` in http_server.py
- **Memory management** - 512-byte chunks for large files, `gc.collect()` periodically
- **Non-blocking sockets** - `OSError` when no data (not None); EAGAIN (errno 11) requires retry with `asyncio.sleep_ms(10)`
- **Async only** - use `asyncio.create_task()`, never threading
- **Socket buffer limits** - use `_sendall()` with retry logic for large responses
- **Error handling** - Always wrap socket operations in try/except for OSError

### 3. WiFi Dual-Mode Boot Sequence

```
1. Start AP immediately (fallback access)
2. Try saved credentials (STA mode)
3. If STA succeeds: wait 5s grace period, then disable AP
4. If STA fails: keep AP running
```

### 4. mDNS Setup (Critical Order)

```python
# boot.py - Must set hostname BEFORE creating WLAN interfaces
import network
network.hostname("darkroom")  # Accessible as darkroom.local
```

## Development Workflow

### Deploy to Pico 2 W

```bash
# Using ampy (macOS: /dev/tty.usbmodem*)
pip3 install adafruit-ampy
export AMPY_PORT=/dev/tty.usbmodem1101

ampy put boot.py
ampy put index.html
ampy mkdir lib
ampy put lib/gpio_control.py lib/gpio_control.py
ampy put lib/http_server.py lib/http_server.py
ampy put lib/timer_manager.py lib/timer_manager.py
ampy put lib/wifi_ap.py lib/wifi_ap.py
ampy put lib/wifi_sta.py lib/wifi_sta.py
```

### Monitor Console

```bash
screen /dev/tty.usbmodem1101 115200
# Look for: "✅ SYSTEM READY" with WiFi credentials
```

### Test Connection

```bash
# Connect to DarkroomTimer WiFi (password: darkroom123)
curl http://192.168.4.1/ping
curl "http://192.168.4.1/timer?gpio=14&duration=5.0"
```

## Common Modifications

### Adding New Endpoint

1. Add async handler method to `HTTPServer` class in [lib/http_server.py](lib/http_server.py)
2. Add route in `_handle_request()` method
3. Use `_json_response()` or `_sendall()` for responses
4. Always include CORS headers via `_cors_headers()`
5. Handle query params with `_parse_query_string()` (no urllib available)

### Changing Default WiFi

Edit [lib/wifi_ap.py](lib/wifi_ap.py) constants:

```python
DEFAULT_SSID = "DarkroomTimer"
DEFAULT_PASSWORD = "darkroom123"  # Min 8 chars
DEFAULT_CHANNEL = 6  # 1-11
```

### Modifying Relay Pins

Update `RELAY_PINS` dict in [lib/gpio_control.py](lib/gpio_control.py). Remember active-LOW: `Pin.value(0)` = ON

### WiFi Config Persistence

Credentials saved to `wifi_config.json` at root:

```python
{"ssid": "MyNetwork", "password": "mypassword"}
```

Delete this file to reset WiFi or redeploy with different settings

## Troubleshooting

| Issue                  | Solution                                                             |
| ---------------------- | -------------------------------------------------------------------- |
| Pico won't boot        | Reflash MicroPython UF2, check `screen` for errors                   |
| WiFi not visible       | Verify MicroPython v1.27.0+, check AP initialization logs            |
| HTML page slow/timeout | Normal - ~610KB file, uses 512-byte chunks; wait 10-15 seconds       |
| mDNS not working       | Ensure `network.hostname()` called before WLAN activation            |
| Relay stuck ON         | Check active-LOW logic: `value(0)`=ON, `value(1)`=OFF                |
| OSError EAGAIN (11)    | Socket buffer full; use retry loop with `asyncio.sleep_ms(10)`       |
| Memory errors          | Increase `gc.collect()` frequency, reduce chunk sizes                |
| Timer desync           | Client must respect `start_at` timestamp in response (not immediate) |
| WiFi not visible       | Verify MicroPython v1.27.0+, check AP initialization logs            |
| HTML page slow         | Normal - ~610KB file, uses 512-byte chunks                           |
| mDNS not working       | Ensure `network.hostname()` called before WLAN activation            |
| Relay stuck            | Check active-LOW logic: value(0)=ON, value(1)=OFF                    |
