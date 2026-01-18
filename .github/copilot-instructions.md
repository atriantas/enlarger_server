# Darkroom Timer System - AI Coding Agent Instructions

> **Project Context**: Professional darkroom timer system with **dual implementations**: (1) Raspberry Pi Flask server + HTML client, (2) Raspberry Pi Pico 2 W MicroPython standalone. Current branch: `Back_Up`, Default branch: `main`. Repository: `atriantas/enlarger_server`.

## 🎯 Quick Start for AI Agents

### Essential Files - Choose Your Implementation

**Raspberry Pi (Flask) Implementation:**

- `Raspberry_Server_v3.0.3.py` - Flask server with GPIO control (~669 lines)
- `Darkroom_Tools_v3.0.3.html` - Single-file client application (~14,593 lines)

**Pico 2 W (MicroPython) Implementation:**

- `boot.py` - Main entry point with async event loop (~101 lines)
- `index.html` - Client (copy of Darkroom_Tools_v3.0.3.html with Pico defaults)
- `lib/wifi_ap.py` - WiFi hotspot management (~150 lines)
- `lib/gpio_control.py` - GPIO relay control (~159 lines)
- `lib/http_server.py` - Socket-based HTTP server (~552 lines)
- `lib/timer_manager.py` - Async timer management (~248 lines)

**Legacy/Archive:** `Raspberry_Server_3.py`, `_5.py`, `_6.py`, `_7.py` - DO NOT MODIFY

### Critical Architecture Patterns

**Raspberry Pi:** Two-component system - Flask server (REST API) + HTML client (UI + state management)

**Pico 2 W:** All-in-one system - MicroPython async server + embedded HTTP + WiFi AP + GPIO control

**Both implementations:** All photographic timing uses `Date.now()` for millisecond precision, active-LOW relay logic, identical REST API

### Immediate Productivity Checklist

- [ ] Understand the 10-manager class ecosystem (see Manager Classes section)
- [ ] Never use `setInterval` - always use `DriftCorrectedTimer`
- [ ] Always use `StorageManager` for localStorage operations
- [ ] Preserve safelight auto-off flow with immediate restoration
- [ ] Respect triple-fallback HTTP strategy (CORS → no-cors → Image)
- [ ] Use 150ms debouncing for live settings changes
- [ ] Click-to-apply test strip steps to CALC tab
- [ ] Theme-aware visual feedback for all UI elements

## 🏗️ Big Picture Architecture

### Raspberry Pi Flask Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (Single HTML File)               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   UI Layer  │  │ Manager      │  │ State Management │  │
│  │  (7 Tabs)   │  │ Classes      │  │  (appState)      │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│         │                │                     │            │
│         └────────────────┴─────────────────────┘            │
│                          │                                  │
│              HTTP Requests (Triple-Fallback)                │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ GPIO Control
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Raspberry Pi Flask Server (Port 5000)          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  REST API   │  │ GPIO Control │  │  Thread Timers   │  │
│  │  Endpoints  │  │  (Active-LOW)│  │  (Daemon)        │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│         │                │                     │            │
│         └────────────────┴─────────────────────┘            │
│                          │                                  │
│              4 Relays (GPIO 25, 17, 27, 22)                 │
└─────────────────────────────────────────────────────────────┘
```

### Pico 2 W MicroPython Implementation

```
┌─────────────────────────────────────────────────────────────┐
│            Phone/Tablet Browser (WiFi Client)               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ UI Layer    │  │ Manager      │  │ State Management │  │
│  │ (index.html)│  │ Classes      │  │  (appState)      │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│                          │                                  │
│              HTTP Requests (192.168.4.1:80)                 │
└─────────────────────────────────────────────────────────────┘
                          │
                     WiFi Hotspot
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          Raspberry Pi Pico 2 W (MicroPython)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  boot.py (Async Event Loop)                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │  │
│  │  │ WiFi AP    │  │ HTTP       │  │ GPIO Control  │  │  │
│  │  │ (wifi_ap)  │  │ (socket)   │  │ (gpio_ctrl)   │  │  │
│  │  └────────────┘  └────────────┘  └───────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Timer Manager (Async Non-Blocking)             │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│              4 Relays (GPIO 14, 15, 16, 17)                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Differences

| Aspect       | Raspberry Pi Flask | Pico 2 W MicroPython |
| ------------ | ------------------ | -------------------- |
| **Server**   | Flask (threading)  | Socket + asyncio     |
| **WiFi**     | Client on network  | Hotspot (AP mode)    |
| **GPIO**     | BCM 25,17,27,22    | GP 14,15,16,17       |
| **Timer**    | Thread-based       | Async/await          |
| **Port**     | 5000               | 80                   |
| **IP**       | Dynamic (DHCP)     | Fixed (192.168.4.1)  |
| **Shutdown** | API endpoints      | Physical button only |

### Data Flow Patterns

**Exposure Flow**:

```
User clicks Start → CountdownManager → AudioService beeps →
RelayManager.triggerTimerRelay() → Safelight check →
Server timer request → GPIO 25 active → Duration →
0.5s buffer → Safelight restoration → Completion beep
```

**Persistence Flow**:

```
UI Change → Manager Class → StorageManager →
LocalStorage (darkroom_timer_*) → appState sync →
UI Update
```

**State Management**:

```javascript
const appState = {
  ui: {
    /* transient, not persisted */
  },
  calculator: {
    /* runtime calculator state */
  },
  timers: {
    /* timer instances state */
  },
  settings: {
    /* persisted preferences */
  },
  persistent: {
    /* profiles, presets, etc. */
  },
};
```

## 🔧 Manager Class Ecosystem

**10 Critical Managers** - Understand these before any modifications:

### 1. RelayManager (lines ~8512-9320)

**Central hub for server communication**

- `sendRequest(endpoint, params)` - Triple-fallback HTTP (CORS → no-cors → Image)
- `triggerTimerRelay(duration)` - Safelight-aware exposure with 0.5s buffer
- `setRelay(relayNum, state)` - Individual relay control
- `handleSafelightAutoOff(relayNum, newState)` - Critical safelight protection
- **Critical**: Safelight auto-off with immediate restoration after exposure
- **Triple-fallback strategy**: Tries CORS mode, then no-cors, then Image object for maximum compatibility

### 2. Timer (lines ~5380-5520)

**Individual timer instances** (Dev, Stop, Fix, Flo)

- Uses `DriftCorrectedTimer` for precision
- State managed via appState.timers object
- Auto-chain via `autoStart` setting
- Warning beep at 10 seconds
- Default times from DEFAULT_TIMER_TIMES

### 3. IncrementalTimer (lines ~9925-10100)

**Dodge/burn calculator with step progression**

- Step-by-step exposure calculations
- Integrates with countdown and relay triggering
- Base time slider (0.4-50s), stop increment selector
- Auto-trigger calls `window.relayManager.triggerTimerRelay(appState.calculator.thisExposureTime)`

### 4. FStopTestStripGenerator (lines ~11834-13670)

**F-stop test strip generation**

- Cumulative vs incremental methods
- **Click-to-apply**: Click step → applies time to CALC tab's base time
- **Theme-aware**: Dynamic colors based on current theme and exposure intensity
- Auto-advance with configurable delays (150ms debouncing)
- Transfer destination: 'calc' or 'split' tab
- Profile management with save/load/delete

### 5. CountdownManager (lines ~5691-5900)

**Visual countdown before exposure**

- Configurable delay (default 5 seconds)
- Patterns: every-second, last3, last5, none
- Theme-aware visual feedback (colors adapt to dark/light/day)
- Audio beeps based on pattern
- Cancelable at any time

### 6. ChemicalManager (lines ~7051-7800)

**Darkroom chemistry tracking**

- Mix calculator with presets
- Developer capacity tracking (paper-area based)
- Shelf-life tracking with expiration alerts
- Storage keys: CHEMICAL_PRESETS, CAPACITY_TRACKER, SHELF_LIFE

### 7. SettingsManager (lines ~5928-6500)

**Global preferences persistence**

- Live settings with 150ms debouncing
- Persists to LocalStorage via StorageManager
- Applies settings to runtime immediately
- Handles color scheme, sound, countdown, test strip settings
- **Debouncing**: 150ms delay prevents excessive UI updates

### 8. AudioService (lines ~4190-4360)

**Web Audio API for beep patterns**

- Configurable frequency, duration, volume
- Presets: warning, complete, countdown, relay, chemical, etc.
- Must be initialized with user interaction
- Used by all timer classes for feedback

### 9. StorageManager (lines ~5027-5280)

**Centralized LocalStorage handler**

- Manages all persistence keys with error handling
- **Critical**: All state changes must flow through this manager
- Keys: settings, profiles, current_profile, color_scheme, chemical_presets, capacity_tracker, shelf_life, custom_filter_banks, test_strip_profiles, current_test_strip_profile, split_grade_presets, current_split_preset, test_transfer_destination
- JSON serialization with error handling

### 10. DriftCorrectedTimer (lines ~4369-4450)

**High-precision timing**

- Uses `Date.now()` for millisecond accuracy
- Compensates for JavaScript timer drift
- **Never use setInterval** - always use this for photographic timing
- Callback-based with interval correction

## 📋 Tab-Specific Architecture

### CALC Tab

- Base time slider (0.4-50s), stop increment selector
- Exposure calculator with start/stop/reset buttons
- **Auto-trigger**: Calls `window.relayManager.triggerTimerRelay(appState.calculator.thisExposureTime)` after countdown

### TEST Tab (F-Stop Test Strip)

- FStopTestStripGenerator supports cumulative/incremental methods
- **Click-to-apply**: Clicking a step applies its time to CALC tab's base time
- Theme-aware colors based on current theme and exposure intensity

### TIMER Tab

- Four independent Timer instances (Dev, Stop, Fix, Flo)
- Default times from `DEFAULT_TIMER_TIMES`
- Optional auto-chain (autoStart) for workflow automation

### CONTROL Tab (Relay)

- RelayManager manages server IP/port, connection tests
- **Relay map**: 1→GPIO25 (Enlarger), 2→GPIO17 (Safelight), 3→GPIO27 (Ventilation), 4→GPIO22 (White Light)
- safelightAutoOff turns safelight off while enlarger is on, restores afterward

### CHEMICAL Tab

- ChemicalManager handles mix calculator, presets
- Developer capacity tracking (paper-area based)
- Shelf-life tracking with expiration alerts

### CHART Tab

- updateChart() renders f-stop table based on current base time and stop settings

### SETTINGS Tab

- SettingsManager persists preferences with 150ms debouncing
- Sound toggles, autoStart, color scheme
- Countdown options (countdownDelay, countdownBeep, countdownPattern)
- Test strip autoAdvance, safelightAutoOff

## Critical Architecture Patterns

### 1. Manager Class Ecosystem (Client)

The client uses sophisticated manager classes that must be understood for any modifications:

- **RelayManager** (lines ~6537-7100) - Central hub for server communication
  - Handles all HTTP requests to Flask server
  - Manages relay state tracking (1=GPIO25 Enlarger, 2=GPIO17 Safelight, 3=GPIO27 Ventilation, 4=GPIO22 White Light)
  - **Critical**: Safelight auto-off feature - automatically turns off safelight when enlarger activates, restores after exposure + 0.5s buffer
  - Uses triple-fallback fetch strategy for maximum compatibility

- **Timer** class (lines ~4509-4650) - Individual timer instances (Dev, Stop, Fix, Flo)
  - Uses DriftCorrectedTimer for millisecond precision
  - State managed via appState.timers object
  - Auto-chain functionality via autoStart setting

- **IncrementalTimer** (lines ~7487+) - Dodge/burn calculator with step progression
  - Manages step-by-step exposure calculations
  - Integrates with countdown and relay triggering

- **FStopTestStripGenerator** (lines ~8502+) - Test strip generation
  - Supports cumulative vs incremental methods
  - **Recent**: Click-to-apply functionality - test steps can be clicked to apply their time to CALC tab
  - **Recent**: Enhanced visual feedback with theme-aware coloring

- **CountdownManager** (lines ~4704+) - Visual countdown before exposure
  - Configurable delay (default 5 seconds)
  - Multiple beep patterns: every-second, last3, last5, none

- **ChemicalManager** (lines ~5876+) - Darkroom chemistry tracking
  - Mix calculator with presets
  - Developer capacity tracking (paper-area based)
  - Shelf-life tracking with expiration alerts

- **SettingsManager** (lines ~4886+) - Global preferences
  - Persists all user settings to LocalStorage
  - **Recent**: Enhanced live settings application with debouncing (150ms)

- **AudioService** (lines ~3781+) - Web Audio API for beep patterns
  - Configurable frequency, duration, volume
  - Used by all timer classes for feedback

- **StorageManager** - Centralized LocalStorage handler
  - Manages all persistence keys with error handling
  - **Critical**: All state changes must flow through this manager

- **DriftCorrectedTimer** (lines ~3900+) - High-precision timing
  - Uses Date.now() for millisecond accuracy
  - Compensates for JavaScript timer drift
  - **Never use setInterval** - always use this for photographic timing

### 2. State Management Architecture

**Three-tier state system** with clear separation:

```javascript
const appState = {
  ui: {
    /* transient, not persisted */
  },
  calculator: {
    /* runtime calculator state */
  },
  timers: {
    /* timer instances state */
  },
  settings: {
    /* persisted preferences */
  },
  persistent: {
    /* persisted data (profiles, presets) */
  },
};
```

**Storage Keys** (all prefixed with `darkroom_timer_`):

- `settings` - All user preferences
- `profiles` - Saved timer profiles
- `current_profile` - Active profile name
- `color_scheme` - Theme preference
- `chemical_presets` - Chemistry presets
- `capacity_tracker` - Developer usage
- `shelf_life` - Chemical expiration tracking
- `custom_filter_banks` - Custom contrast filters
- `test_strip_profiles` - Test strip configurations

### 3. GPIO & Hardware Control

**Pin Mapping (BCM Mode)**:

```python
RELAY_PINS = {
    25: {"name": "Enlarger Timer", "state": False},
    17: {"name": "Safelight", "state": False},
    27: {"name": "Ventilation", "state": False},
    22: {"name": "White Light", "state": False}
}
```

**Critical Hardware Pattern**: Relays are **active-LOW**

- `GPIO.HIGH` = OFF
- `GPIO.LOW` = ON
- The `set_relay_state(pin, state)` function handles this inversion

**Safelight Auto-Off Flow** (CRITICAL - must be preserved):

1. User starts exposure (CALC, TEST, or TIMER with auto-trigger)
2. `RelayManager.triggerTimerRelay()` checks if safelight (relay 2) is on
3. If on, remembers state and turns safelight OFF before starting timer
4. Server starts GPIO 25 timer for specified duration
5. After duration, safelight is automatically restored
6. This prevents safelight fogging during exposure

### 4. API Endpoints (Flask Server)

**Production API (v3.0.3)**:

- `GET /ping` - Connection test, returns `{"status": "ok"}`
- `GET /relay?gpio=25&state=on` - Control single relay (state: `on`|`off`)
- `GET /timer?gpio=25&duration=5.0` - Timed relay activation (max 3600s)
- `GET /status` - Get all relay states
- `GET /all?state=on` - Control all relays simultaneously
- `GET /shutdown` - Graceful system shutdown (3s delay)
- `GET /reboot` - System reboot (3s delay)

**All endpoints support OPTIONS for CORS preflight**. Query parameters use GPIO pin numbers, not relay numbers.

**API Response Pattern**:

```json
{
  "status": "success",
  "gpio": 25,
  "duration": 5.5,
  "name": "Enlarger Timer",
  "message": "Timer started for 5.5s",
  "timestamp": "2026-01-08T10:30:00"
}
```

### 5. Client-Side Integration Flows

**Exposure Flow**:
CALC countdown → AudioService beeps → RelayManager.sendRequest('timer', { gpio: 25, duration }) → server toggles GPIO 25 active-low → client status updates

**Safelight Flow**:
When enlarger turns ON, RelayManager.handleSafelightAutoOff() ensures GPIO17 OFF; on completion, immediately restores previous safelight state

**Persistence Flow**:
UI changes → SettingsManager.saveGlobalSettings() → StorageManager.saveSettings() → appState.settings synced → render functions update

## 📊 Tab-Specific Architecture

### CALC Tab

- Base time slider (0.4-50s), stop increment selector
- Exposure calculator with start/stop/reset buttons
- Uses IncrementalTimer, CountdownManager, AudioService
- **Auto-trigger**: Calls `window.relayManager.triggerTimerRelay(appState.calculator.thisExposureTime)` after countdown

### TEST Tab (F-Stop Test Strip)

- FStopTestStripGenerator supports cumulative/incremental methods
- Countdown and auto-advance with configurable delays
- Uses DEFAULT_SETTINGS.testBaseTime\* and appState.settings.stopDenominator
- **Click-to-apply**: Clicking a step applies its time to CALC tab's base time
- **Theme-aware**: Dynamic colors based on current theme and exposure intensity

### TIMER Tab

- Four independent Timer instances (Dev, Stop, Fix, Flo)
- Default times from DEFAULT_TIMER_TIMES
- Optional auto-chain (autoStart) for workflow automation
- Beep patterns use AudioService presets

### CONTROL Tab (Relay)

- RelayManager manages server IP/port, connection tests
- UI IDs: relayServerIP, relayServerPort, testRelayConnection, relayStatus, autoTriggerRelay, testTimerRelay, testTimerSeconds, allRelaysOn, allRelaysOff
- Relay map: 1→GPIO25 (Enlarger), 2→GPIO17 (Safelight), 3→GPIO27 (Ventilation), 4→GPIO22 (White Light)
- safelightAutoOff turns safelight off while enlarger is on, restores afterward

### CHEMICAL Tab

- ChemicalManager handles mix calculator, presets
- Developer capacity tracking (paper-area based)
- Shelf-life tracking with expiration alerts
- Uses storage keys: CHEMICAL_PRESETS, CAPACITY_TRACKER, SHELF_LIFE

### CHART Tab

- updateChart() renders f-stop table based on current base time and stop settings
- Uses formatStop, calculateTime, and settings limits

### SETTINGS Tab

- SettingsManager persists preferences:
  - Sound toggles, autoStart, color scheme
  - Countdown options (countdownDelay, countdownBeep, countdownPattern)
  - Test strip autoAdvance, safelightAutoOff
- **Recent**: Live settings with 150ms debouncing

## Recent Updates (January 2026)

### Latest Enhancements

1. **Click-to-Apply Test Strip Steps**: Test strip steps are clickable → applies time to CALC tab
2. **Theme-Aware Visual Feedback**: Test strip colors adapt to dark/light/day schemes
3. **Enhanced Safelight Restoration**: 0.5s buffer after exposure before restoring safelight
4. **Live Settings with Debouncing**: 150ms delay prevents excessive UI updates
5. **Improved State Management**: Clear separation between transient UI state and persistent settings

### Critical Patterns for AI Agents

1. **Always use StorageManager** for localStorage operations
2. **Respect triple-fallback fetch strategy** for HTTP requests
3. **Preserve safelight auto-off flow** (off → enlarger → duration → 0.5s buffer → restore)
4. **Use DriftCorrectedTimer** for precision (never setInterval)
5. **CSS variable theming** - modify :root and theme classes, not individual components
6. **Event delegation** for dynamic elements
7. **State synchronization** - update appState before UI changes, flow through managers

## Critical Client Architecture Patterns

### Manager Class Ecosystem

The client uses a sophisticated manager class system that must be understood for any modifications:

1. **RelayManager** (lines ~6537-7100) - Central hub for server communication
   - Handles all HTTP requests to Flask server
   - Manages relay state tracking (1=GPIO25 Enlarger, 2=GPIO17 Safelight, 3=GPIO27 Ventilation, 4=GPIO22 White Light)
   - **Critical**: Safelight auto-off feature - automatically turns off safelight when enlarger activates, restores after exposure
   - Uses triple-fallback fetch strategy for maximum compatibility

2. **Timer** class (lines ~4509-4650) - Individual timer instances (Dev, Stop, Fix, Flo)
   - Uses DriftCorrectedTimer for millisecond precision
   - State managed via appState.timers object
   - Auto-chain functionality via autoStart setting

3. **IncrementalTimer** (lines ~7487+) - Dodge/burn calculator with step progression
   - Manages step-by-step exposure calculations
   - Integrates with countdown and relay triggering

4. **FStopTestStripGenerator** (lines ~8502+) - Test strip generation
   - Supports cumulative vs incremental methods
   - **Recent**: Click-to-apply functionality - test steps can be clicked to apply their time to CALC tab
   - **Recent**: Enhanced visual feedback with theme-aware coloring

5. **CountdownManager** (lines ~4704+) - Visual countdown before exposure
   - Configurable delay (default 5 seconds)
   - Multiple beep patterns: every-second, last3, last5, none

6. **ChemicalManager** (lines ~5876+) - Darkroom chemistry tracking
   - Mix calculator with presets
   - Developer capacity tracking (paper-area based)
   - Shelf-life tracking with expiration alerts

7. **SettingsManager** (lines ~4886+) - Global preferences
   - Persists all user settings to LocalStorage
   - **Recent**: Enhanced live settings application with debouncing (150ms)

8. **AudioService** (lines ~3781+) - Web Audio API for beep patterns
   - Configurable frequency, duration, volume
   - Used by all timer classes for feedback

9. **StorageManager** - Centralized LocalStorage handler
   - Manages all persistence keys with error handling
   - **Critical**: All state changes must flow through this manager

10. **DriftCorrectedTimer** (lines ~3900+) - High-precision timing
    - Uses Date.now() for millisecond accuracy
    - Compensates for JavaScript timer drift
    - **Never use setInterval** - always use this for photographic timing

### State Management Architecture

**Three-tier state system** with clear separation:

```javascript
const appState = {
  ui: {
    /* transient, not persisted */
  },
  calculator: {
    /* runtime calculator state */
  },
  timers: {
    /* timer instances state */
  },
  settings: {
    /* persisted preferences */
  },
  persistent: {
    /* persisted data (profiles, presets) */
  },
};
```

**Storage Keys** (all prefixed with `darkroom_timer_`):

- `settings` - All user preferences
- `profiles` - Saved timer profiles
- `current_profile` - Active profile name
- `color_scheme` - Theme preference
- `chemical_presets` - Chemistry presets
- `capacity_tracker` - Developer usage
- `shelf_life` - Chemical expiration tracking
- `custom_filter_banks` - Custom contrast filters
- `test_strip_profiles` - Test strip configurations

### GPIO & Hardware Control

**Pin Mapping (BCM Mode)**:

```python
RELAY_PINS = {
    25: {"name": "Enlarger Timer", "state": False},
    17: {"name": "Safelight", "state": False},
    27: {"name": "Ventilation", "state": False},
    22: {"name": "White Light", "state": False}
}
```

**Critical Hardware Pattern**: Relays are **active-LOW**

- `GPIO.HIGH` = OFF
- `GPIO.LOW` = ON
- The `set_relay_state(pin, state)` function handles this inversion

**Safelight Auto-Off Flow** (CRITICAL - must be preserved):

1. User starts exposure (CALC, TEST, or TIMER with auto-trigger)
2. `RelayManager.triggerTimerRelay()` checks if safelight (relay 2) is on
3. If on, remembers state and turns safelight OFF before starting timer
4. Server starts GPIO 25 timer for specified duration
5. After duration, safelight is automatically restored
6. This prevents safelight fogging during exposure

### API Endpoints (Flask Server)

**Production API (v3.0.3)**:

- `GET /ping` - Connection test, returns `{"status": "ok"}`
- `GET /relay?gpio=25&state=on` - Control single relay (state: `on`|`off`)
- `GET /timer?gpio=25&duration=5.0` - Timed relay activation (max 3600s)
- `GET /status` - Get all relay states
- `GET /all?state=on` - Control all relays simultaneously
- `GET /shutdown` - Graceful system shutdown (3s delay)
- `GET /reboot` - System reboot (3s delay)

**All endpoints support OPTIONS for CORS preflight**. Query parameters use GPIO pin numbers, not relay numbers.

**API Response Pattern**:

```json
{
  "status": "success",
  "gpio": 25,
  "duration": 5.5,
  "name": "Enlarger Timer",
  "message": "Timer started for 5.5s",
  "timestamp": "2026-01-08T10:30:00"
}
```

### Client-Side Integration Flows

**Exposure Flow**:
CALC countdown → AudioService beeps → RelayManager.sendRequest('timer', { gpio: 25, duration }) → server toggles GPIO 25 active-low → client status updates

**Safelight Flow**:
When enlarger turns ON, RelayManager.handleSafelightAutoOff() ensures GPIO17 OFF; on completion, immediately restores previous safelight state

**Persistence Flow**:
UI changes → SettingsManager.saveGlobalSettings() → StorageManager.saveSettings() → appState.settings synced → render functions update

## Tab-Specific Architecture

### CALC Tab

- Base time slider (0.4-50s), stop increment selector
- Exposure calculator with start/stop/reset buttons
- Uses IncrementalTimer, CountdownManager, AudioService
- **Auto-trigger**: Calls `window.relayManager.triggerTimerRelay(appState.calculator.thisExposureTime)` after countdown

### TEST Tab (F-Stop Test Strip)

- FStopTestStripGenerator supports cumulative/incremental methods
- Countdown and auto-advance with configurable delays
- Uses DEFAULT_SETTINGS.testBaseTime\* and appState.settings.stopDenominator
- **Click-to-apply**: Clicking a step applies its time to CALC tab's base time
- **Theme-aware**: Dynamic colors based on current theme and exposure intensity

### TIMER Tab

- Four independent Timer instances (Dev, Stop, Fix, Flo)
- Default times from DEFAULT_TIMER_TIMES
- Optional auto-chain (autoStart) for workflow automation
- Beep patterns use AudioService presets

### CONTROL Tab (Relay)

- RelayManager manages server IP/port, connection tests
- UI IDs: relayServerIP, relayServerPort, testRelayConnection, relayStatus, autoTriggerRelay, testTimerRelay, testTimerSeconds, allRelaysOn, allRelaysOff
- Relay map: 1→GPIO25 (Enlarger), 2→GPIO17 (Safelight), 3→GPIO27 (Ventilation), 4→GPIO22 (White Light)
- safelightAutoOff turns safelight off while enlarger is on, restores afterward

### CHEMICAL Tab

- ChemicalManager handles mix calculator, presets
- Developer capacity tracking (paper-area based)
- Shelf-life tracking with expiration alerts
- Uses storage keys: CHEMICAL_PRESETS, CAPACITY_TRACKER, SHELF_LIFE

### CHART Tab

- updateChart() renders f-stop table based on current base time and stop settings
- Uses formatStop, calculateTime, and settings limits

### SETTINGS Tab

- SettingsManager persists preferences:
  - Sound toggles, autoStart, color scheme
  - Countdown options (countdownDelay, countdownBeep, countdownPattern)
  - Test strip autoAdvance, safelightAutoOff
- **Recent**: Live settings with 150ms debouncing

## Recent Updates (January 2026)

### Latest Enhancements

1. **Click-to-Apply Test Strip Steps**: Test strip steps are clickable → applies time to CALC tab
2. **Theme-Aware Visual Feedback**: Test strip colors adapt to dark/light/day schemes
3. **Enhanced Safelight Restoration**: 0.5s buffer after exposure before restoring safelight
4. **Live Settings with Debouncing**: 150ms delay prevents excessive UI updates
5. **Improved State Management**: Clear separation between transient UI state and persistent settings

### Critical Patterns for AI Agents

1. **Always use StorageManager** for localStorage operations
2. **Respect triple-fallback fetch strategy** for HTTP requests
3. **Preserve safelight auto-off flow** (off → enlarger → duration → 0.5s buffer → restore)
4. **Use DriftCorrectedTimer** for precision (never setInterval)
5. **CSS variable theming** - modify :root and theme classes, not individual components
6. **Event delegation** for dynamic elements
7. **State synchronization** - update appState before UI changes, flow through managers

## Development Workflow

### Raspberry Pi Flask Testing

```bash
# On Raspberry Pi
python3 Raspberry_Server_v3.0.3.py

# Access from browser
http://<pi-ip>:5000/
http://<pi-ip>:5000/ping
```

Server logs show:

- Local IP and hostname
- All configured GPIO pins
- CORS status
- Available endpoints

### Pico 2 W MicroPython Testing

**Prerequisites:**

```bash
# Install Thonny IDE or ampy
pip3 install adafruit-ampy
```

**Flash MicroPython (one-time):**

1. Download UF2: https://micropython.org/download/rp2w/
2. Hold BOOTSEL button on Pico 2 W
3. Connect USB to computer
4. Copy UF2 to mounted drive
5. Pico reboots with MicroPython

**Deploy Files:**

```bash
# Using ampy (replace /dev/ttyACM0 with your port)
export AMPY_PORT=/dev/ttyACM0

ampy put boot.py
ampy put index.html
ampy mkdir lib
ampy put lib/wifi_ap.py lib/wifi_ap.py
ampy put lib/gpio_control.py lib/gpio_control.py
ampy put lib/http_server.py lib/http_server.py
ampy put lib/timer_manager.py lib/timer_manager.py
```

**Test System:**

1. Connect USB power to Pico 2 W
2. Watch console output (Thonny or screen):
   ```bash
   screen /dev/ttyACM0 115200
   ```
3. Should show: "✅ SYSTEM READY" with WiFi credentials
4. Connect phone to "DarkroomTimer" WiFi (password: darkroom123)
5. Open browser to http://192.168.4.1/

**Edit Configuration:**
Edit `boot.py` lines 27-29 for WiFi settings:

```python
WIFI_SSID = "YourSSID"
WIFI_PASSWORD = "yourpassword"
HTTP_PORT = 80
```

### Testing Without Hardware

For development without Raspberry Pi, comment out GPIO imports and mock the GPIO module. The HTML client works standalone with server unavailable (relay features disabled).

### Python Dependencies

```bash
pip3 install Flask RPi.GPIO
```

No other dependencies required. Server uses only Python stdlib + Flask + GPIO.

### Client Development

The HTML client can be opened directly in a browser for testing UI features. Relay functionality requires the server to be running. Use browser DevTools to:

1. **Check LocalStorage**: Application → Local Storage → Look for `darkroom_timer_*` keys
2. **Monitor Network**: Console tab for fetch requests to server
3. **Test Audio**: Browser must allow audio autoplay (user interaction required)
4. **Verify State**: `appState` object in console for current timer states

### Critical Conventions

1. **GPIO Safety**: Server always calls `cleanup_gpio()` on exit via `atexit.register()` (Flask) or in shutdown handlers (MicroPython) to reset pins to safe state (all OFF).

2. **Threading vs Async**: Flask uses daemon threads (`threading.Thread`). Pico 2 W uses asyncio (`async`/`await`). Never mix paradigms within implementation.

3. **CORS Headers**: Both servers add CORS headers to ALL responses. Flask uses `@app.after_request`, Pico uses manual headers in each response. Never remove CORS handling.

4. **Timer Precision**: Client uses `Date.now()` for millisecond accuracy, not `setInterval`. Critical for photographic timing.

5. **CSS Custom Properties**: When editing styles, modify CSS variables in `:root` and theme classes, not individual component styles.

6. **LocalStorage Keys**: Use descriptive prefixed keys (e.g., `darkroomTimer_profiles`, `relayManager_ip`). Always handle missing keys gracefully.

7. **MicroPython Limitations**:
   - No `urllib.parse` - use custom `_url_decode()` in `http_server.py`
   - Non-blocking sockets raise `OSError` when no data, not return None
   - File serving must use chunked transfers (512-byte chunks) for large files
   - Use `asyncio.create_task()` for background tasks, not threading

## Common Tasks

### Adding New Relay Endpoint

1. Add route to `Raspberry_Server_v3.0.3.py` with OPTIONS support
2. Update `RelayManager` in HTML to add corresponding method
3. Update server's root endpoint `/` documentation

### Adding Timer Feature

1. Create or extend manager class in HTML `<script>` section
2. Add UI elements with appropriate classes (reuse existing styles)
3. Bind event listeners in manager's `init()` method
4. Persist state via LocalStorage if needed
5. Call `window.relayManager.triggerTimerRelay()` if auto-trigger needed

### Changing GPIO Pins

Update `RELAY_PINS` dict in server. **Must also update any hardcoded references in HTML** (e.g., enlarger = GPIO 25 assumptions in relay manager).

### Style Changes

Prefer modifying CSS variables over component styles. If adding new components, reuse consolidated classes (`.shelf-life-item`, `.settings-btn`, etc.) to maintain consistency.

### Adding New Storage Keys

1. Add key to `STORAGE_KEYS` object (lines ~4077-4089)
2. Add corresponding save/load methods to `StorageManager` class
3. Update `clearAllData()` method to include new key
4. Use in manager classes for persistence

### Modifying Relay Behavior

**Critical**: Any changes to relay timing must preserve the 0.5s buffer for safelight restoration. The sequence is:

1. Turn off safelight (if enabled)
2. Start enlarger timer
3. Wait for duration
4. Add 0.5s buffer
5. Restore safelight (if it was on)

## Testing Checklist

- [ ] **Raspberry Pi**: Server starts and logs local IP correctly
- [ ] **Pico 2 W**: System boots with "✅ SYSTEM READY" message
- [ ] `/ping` endpoint responds on both implementations
- [ ] Relay control toggles GPIO pins (verify with multimeter or LED)
- [ ] Client connects and shows "Connected successfully!"
- [ ] Timer countdown plays sound and triggers relay
- [ ] All relays turn OFF on server shutdown
- [ ] Settings persist across page reloads
- [ ] Test in all three color schemes (dark/light/day)
- [ ] Safelight auto-off works correctly (turns off during exposure, restores after)
- [ ] Countdown patterns work (every-second, last3, last5, none)
- [ ] Test strip auto-advance functions with configurable delay
- [ ] Chemical manager tracks capacity and shelf-life correctly
- [ ] F-stop calculations match expected values
- [ ] **Raspberry Pi**: Shutdown/reboot commands work with 3-second delay
- [ ] **Pico 2 W**: WiFi hotspot accessible from phone/tablet
- [ ] Click-to-apply test strip steps work (click step → applies to CALC tab)
- [ ] Theme-aware visual feedback on test strip steps (colors adapt to theme)
- [ ] Live settings with debouncing (150ms delay prevents excessive updates)
- [ ] Enhanced safelight restoration with 0.5s buffer after exposure
- [ ] State persistence correctly separates transient vs persistent data

## Troubleshooting

### Common Issues

**Flask Server won't start**: Check if Flask and RPi.GPIO are installed (`pip3 install Flask RPi.GPIO`)  
**Pico 2 W won't boot**: Verify MicroPython firmware is flashed, check USB console output  
**CORS errors**: Verify server is running and port matches client configuration  
**No audio**: Interact with page first (browser autoplay policy)  
**Relays not responding**: Check GPIO pin mapping and active-LOW logic  
**Timer drift**: Ensure using `DriftCorrectedTimer`, not `setInterval`  
**Safelight not restoring**: Check 0.5s buffer in `RelayManager.triggerTimerRelay()`  
**Pico 2 W WiFi issues**: Check SSID/password in `boot.py`, verify phone connected to correct network  
**MicroPython import errors**: Ensure all `lib/` files are uploaded, check file paths

### Debug Commands

```javascript
// In browser console
window.appState; // View current state
window.relayManager.testConnection(); // Test server
window.storageManager.loadSettings(); // Check persisted data
```

### Getting Help

- Check `USER_MANUAL.md` for user-facing documentation
- Check `PICO_README.md` for Pico 2 W specific details
- Check `QUICK_START.md` for quick setup guides
- Use browser DevTools for client-side debugging
- Check server logs for GPIO and API issues
- For Pico 2 W: Monitor USB console with Thonny or `screen /dev/ttyACM0 115200`
