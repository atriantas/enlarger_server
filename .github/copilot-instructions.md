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

| File                                                         | Purpose           | Key Details                                            |
| ------------------------------------------------------------ | ----------------- | ------------------------------------------------------ |
| [boot.py](RaspberryPiPico/boot.py)                           | Main entry point  | Async event loop, WiFi setup, component initialization |
| [lib/gpio_control.py](RaspberryPiPico/lib/gpio_control.py)   | Relay control     | Active-LOW logic, pins GP14-17                         |
| [lib/http_server.py](RaspberryPiPico/lib/http_server.py)     | HTTP server       | Socket-based, CORS, 512-byte chunked file serving      |
| [lib/timer_manager.py](RaspberryPiPico/lib/timer_manager.py) | Timer management  | Async non-blocking, scheduled start for sync           |
| [lib/wifi_ap.py](RaspberryPiPico/lib/wifi_ap.py)             | WiFi hotspot      | SSID: DarkroomTimer, IP: 192.168.4.1                   |
| [lib/wifi_sta.py](RaspberryPiPico/lib/wifi_sta.py)           | Router connection | Saves credentials to wifi_config.json                  |
| [index.html](RaspberryPiPico/index.html)                     | Web client        | Single-file app with all UI/logic                      |

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
- **Non-blocking sockets** - `OSError` when no data (not None)
- **Async only** - use `asyncio.create_task()`, never threading

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

ampy put RaspberryPiPico/boot.py boot.py
ampy put RaspberryPiPico/index.html index.html
ampy mkdir lib
ampy put RaspberryPiPico/lib/gpio_control.py lib/gpio_control.py
ampy put RaspberryPiPico/lib/http_server.py lib/http_server.py
ampy put RaspberryPiPico/lib/timer_manager.py lib/timer_manager.py
ampy put RaspberryPiPico/lib/wifi_ap.py lib/wifi_ap.py
ampy put RaspberryPiPico/lib/wifi_sta.py lib/wifi_sta.py
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

1. Add handler method to `HTTPServer` class in [lib/http_server.py](RaspberryPiPico/lib/http_server.py)
2. Add route in `_handle_request()` method
3. Include CORS headers in response

### Changing Default WiFi

Edit [boot.py](RaspberryPiPico/boot.py) or [lib/wifi_ap.py](RaspberryPiPico/lib/wifi_ap.py):

```python
DEFAULT_SSID = "DarkroomTimer"
DEFAULT_PASSWORD = "darkroom123"
```

### Modifying Relay Pins

Update `RELAY_PINS` dict in [lib/gpio_control.py](RaspberryPiPico/lib/gpio_control.py)

## Troubleshooting

| Issue            | Solution                                                  |
| ---------------- | --------------------------------------------------------- |
| Pico won't boot  | Reflash MicroPython UF2, check `screen` for errors        |
| WiFi not visible | Verify MicroPython v1.27.0+, check AP initialization logs |
| HTML page slow   | Normal - ~610KB file, uses 512-byte chunks                |
| mDNS not working | Ensure `network.hostname()` called before WLAN activation |
| Relay stuck      | Check active-LOW logic: value(0)=ON, value(1)=OFF         |
