# Darkroom Timer - Raspberry Pi Pico 2 W

> **Project**: Professional darkroom timer with chemical management, exposure calculation, and relay control.  
> **Hardware**: Raspberry Pi Pico 2 W | **Runtime**: MicroPython v1.27.0  
> **Branch**: `Back_Up` | **Repository**: `atriantas/enlarger_server`

## System Architecture

**Full Stack**: Pico 2 W device hosts async HTTP server + GPIO relay control + temp sensing. Single-page HTML/JS client (610KB) provides multi-tab UI for timer, calculations, relay control, and logging.

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

## Essential Files

| File                                                   | Purpose                   | Key Details                                                          |
| ------------------------------------------------------ | ------------------------- | -------------------------------------------------------------------- |
| [boot.py](boot.py)                                     | Main entry point          | Async event loop, WiFi dual-mode (AP+STA), init order                |
| [lib/gpio_control.py](lib/gpio_control.py)             | Relay control             | Active-LOW (0=ON, 1=OFF), pins GP14-17                               |
| [lib/http_server.py](lib/http_server.py)               | REST API server           | Socket-based, CORS, 512-byte chunks for large files                  |
| [lib/timer_manager.py](lib/timer_manager.py)           | Async timer orchestration | Scheduled start w/ `start_at` sync, heating control                  |
| [lib/temperature_sensor.py](lib/temperature_sensor.py) | DS1820 1-Wire temp        | 750ms conversion, async read loop, caching                           |
| [lib/wifi_ap.py](lib/wifi_ap.py)                       | WiFi hotspot (fallback)   | SSID: DarkroomTimer, 192.168.4.1:80                                  |
| [lib/wifi_sta.py](lib/wifi_sta.py)                     | WiFi router (primary)     | Credentials in wifi_config.json, mDNS: darkroom.local                |
| [index.html](index.html)                               | Client SPA (all features) | 8 tabs, ~130KB CSS/JS, single appState store, drift-corrected timers |

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

## Critical Patterns & Constraints

### 1. Timer Synchronization (Device ↔ Browser)

**Problem**: Network latency causes client/server timer desync.  
**Solution**: Server returns `start_at` timestamp (150ms future), client uses this as countdown origin.

```python
# lib/timer_manager.py - calculate_start_at() returns synchronized start
def calculate_start_at(self):
    return time.ticks_add(self.get_current_time_ms(), SYNC_DELAY_MS)  # 150ms compensation

# Browser receives: {"relay": true, "duration": 10.0, "start_at": 12345678}
# Client ignores duration, starts countdown FROM start_at timestamp
```

**Key**: Always use server-supplied `start_at` in UI timer—never start immediately from client.

### 2. MicroPython v1.27.0 Hard Constraints

- **No urllib.parse** — write custom `_url_decode()` in http_server.py
- **Memory**: Device has ~200KB free; use 512-byte chunks for file I/O, call `gc.collect()` in loops
- **Sockets**: Non-blocking mode raises `OSError` (errno 11 = EAGAIN) when buffer full; retry with `asyncio.sleep_ms(10)`
- **Async mandatory**: Use `asyncio.create_task()`, `asyncio.sleep_ms()`, never `time.sleep()` or threading
- **Pin operations**: Active-LOW is hardware pattern here—`Pin.value(0) = ON`, `Pin.value(1) = OFF`
- **Error handling**: Always wrap socket ops in try/except for OSError; timeout via `socket.settimeout()`

### 3. WiFi Dual-Mode Failover (boot.py)

Order matters—AP first (immediate fallback), then try STA (persistent connection):

```
1. Set network.hostname("darkroom") BEFORE any WLAN init
2. Start WiFiAP immediately → 192.168.4.1:80 available instantly
3. Try WiFiSTA with saved credentials (5s attempt)
4. If STA succeeds: wait 5s grace, disable AP (conserve resources)
5. If STA fails: keep AP running (always reachable)
```

This ensures device is always reachable—either via hotspot or mDNS.

### 4. Browser State Management (index.html)

**Single source of truth**: `appState` object (5331-5431 in JS).  
**Pattern**: Transient UI state separate from persisted settings.

```javascript
appState = {
  ui: { activeTab, timerStatus },       // Never persisted
  calculator: { base, stop, increment }, // Runtime calc state
  timers: { active_timers: [...] },      // Ephemeral
  persistent: {
    currentProfile,                       // Via SettingsManager
    currentChemicalPreset                // Via ChemicalManager
  },
  settings: { ... }                       // Via StorageManager.saveSettings()
}
```

**Rule**: All settings writes → call `StorageManager` methods to persist.  
**Rule**: Render functions read from appState, never query DOM (single source of truth).

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

## Common Modifications & Patterns

### Adding a New HTTP Endpoint (lib/http_server.py)

1. Define async handler in `HTTPServer` class
2. Add route check in `_handle_request()` method (`if path.startswith('/your-endpoint')`)
3. Parse query params with `_parse_query_string()` (no urllib available)
4. Return JSON via `_json_response(dict, status)` or raw via `_sendall(bytes)`
5. **Always** include `_cors_headers()` in response

```python
# Example in lib/http_server.py _handle_request()
elif path.startswith('/my-endpoint'):
    params = self._parse_query_string(query_string)
    result = {"value": params.get("param", "default")}
    response = self._json_response(result)
```

### Adding New Relay Pin

1. Update `RELAY_PINS` dict in [lib/gpio_control.py](lib/gpio_control.py) (line 11-16)
2. Remember: active-LOW logic required—`Pin.value(0)` turns ON, `Pin.value(1)` turns OFF
3. No other files need changes (GPIOControl dynamically initializes all pins)

### Changing WiFi Defaults

Edit [lib/wifi_ap.py](lib/wifi_ap.py):

```python
DEFAULT_SSID = "DarkroomTimer"      # Change SSID name
DEFAULT_PASSWORD = "darkroom123"    # Min 8 chars required
DEFAULT_CHANNEL = 6                 # 1-11 valid
```

Or reset WiFi: Delete `wifi_config.json` from Pico, device falls back to AP mode.

### Temperature Sensor Integration (New Features)

[lib/temperature_sensor.py](lib/temperature_sensor.py) reads DS1820 on GP18:

```python
sensor = TemperatureSensor(pin_num=18)
# Async loop calls: await sensor.read_temperature_async()
# Result cached in sensor.last_temp (Celsius)
```

TimerManager can use for heating relay logic (GP16). Heating disabled by default—enable via heating control endpoint.

### Creating New Tab in index.html

1. Add tab dropdown item: `<button class="tab-dropdown-item" data-tab="new-id">New Tab</button>`
2. Add tab content: `<div id="new-id" class="tab-content">...</div>`
3. Tab switching automatic via event delegation in switchTab() function
4. Use existing UI components: `.incremental-timer` (panel), `.settings-btn` (button), `.shelf-life-list` (list)

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
| Temperature read fails | Check DS1820 wiring on GP18, verify 1-Wire pull-up resistor          |
| Drift in countdown     | Browser clocks may drift; rely on server `start_at` for sync         |

## Client-Side JS Architecture (index.html)

**Key Classes** (all run in browser):

- `StorageManager`: Persist settings to localStorage (keyed by STORAGE_KEYS)
- `SettingsManager`: Manage profiles, chemical presets, UI preferences
- `Timer`: Individual countdown timer (drift-corrected via DriftCorrectedTimer)
- `ChemicalManager`: Track chemical stock, shelf-life, expiration
- `ExposureLogManager`: Logging and session history
- `RelayManager`: Map relay control buttons to HTTP endpoints
- `FStopTestStripGenerator`: Calculate test strip increments
- `SplitGradeCalculator`: Soft/hard grade exposure splits

**Data Flow**: User interaction → `appState` update → API call (`fetch` to Pico) → render update

**CSS Consolidation**: Single-file approach with highly consolidated classes (`.incremental-timer`, `.settings-btn`, `.shelf-life-item`) using inline styles for variants to reduce CSS size.

## index.html - User Interface Features

The client is a full-featured single-page application with 8 tabs organized by workflow. **All state is managed in `appState` object** (never read from DOM).

### Tab Structure & Navigation

- **Collapsible menu**: Dropdown navigation (hamburger button) with active tab indicator
- **Event delegation**: Tab switching via `switchTab(tabId)` function
- **Automatic switching**: Menu closes on selection; scrolls to active tab
- **Accessibility**: Tab items have proper ARIA attributes and keyboard support

### CALC Tab - Exposure Calculator

**Purpose**: Base time + f-stop increments → precise exposure times

**Components**:

- **Base Time Slider**: 0.5-300s, primary exposure duration
- **Stop Slider**: -5 to +5 stops (0.1 increments), adjustment from base
- **Increment Selector**: 1/2, 1/3, 1/6 stops - predefined step sizes
- **Results Display**:
  - Calculated exposure time in seconds
  - Detailed f-stop breakdown
  - Timer status (ready/running/complete)

**Key Pattern**: All sliders update `appState.calculator` → triggers `renderCalculatorDisplay()` → updates DOM

**User Flow**: Set base → adjust stop value → see instant calculation → click "Start Exposure" → server syncs via `/timer` endpoint with `start_at` timestamp

### SPLIT Tab - Split-Grade Calculator

**Purpose**: Hard/soft grade exposure splits for precise contrast control

**Components**:

- **Hard Grade Input**: Selects magenta (high contrast) filter strength
- **Soft Grade Input**: Selects cyan (low contrast) filter strength
- **Hard Exposure Timer**: Duration for hard-grade phase
- **Soft Exposure Timer**: Duration for soft-grade phase
- **Total Exposure Display**: Combined duration

**Key Pattern**: Two-phase exposure management - tracks separate times for each grade, calculates split ratio

**Physics**: Hard (magenta) tightens shadows; Soft (cyan) opens highlights. Ratio determines final print contrast.

### CHART Tab - Reference Time Table

**Purpose**: Quick lookup table for exposure calculations

**Components**:

- **Incremental Time Table**: Calculates times for each increment (1/2, 1/3, 1/6 stops)
- **Base Time Control**: Same slider as CALC tab, syncs bidirectionally
- **Dynamic Rows**: Updated by `updateChart()` whenever base time changes
- **Print-Friendly**: Full table visible for darkroom notes/reference

**Implementation**: `updateChart()` recalculates all times on base slider change using `calculateTime(base, stop)` formula

### FSTOP-TEST Tab - Test Strip Generator

**Purpose**: Automated test strip creation with precise incremental steps

**Features**:

- **Method Selection**:
  - Cumulative: Each step adds time (5s + 5s + 5s = 15s total per step)
  - Incremental: Each step is independent (5s, 5s, 5s for each section)
- **Step Configuration**: Number of steps (2-12), time per step, start/stop adjustment
- **Auto-Advance**: Automatic step progression with configurable delay (0.5-10s)
- **Countdown Display**: Visual countdown for each step with audio beeps
- **Denominator Control**: Switch between 1/2, 1/3, 1/6 stop increments
- **Visual Feedback**:
  - Active step highlighting
  - Progress bar showing overall completion
  - Step preview with estimated times

**Key Class**: `FStopTestStripGenerator` - manages step logic, countdown state, auto-advance

**User Flow**: Configure steps → Start → Wait for auto-advance or manually progress → Compare strips → Use best for CALC

### TIMER Tab - Chemistry Timer Management

**Purpose**: Track chemical processing times (developer, stop, fixer, wash)

**Features**:

- **4 Independent Timers**:
  - Developer (top left)
  - Stop Bath (top right)
  - Fixer (bottom left)
  - Photo Wash/Flo (bottom right)
- **Timer Profiles**: Save/load preset time configurations
- **Default Times**: Configurable via SETTINGS tab
- **Auto-Start Chain**: Enable to auto-start next timer when current completes
- **Manual Controls**: Play/pause/stop per timer
- **Visual States**:
  - Ready: Black background, red text
  - Running: Pulsing animation
  - Warning: Last 3 seconds highlighted
  - Complete: Green background

**Relay Mapping**: Each timer controls corresponding relay (via `RelayManager`)

- Developer → GP14 (Enlarger - relay reused for chemistry control)
- Stop → GP15 (Safelight)
- Fixer → GP16 (Heating element)
- Wash → GP17 (White Light)

**Key Pattern**: `Timer` class instances for each timer; `CountdownManager` coordinates auto-start logic

### RELAY Tab - Hardware Control

**Purpose**: Manual relay switch control for all 4 outputs

**Components**:

- **Relay Grid**: 2×2 layout showing all 4 relays
- **Individual Toggles**: On/off switch for each relay
- **State Indicators**: Current state display (ON/OFF)
- **Status Feedback**: Shows relay response from server
- **Master Control**: "All On" / "All Off" buttons for bulk control

**Implementation**: `RelayManager` class handles all relay HTTP requests via `/relay?gpio=X&state=on/off`

**User Workflow**: Bypass timers for manual safelight/ventilation control during setup

### CHEMICAL Tab - Chemical Stock & Shelf-Life Tracking

**Purpose**: Monitor chemical inventory, expiration, and usage

**Features**:

- **Chemical Presets**: Predefined stocks (developer types, fixers, stop baths)
- **Custom Chemicals**: Add custom chemical entries
- **Stock Management**:
  - Name, dilution ratio, creation date
  - Shelf-life calculation (days remaining)
  - Visual warnings (expiring: orange, expired: red)
- **Usage Logging**: Track consumption per session
- **Delete/Edit**: Manage preset list

**Key Class**: `ChemicalManager` - persistence via localStorage via `StorageManager`

**Business Logic**: Shelf-life auto-calculated from creation date; color-coded warnings drive workflow decisions

### LOGS Tab - Exposure Session History

**Purpose**: Record and review all exposures and timer sessions

**Features**:

- **Auto-Logging**: Every exposure/timer session recorded with:
  - Timestamp, duration, relay used
  - Test strip results, notes
  - Environmental data (temperature, humidity if available)
- **Session History**: Scrollable list, newest first
- **Search/Filter**: Filter by relay, date range (future feature)
- **Export Data**: Copy to clipboard for external analysis (future feature)
- **CSV Format**: Ready for spreadsheet analysis

**Key Class**: `ExposureLogManager` - manages log storage, retrieval, formatting

**Developer Note**: Uses localStorage for persistence; consider IndexedDB if logs grow large

### SETTINGS Tab - System Configuration

**Purpose**: Centralized configuration for all darkroom parameters

**Sections**:

#### Sound Settings

- **Calc Warning Beep**: Audio cue 3s before exposure ends
- **Calc End Beep**: Completion confirmation for exposure
- **Timer Warning Beep**: 3s before timer ends
- **Timer End Beep**: Completion confirmation for chemistry timers
- **Volume Control**: Master volume 0-100%
- **Beep Pattern**: Selectable patterns (single, double, triple)

#### Countdown Settings

- **Countdown Delay**: 0-30 seconds (preparation window before exposure)
- **Countdown Beep**: Enable/disable countdown audio
- **Countdown Pattern**:
  - `every-second`: Beep every second
  - `last3`: Beep only final 3 seconds
  - `last5`: Beep final 5 seconds
  - `none`: Silent countdown

#### Timer Auto-Start

- **Enable Auto-Start**: Chains timers automatically (Developer → Stop → Fixer → Wash)
- **Default Times**: Pre-set times for each timer in seconds
- **Default Photo Flo**: Include wash cycle in auto-start chain

#### Test Strip Auto-Advance

- **Enable Auto-Advance**: Automatically progress test strip steps
- **Auto-Advance Delay**: 0.5-10 seconds between steps
- **Step Method**: Cumulative vs Incremental

#### Color Scheme

- **Dark Mode**: Original red-on-black scheme (default)
- **Day Mode**: Dark grey with blue accent
- **Light Mode**: White background with blue accent

**Persistence**: All settings saved to localStorage via `StorageManager.saveSettings()` on every change

**UI Pattern**: Settings use toggles (`.toggle-btn`), sliders (`.slider`), and dropdowns (`.settings-input`)

### UI Component Patterns (CSS Classes)

**Universal Components** (use these for consistency):

| Class                | Usage                                                     | Variants                           |
| -------------------- | --------------------------------------------------------- | ---------------------------------- |
| `.incremental-timer` | Container for major sections (panels, calculator, timers) | `.light`, `.dark`                  |
| `.settings-btn`      | All action buttons (start, stop, delete, save)            | `.primary` (blue), `.danger` (red) |
| `.toggle-btn`        | On/off switches, mode selectors                           | `.active` adds highlighting        |
| `.settings-input`    | Text inputs, selects, number inputs                       | All inherit border/focus styles    |
| `.shelf-life-item`   | List items (relays, presets, chemicals)                   | `.active`, `.expiring`, `.expired` |
| `.shelf-life-list`   | Container for lists                                       | 1-column vertical layout           |
| `.label-sm`          | Small informational text                                  | Standard dark/light scheme         |
| `.value-display`     | Large numeric display (times, stop values)                | Used for emphasis                  |
| `.timer-grid`        | 2×2 layout for timers                                     | Auto grid layout                   |
| `.progress-bar`      | Visual progress indicator                                 | Uses gradient background           |

**Never add new CSS classes** - use inline `style=` attributes for one-off adjustments instead

### State Management Patterns

**Reading State**:

```javascript
const currentTab = appState.ui.activeTab;
const baseTime = appState.calculator.base;
const relayStatus = appState.persistent.relayStates[14]; // GP14
```

**Writing State**:

```javascript
// Always update through managers, never direct assignment
settingsManager.setCurrentProfile(profileName); // Updates appState.persistent.currentProfile + localStorage
```

**Rendering**:

```javascript
function renderCalculatorDisplay() {
  // Read from appState
  const base = appState.calculator.base;
  const result = calculateTime(base, appState.calculator.stop);

  // Update DOM
  document.getElementById("calculatedTime").textContent =
    result.toFixed(2) + "s";
}

// Call render after state changes
appState.calculator.base = 10;
renderCalculatorDisplay();
```

### API Integration Pattern

All device communication goes through fetch to `/` endpoints:

```javascript
// Example: Start timed exposure
async function startExposure(gpio, duration) {
  try {
    const response = await fetch(`/timer?gpio=${gpio}&duration=${duration}`);
    const data = await response.json();

    // Server returns: { relay: true, duration: 10.0, start_at: 1234567890 }
    // Use start_at for client-side countdown synchronization

    const clientCountdown = new DriftCorrectedTimer(data.start_at, duration);
    clientCountdown.start();
  } catch (error) {
    console.error("Timer failed:", error);
  }
}
```

---

**Last Updated**: Project analyzed 2026-01-20 | MicroPython v1.27.0 | index.html v3.0.3
