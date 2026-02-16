# Darkroom Timer - Pico 2 W (MicroPython v1.27.0)

## Big picture
- Pico 2 W runs an asyncio socket HTTP server + GPIO relay control + timer sync + optional sensors; the UI is a single-page app in index.html.
- Boot order is intentional for safety: GPIO first, sensors, TimerManager, WiFi AP/STA, then HTTPServer in boot.py.
- HTTP server is memory-aware: CORS on all responses, chunked HTML (512 bytes), and a custom _parse_query_string (no urllib.parse) in lib/http_server.py.
- Relays are active-LOW: Pin.value(0) = ON, Pin.value(1) = OFF.

## Boot and runtime flow
- boot.py creates GPIOControl, TemperatureSensor (DS18B20), optional DarkroomLightMeter, TimerManager, WiFiAP/WiFiSTA, UpdateManager, then HTTPServer.
- AUTORUN_BLOCK_PIN is GP6; pulling to GND skips autorun for safe maintenance.
- mDNS hostname (darkroom.local) is set before any WLAN creation; do not move network.hostname().
- Main loop runs HTTPServer + TimerManager heating task via asyncio.gather.

## HTTP API and server patterns
- Routes are handled in lib/http_server.py; add endpoints by following the existing handler pattern and return _json_response with _cors_headers.
- Core endpoints: /relay, /timer, /status, /all, /ping, /wifi-config, /wifi-status, /index.html.
- /timer uses scheduled starts: TimerManager returns start_at = now + 150 ms so the client and relay begin together.
- Relay safety: turning a relay off stops any active timer for that pin.

## Client SPA (index.html)
- appState is the single source of truth; managers (SettingsManager, Timer, RelayManager, FStopTestStripGenerator, LightMeterManager) read/write it.
- All tabs (CALC, SPLIT, FSTOP-TEST, TIMER, RELAY, CHEMICAL, LOGS, SETTINGS) live in one file; shared utilities include formatStop and DriftCorrectedTimer.
- CSS is heavily consolidated to save size; prefer reusing existing utility classes over new ones.

## Sensors, algorithms, and data
- Light meter: TSL2591X on I2C GP0/1 (optional) in lib/light_sensor.py; used for exposure, contrast, and split-grade modes.
- Split-grade (enhanced): lib/splitgrade_enhanced.py computes delta_ev = abs(log2(shadow_lux / highlight_lux)) and selects filter pairs via lib/paper_database.py.
- Legacy path remains in lib/light_sensor.py with fixed filter pairs; enhanced path uses get_filter_selection and validate_exposure_times.
- Paper data lives in lib/paper_database.py; keep manufacturer [cite: ...] annotations when adding entries.
- Heating control: TimerManager polls temperature when enabled and uses hysteresis; heating relay is GP16.

## WiFi and networking
- AP starts immediately for access; STA attempts connect and disables AP on success (to avoid routing conflicts).
- Credentials persist in wifi_config.json; WiFiSTA disables power saving when available.
- AP defaults: SSID=DarkroomTimer, password=darkroom123, IP=192.168.4.1.

## Updates and versioning
- UpdateManager fetches GitHub releases and can download boot.py, index.html, and lib/*.py into place.
- Updates are chunked at 512 bytes; version is tracked in version.json.

## Hardware map
- Relays on GP14-17 (Enlarger, Safelight, Heating, White Light). I2C light meter on GP0/1, DS18B20 temp sensor on GP18.

## Dev workflows
- Local algorithm tests (no hardware): python3 test_heiland_algorithm.py, python3 test_split_grade.py, python3 test_full_implementation.py.
- Deployment: use ampy to upload boot.py, index.html, and lib/* (see README.md). HTML is large and served in chunks.

## Key files to reference
- boot.py (init order, WiFi flow, autorun block)
- lib/http_server.py (routes, chunked HTML, query parsing)
- lib/timer_manager.py (start_at sync, heating control)
- lib/gpio_control.py (active-LOW relay logic)
- lib/update_manager.py (release updates, version.json)
- lib/splitgrade_enhanced.py and lib/paper_database.py (Heiland-style split grade)
- lib/light_sensor.py (TSL2591X, legacy split-grade)
- index.html (SPA, appState, managers)
