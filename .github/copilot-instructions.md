# Darkroom Timer - Raspberry Pi Pico 2 W

> **Project**: Professional darkroom timer with split-grade exposure calculation, chemical management, and relay control.  
> **Hardware**: Raspberry Pi Pico 2 W | **Runtime**: MicroPython v1.27.0  
> **Branch**: `Back_Up` | **Repository**: `atriantas/enlarger_server`

## System Architecture

**Full Stack**: Pico 2 W hosts async HTTP server + GPIO relay control + temp/light sensing. Single-page HTML/JS client provides multi-tab UI for timer, Heiland-inspired split-grade calculations, relay control, and logging.

```
┌─ Pico 2 W (192.168.4.1:80 or darkroom.local) ──┐
│  boot.py (async event loop)                     │
│  ├─ HTTPServer (socket-based, CORS)             │
│  │   ├─ /light-meter-split-grade-heiland        │
│  │   │   (dynamic filter selection by ΔEV)      │
│  │   └─ 20+ endpoints (relay, timer, temp, etc) │
│  ├─ GPIOControl (4 relays: GP14-17, active-LOW) │
│  ├─ TimerManager (scheduled, sync'd timers)     │
│  ├─ TemperatureSensor (DS1820 on GP18)          │
│  ├─ LightMeter (TSL2591X I²C GP0/1)             │
│  ├─ WiFiAP (192.168.4.1, SSID: DarkroomTimer)   │
│  └─ WiFiSTA (saves to wifi_config.json)         │
└──────────────────────────────────────────────────┘
         ▲ HTTP/JSON ▲ Async await on response
         │            │
   ┌─────▼────────────▼─────┐
   │  Browser/Mobile Client  │
   │  index.html (~610KB)    │
   │  • 8 tabs (CALC, SPLIT, │
   │    CHART, FSTOP, TIMER, │
   │    RELAY, CHEMICAL, etc)│
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
5. **Active-LOW Hardware**: `GPIO.value(0)` = Relay ON, `GPIO.value(1)` = Relay OFF.
6. **Heiland-Inspired Split-Grade**: Dynamic filter selection based on measured contrast (ΔEV), not fixed filter pairs.

## Essential Files

| File                       | Purpose                    | Key Details                                        |
| -------------------------- | -------------------------- | -------------------------------------------------- |
| boot.py                    | Main entry point           | Async event loop, WiFi dual-mode, init order       |
| lib/gpio_control.py        | Relay control              | Active-LOW (0=ON, 1=OFF), pins GP14-17             |
| lib/http_server.py         | REST API server            | Socket-based, CORS, 512-byte chunks, 20+ endpoints |
| lib/timer_manager.py       | Async timer orchestration  | Scheduled start w/ `start_at` sync                 |
| lib/temperature_sensor.py  | DS1820 temp sensor         | 750ms conversion, async read                       |
| lib/light_sensor.py        | TSL2591X light meter       | I²C lux sensor, exposure calc (legacy)             |
| lib/splitgrade_enhanced.py | **Heiland-like algorithm** | Dynamic filter selection, ΔEV-based                |
| lib/paper_database.py      | **Paper/filter database**  | Ilford/FOMA papers, ISO R, gamma, filter factors   |
| lib/wifi_ap.py             | WiFi hotspot               | SSID: DarkroomTimer, 192.168.4.1:80                |
| lib/wifi_sta.py            | WiFi router                | Credentials in wifi_config.json                    |
| index.html                 | Client SPA                 | 8 tabs, single appState store                      |

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

**Core Functionality**:

- `GET /ping` - Connection test
- `GET /relay?gpio=14&state=on` - Control relay
- `GET /timer?gpio=14&duration=10.5` - Timed activation (returns start_at)
- `GET /status` - All relay states + active timers
- `GET /temperature` - Current temperature

**Light Meter & Split-Grade** (TSL2591X on I²C GP0/1):

- `GET /light-meter?samples=5` - Lux measurement
- `GET /light-meter-highlight` - Store highlight reading
- `GET /light-meter-shadow` - Store shadow reading
- `GET /light-meter-contrast` - Calculate ΔEV from stored readings
- `GET /light-meter-split-grade` - **Legacy** fixed-filter algorithm (00 & 5)
- `GET /light-meter-split-grade-heiland` - **Enhanced** dynamic filter selection (ΔEV-based)
  - Params: `paper_id` (e.g., `ilford_mg_iv`, `foma_fomaspeed`)
  - Returns: `soft_filter`, `hard_filter`, `soft_time`, `hard_time`, `delta_ev`, `optimization_note`
- `GET /light-meter-calibrate?calibration=1000` - Set calibration constant

**WiFi Management**:

- `GET /wifi-status` - Current WiFi state
- `POST /wifi-config` - Save STA credentials
- `GET /wifi-ap-force` - Force AP-only mode
- `GET /wifi-clear` - Clear saved credentials

## Split-Grade Algorithm Evolution

### Legacy Algorithm (lib/light_sensor.py)

- Fixed filter pairs: Ilford 00 & 5, FOMA 2xY & 2xM2
- Linear exposure model: `time = calibration / lux × filter_factor`
- **Limitation**: Unrealistic exposures for non-extreme contrast ranges

### Heiland-Inspired Algorithm (lib/splitgrade_enhanced.py)

- **Dynamic filter selection** based on measured ΔEV (contrast range):
  ```python
  ΔEV = abs(log₂(shadow_lux / highlight_lux))
  ```
- **Filter selection logic** (Ilford example):
  - ΔEV < 1.0 → filters 1 & 2 (very low contrast)
  - ΔEV 1.5-2.0 → filters 00 & 3 (medium-low)
  - ΔEV 2.5-3.0 → filters 00 & 4 (medium-high)
  - ΔEV > 3.0 → filters 00 & 5 (high contrast)
- **Paper database integration**: Uses ISO R values, gamma, filter factors from manufacturer data
- **Optimization**: Balances soft/hard exposure times to minimize tonal placement error

### Paper Database Structure (lib/paper_database.py)

```python
PAPER_DATABASE = {
    'ilford_mg_iv': {
        'manufacturer': 'Ilford',
        'base_iso_p': 500,  # Speed without filter
        'dmin': 0.06, 'dmax': 2.15,
        'filters': {
            '00': {'factor': 2.5, 'iso_r': 180, 'gamma': 0.45, ...},
            '5': {'factor': 3.0, 'iso_r': 40, 'gamma': 1.2, ...},
            # ... grades 0-4
        }
    },
    'foma_fomaspeed': { ... }  # FOMA Variant system
}
```

**Key Functions**:

- `get_filter_selection(delta_ev, system='ilford')` - Returns optimal filter pair for ΔEV
- `get_paper_data(paper_id)` - Returns full paper characteristics
- `validate_exposure_times(soft_time, hard_time)` - Checks min/max practical limits

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

TSL2591X on I²C GP0/1. Calibration: `calibration_constant = measured_lux × correct_time`.

**Workflow**:

1. Measure highlight area → `/light-meter-highlight`
2. Measure shadow area → `/light-meter-shadow`
3. Calculate split-grade → `/light-meter-split-grade-heiland?paper_id=ilford_mg_iv`
4. Server returns: `{soft_filter, hard_filter, soft_time, hard_time, delta_ev}`

**Split-Grade Exposure**:

1. Expose with **soft filter** for `soft_time` (controls highlights)
2. Expose with **hard filter** for `hard_time` (controls shadows)
3. Filters chosen dynamically based on scene contrast (ΔEV)

## Development Workflow

### Testing Split-Grade Algorithm (Without Hardware)

```bash
# Run standalone tests with sample data
python3 test_heiland_algorithm.py
python3 test_split_grade.py
python3 test_full_implementation.py
```

These simulate the algorithm with various contrast scenarios without requiring Pico hardware.

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

1. Add async handler in `HTTPServer` class (e.g., `async def _handle_new_endpoint(self, conn, params)`)
2. Add route check in `_handle_request()` with path matching
3. Parse params with `_parse_query_string()` (custom - no urllib.parse)
4. Return JSON via `_json_response(data, status=200)`
5. Include `_cors_headers()` in response

**Example Pattern** (from lib/http_server.py:880):

```python
async def _handle_light_meter_split_grade_heiland(self, conn, params):
    paper_id = params.get('paper_id', ['ilford_mg_iv'])[0]
    result = calculate_split_grade_enhanced(
        self.light_meter.highlight_lux,
        self.light_meter.shadow_lux,
        paper_id=paper_id,
        calibration=self.light_meter.calibration
    )
    conn.send(self._json_response(result))
```

### Modifying Paper Database

Edit `lib/paper_database.py`:

- Add new paper entry to `PAPER_DATABASE` dict
- Include: `manufacturer`, `base_iso_p`, `dmin`, `dmax`, `filters`
- Each filter needs: `factor`, `iso_r`, `gamma`, `contrast_index`
- Update `FILTER_SELECTION_ILFORD` or `FILTER_SELECTION_FOMA` for dynamic selection logic
- Reference manufacturer docs in comments (see existing `[cite: XXX]` format)

### Testing Workflow

1. **Algorithm changes**: Test with `test_heiland_algorithm.py` (no hardware)
2. **Integration**: Test with `test_full_implementation.py` (imports real modules)
3. **Deployment**: Upload to Pico, test via curl/browser
4. **Validation**: Check console output for errors, verify exposures are realistic (2-30s range)

### Adding Relay Pin

Update `RELAY_PINS` dict in gpio_control.py. Active-LOW required.

### Changing WiFi Defaults

Edit wifi_ap.py: SSID, password, channel.

## Troubleshooting

| Issue                         | Solution                                                   |
| ----------------------------- | ---------------------------------------------------------- |
| Pico won't boot               | Reflash MicroPython UF2, check console                     |
| WiFi not visible              | Verify MicroPython v1.27.0+, check AP logs                 |
| HTML slow/timeout             | Normal - 610KB file, 512-byte chunks; wait 10-15s          |
| Relay stuck ON                | Check active-LOW: value(0)=ON                              |
| OSError EAGAIN                | Socket buffer full; retry with asyncio.sleep_ms(10)        |
| Memory errors                 | Increase gc.collect() frequency                            |
| Timer desync                  | Client must use server `start_at`                          |
| Unrealistic split-grade times | Use Heiland endpoint, check paper_id, verify calibration   |
| Filter selection wrong        | Check ΔEV calculation, verify paper database filter ranges |

## Documentation & Research

**Plans Directory** (`/plans`): Contains comprehensive research and implementation docs:

- `final_splitgrade_research_summary.md` - Overview of Heiland methodology vs. current impl
- `heiland_splitgrade_research.md` - Detailed Heiland algorithm research
- `splitgrade_comparison_analysis.md` - Algorithm comparison & gap analysis
- `manufacturer_data_research_plan.md` - Ilford/FOMA data extraction plan
- Other planning docs for UI transformation & implementation strategies

**Key Insights**:

- Current `lib/light_sensor.py` uses fixed filters (unrealistic for most contrasts)
- Enhanced `lib/splitgrade_enhanced.py` implements dynamic filter selection
- Paper database sourced from manufacturer PDFs (see `[cite: XXX]` references)
- ΔEV-based filter selection mimics Heiland Splitgrade Controller behavior

## Client-Side Architecture

**Key Classes**: StorageManager, SettingsManager, Timer, ChemicalManager, ExposureLogManager, RelayManager, FStopTestStripGenerator, SplitGradeCalculator.

**State Management**: All state in `appState` object. Read from appState, write via managers.

**API Integration**: Fetch to `/` endpoints. Server returns `start_at` for sync.

**UI**: 8 tabs (CALC, SPLIT, CHART, FSTOP-TEST, TIMER, RELAY, CHEMICAL, LOGS, SETTINGS). Single-page app with collapsible menu.

---

**Last Updated**: 2026-02-01 | MicroPython v1.27.0
