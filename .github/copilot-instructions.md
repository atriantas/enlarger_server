# Darkroom Timer - Pico 2 W (MicroPython v1.27.0)

## Big picture
- Pico 2 W runs an asyncio HTTP server + GPIO relay control + timer sync + optional sensors; the UI is a single-page app in index.html.
- Boot sequence and wiring order matter: GPIO first (safety), sensors, TimerManager, WiFi AP/STA, then HTTPServer in boot.py.
- HTTPServer is socket-based with CORS and chunked file serving (512 bytes) to fit memory constraints.
- Relays are active-LOW: Pin.value(0) = ON, Pin.value(1) = OFF.

## Server architecture and flow
- Entry point: boot.py initializes GPIOControl, TemperatureSensor, optional DarkroomLightMeter, TimerManager, WiFiAP/WiFiSTA, UpdateManager, then HTTPServer.
- WiFi: AP starts immediately for access; STA attempts connection and disables AP on success. Credentials live in wifi_config.json.
- Timer sync: TimerManager calculates start_at (current + 150 ms) so client countdown aligns with relay start.
- HTTP endpoints are handled in lib/http_server.py using custom _parse_query_string (no urllib.parse).

## Client architecture (index.html)
- Single appState store is the source of truth; managers (SettingsManager, Timer, RelayManager, FStopTestStripGenerator, LightMeterManager) read/write appState.
- CALC, SPLIT, FSTOP-TEST, TIMER, RELAY, CHEMICAL, LOGS, SETTINGS live in one file; watch for shared utility functions (formatStop, DriftCorrectedTimer).

## App features (UI + device)
- CALC tab: f-stop exposure calculator with base time, stop increment selector, incremental exposure timer, countdown beeps, and transfer-to-timer action.
- SPLIT tab: split-grade calculator with paper/filter selection, soft/hard time computation, presets, and send-to-CALC integration.
- FSTOP-TEST tab: test strip generator (cumulative or incremental), auto-advance between steps, countdown integration, per-step relay trigger, and click-to-apply step time to CALC or SPLIT.
- TIMER tab: four process timers (Dev/Stop/Fix/Flo) with start/pause/reset, optional auto-sequencing, and relay auto-trigger support.
- RELAY tab: manual relay control, status display, WiFi connect/force AP/clear credentials, and safelight auto-off during exposures.
- CHEMICAL tab: mix calculator, chemical presets, capacity tracking by paper size, and shelf-life tracker with expiring/expired states.
- LIGHT METER tab: exposure meter mode, contrast analyzer mode, split-grade mode (Heiland path), and virtual proofing with stability gating.
- LOGS tab: session logging for CALC/TEST/SPLIT/TIMER phases with export and delete actions.
- SETTINGS tab: sound settings, countdown settings, auto-advance settings, color scheme, base-time limits, f-stop denominator, and proof stability thresholds.

## Split-grade logic
- Enhanced algorithm: lib/splitgrade_enhanced.py uses delta_ev = abs(log2(shadow_lux / highlight_lux)) and picks filter pairs via lib/paper_database.py.
- Legacy path: lib/light_sensor.py still has fixed filter pairs; enhanced path uses get_filter_selection and validate_exposure_times.
- Paper data lives in lib/paper_database.py; keep the manufacturer [cite: ...] annotations when adding new entries.

## Hardware pin map
- Relays on GP14-17 (Enlarger, Safelight, Heating, White Light). I2C light meter on GP0/1, DS18B20 temp sensor on GP18.

## Dev workflows
- Local algorithm tests (no hardware):
  - python3 test_heiland_algorithm.py
  - python3 test_split_grade.py
  - python3 test_full_implementation.py
- Deploy to Pico with ampy (see README.md); HTML is large and served in chunks.

## Project conventions
- Keep MicroPython constraints in mind: async I/O, avoid blocking sleeps in server paths, and conserve memory (gc.collect where needed).
- New HTTP endpoints should follow the existing pattern in lib/http_server.py: add handler, route match, parse params, return _json_response with _cors_headers.
- When changing relay behavior, remember active-LOW and stop any running timers for that pin when turning off.

## Key files to reference
- boot.py (init order, WiFi flow, task startup)
- lib/http_server.py (routes, chunked HTML, query parsing)
- lib/timer_manager.py (start_at sync, scheduled timers)
- lib/gpio_control.py (active-LOW relay logic)
- lib/splitgrade_enhanced.py and lib/paper_database.py (Heiland-style split grade)
- index.html (SPA, appState, managers)
