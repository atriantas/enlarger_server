# Darkroom Timer - Raspberry Pi Pico 2 W

> **Project**: Professional darkroom timer with chemical management, exposure calculation, and relay control.  
> **Hardware**: Raspberry Pi Pico 2 W | **Runtime**: MicroPython v1.27.0  
> **Branch**: `Back_Up` | **Repository**: `atriantas/enlarger_server`

## System Architecture

**Full Stack**: Pico 2 W hosts async HTTP server + GPIO relay control + temp sensing. Single-page HTML/JS client provides multi-tab UI for timer, calculations, relay control, and logging.

```
┌─ Pico 2 W (192.168.4.1:80 or darkroom.local) ──┐
│  boot.py (async event loop)                     │
│  ├─ HTTPServer (socket-based, CORS)             │
│  ├─ GPIOControl (4 relays: GP14-17, active-LOW) │
│  ├─ TimerManager (scheduled, sync'd timers)    │
│  ├─ TemperatureSensor (DS1820 on GP18)         │
│  ├─ WiFiAP (192.168.4.1, SSID: DarkroomTimer)  │
│  └─ WiFiSTA (saves to wifi_config.json)        │
└─────────────────────────────────────────────────┘
         ▲ HTTP/JSON ▲ Async await on response
         │            │
   ┌─────▼────────────▼─────┐
   │  Browser/Mobile Client  │
   │  index.html (~610KB)    │
   │  • 8 tabs (CALC, SPLIT, │
   │    TIMER, RELAY, etc)   │
   │  • Drift-corrected UI   │
   │    timers, full app     │
   │    state in appState    │
   └────────────────────────┘
```

### Key Architecture Decisions

1. **Async-First Design**: All I/O uses `asyncio` to prevent blocking.
2. **Memory Optimization**: HTML served in 512-byte chunks, `gc.collect()` in loops, no urllib.parse.
3. **WiFi Dual-Mode**: AP starts immediately for instant access; STA attempts connection with 5s timeout.
4. **Timer Synchronization**: Server returns `start_at` timestamp (150ms future); client uses as countdown origin.
5. **Active-LOW Hardware**: GPIO.value(0) = Relay ON, GPIO.value(1) = Relay OFF.

## Essential Files

| File | Purpose | Key Details |
|------|---------|-------------|
| boot.py | Main entry point | Async event loop, WiFi dual-mode, init order |
| lib/gpio_control.py | Relay control | Active-LOW (0=ON, 1=OFF), pins GP14-17 |
| lib/http_server.py | REST API server | Socket-based, CORS, 512-byte chunks |
| lib/timer_manager.py | Async timer orchestration | Scheduled start w/ `start_at` sync |
| lib/temperature_sensor.py | DS1820 temp sensor | 750ms conversion, async read |
| lib/light_sensor.py | TSL2591X light meter | I²C lux sensor, exposure calc |
| lib/wifi_ap.py | WiFi hotspot | SSID: DarkroomTimer, 192.168.4.1:80 |
| lib/wifi_sta.py | WiFi router | Credentials in wifi_config.json |
| index.html | Client SPA | 8 tabs, single appState store |

### File Initialization Order (Critical)

1. GPIOControl (safety)
2. TemperatureSensor (optional)
3. LightSensor (optional)
4. TimerManager
5. WiFiAP (immediate access)
6. WiFiSTA (persistent)
7. HTTPServer (last)

## GPIO Pin Mapping (Active-LOW)

```python
RELAY_PINS = {
    14: "Enlarger Timer",
    15: "Safelight",
    16: "Heating Element",
    17: "White Light"
}
```

**I²C**: SDA GP0, SCL GP1 (TSL2591X)  
**1-Wire**: Data GP18 (DS1820, 4.7kΩ pull-up)

## API Endpoints

- `GET /ping` - Connection test
- `GET /relay?gpio=14&state=on` - Control relay
- `GET /timer?gpio=14&duration=10.5` - Timed activation (returns start_at)
- `GET /status` - All relay states + active timers
- `GET /temperature` - Current temperature
- `GET /light-meter?samples=5` - Lux measurement
- WiFi config, heating control, split-grade calc endpoints available

## Critical Patterns & Constraints

### Timer Synchronization
Server calculates `start_at` (current + 150ms); client uses as countdown origin to compensate for latency.

### MicroPython v1.27.0 Constraints
- No urllib.parse - custom URL decoding
- Memory: ~200KB free; use 512-byte chunks, `gc.collect()` in loops
- Async mandatory: `asyncio.create_task()`, never `time.sleep()`
- Active-LOW: `Pin.value(0)` = ON
- Error handling: Wrap socket ops in try/except

### WiFi Dual-Mode Failover
AP first (instant access), then try STA (5s timeout). mDNS hostname set BEFORE WLAN init.

### Browser State Management
Single source of truth: `appState` object. All settings via managers (StorageManager, SettingsManager).

### Light Meter Integration
TSL2591X on I²C GP0/1. Calibration: `calibration_constant = measured_lux × correct_time`. Split-grade: soft (highlights) + hard (shadows).

## Development Workflow

### Deploy to Pico
```bash
pip3 install adafruit-ampy
export AMPY_PORT=/dev/tty.usbmodem1101
ampy put boot.py
ampy put index.html
ampy mkdir lib
ampy put lib/*.py lib/
```

### Monitor Console
```bash
screen /dev/tty.usbmodem1101 115200
```

### Test Connection
```bash
curl http://192.168.4.1/ping
curl "http://192.168.4.1/timer?gpio=14&duration=5.0"
```

## Common Modifications

### Adding HTTP Endpoint
1. Add async handler in `HTTPServer` class
2. Add route check in `_handle_request()`
3. Parse params with `_parse_query_string()`
4. Return JSON via `_json_response()`
5. Include `_cors_headers()`

### Adding Relay Pin
Update `RELAY_PINS` dict in gpio_control.py. Active-LOW required.

### Changing WiFi Defaults
Edit wifi_ap.py: SSID, password, channel.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pico won't boot | Reflash MicroPython UF2, check console |
| WiFi not visible | Verify MicroPython v1.27.0+, check AP logs |
| HTML slow/timeout | Normal - 610KB file, 512-byte chunks; wait 10-15s |
| Relay stuck ON | Check active-LOW: value(0)=ON |
| OSError EAGAIN | Socket buffer full; retry with asyncio.sleep_ms(10) |
| Memory errors | Increase gc.collect() frequency |
| Timer desync | Client must use server `start_at` |

## Client-Side Architecture

**Key Classes**: StorageManager, SettingsManager, Timer, ChemicalManager, ExposureLogManager, RelayManager, FStopTestStripGenerator, SplitGradeCalculator.

**State Management**: All state in `appState` object. Read from appState, write via managers.

**API Integration**: Fetch to `/` endpoints. Server returns `start_at` for sync.

**UI**: 8 tabs (CALC, SPLIT, CHART, FSTOP-TEST, TIMER, RELAY, CHEMICAL, LOGS, SETTINGS). Single-page app with collapsible menu.

---

**Last Updated**: 2026-01-25 | MicroPython v1.27.0
