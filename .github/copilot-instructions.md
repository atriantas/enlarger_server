# Darkroom Timer System - AI Coding Agent Instructions

## Project Overview

This is a **professional darkroom timer system** consisting of a Raspberry Pi Flask server controlling relay hardware and a sophisticated single-page HTML/JavaScript client application. The system controls 4 GPIO relays for darkroom equipment (enlarger, safelight, ventilation, white light) with precise timing for photographic printing.

## Architecture

### Two-Component System

1. **Flask Server** (`Raspberry_Server_v3.0.3.py`) - Python backend on Raspberry Pi

   - Runs on port 5000, listens on `0.0.0.0`
   - Controls RPi.GPIO pins: 25 (Enlarger), 17 (Safelight), 27 (Ventilation), 22 (White Light)
   - Active-LOW relay logic: `GPIO.HIGH` = OFF, `GPIO.LOW` = ON
   - Serves the HTML file at root `/` if present in same directory
   - Full CORS enabled for cross-origin browser access
   - Thread-based timer system with daemon threads for non-blocking operation
   - Graceful shutdown/reboot endpoints with 3-second delay

2. **Web Client** (`Darkroom_Tools_v3.0.3.html`) - ~10,754 line single-file application
   - Pure vanilla JavaScript, no frameworks
   - CSS custom properties for theming (dark/light/day schemes)
   - LocalStorage-based state persistence
   - Modular class-based architecture despite being single-file
   - Tab-based interface with 7 functional sections

### Server Architecture Details

**Core Functions:**

- `setup_gpio()` - Initializes GPIO pins as outputs, sets all to HIGH (OFF)
- `set_relay_state(pin, state)` - Handles active-LOW logic, returns success
- `timer_thread(pin, duration)` - Daemon thread for timed relay activation
- `start_timer(pin, duration)` - Cancels existing timer, starts new thread
- `stop_timer(pin)` - Stops active timer for given pin, turns relay OFF
- `cleanup_gpio()` - Turns off all relays, calls GPIO.cleanup()

**Flask Endpoints:**

- Root `/` - Serves HTML file if present, otherwise returns server info
- `/ping` - Connection test
- `/relay` - Single relay control (gpio, state)
- `/timer` - Timed relay activation (gpio, duration)
- `/status` - Current state of all relays
- `/all` - Control all relays simultaneously
- `/shutdown` - Graceful system shutdown (3s delay)
- `/reboot` - System reboot (3s delay)

**CORS Handling:**
All responses include CORS headers via `@app.after_request` decorator. This is critical for browser compatibility.

### File Versioning Pattern

Multiple numbered server files exist (`Raspberry_Server_3.py`, `_5.py`, etc.) representing development iterations. **Current production version is `Raspberry_Server_v3.0.3.py`** which pairs with `Darkroom_Tools_v3.0.3.html`. Always work with matching version numbers.

### Project File Structure

```
enlarger_server/
├── Raspberry_Server_v3.0.3.py    # Production Flask server (GPIO control)
├── Darkroom_Tools_v3.0.3.html    # Production client (single-file app)
├── Raspberry_Server_3.py         # Legacy development version
├── Raspberry_Server_5.py         # Legacy development version
├── Raspberry_Server_6.py         # Legacy development version
├── Raspberry_Server_7.py         # Legacy development version
└── .github/
    └── copilot-instructions.md   # This file - AI agent guidance
```

**Never modify legacy server files** - only work with `Raspberry_Server_v3.0.3.py` and `Darkroom_Tools_v3.0.3.html`.

## Critical Client Architecture Patterns

### Manager Class Ecosystem

The client uses a sophisticated manager class system that must be understood for any modifications:

1. **RelayManager** (lines ~6537-7100) - Central hub for server communication

   - Handles all HTTP requests to Flask server
   - Manages relay state tracking (1=GPIO25 Enlarger, 2=GPIO17 Safelight, 3=GPIO27 Ventilation, 4=GPIO22 White Light)
   - Implements auto-trigger functionality for timer integration
   - **Critical**: Safelight auto-off feature - automatically turns off safelight when enlarger activates, restores after exposure
   - Uses triple-fallback fetch strategy: CORS → no-cors → Image object for maximum compatibility
   - **Recent Update**: Enhanced safelight restoration with 0.5s buffer after exposure

2. **Timer** class (lines ~4509-4650) - Individual timer instances

   - Four instances: Dev, Stop, Fix, Flo
   - Uses DriftCorrectedTimer for millisecond precision
   - State managed via appState.timers object
   - Auto-chain functionality via autoStart setting

3. **IncrementalTimer** (lines ~7487+) - Dodge/burn calculator

   - Manages step-by-step exposure calculations
   - Integrates with countdown and relay triggering
   - **Recent Update**: Enhanced state synchronization with appState.calculator

4. **FStopTestStripGenerator** (lines ~8502+) - Test strip generation

   - Supports cumulative vs incremental methods
   - Auto-advance functionality with configurable delays
   - Base/step time calculations with f-stop precision
   - **Recent Update**: Click-to-apply functionality - test steps can be clicked to apply their time to CALC tab
   - **Recent Update**: Enhanced visual feedback with theme-aware coloring

5. **CountdownManager** (lines ~4704+) - Visual countdown before exposure

   - Configurable delay (default 5 seconds)
   - Multiple beep patterns: every-second, last3, last5, none
   - Critical for user preparation before exposure starts

6. **ChemicalManager** (lines ~5876+) - Darkroom chemistry tracking

   - Mix calculator with presets
   - Developer capacity tracking (paper-area based)
   - Shelf-life tracking with expiration alerts
   - Custom naming support

7. **SettingsManager** (lines ~4886+) - Global preferences

   - Persists all user settings to LocalStorage
   - Manages color schemes, sound preferences, auto-start options
   - Handles countdown and test strip settings
   - **Recent Update**: Enhanced live settings application with debouncing

8. **AudioService** (lines ~3781+) - Sound generation

   - Web Audio API for beep patterns
   - Configurable frequency, duration, volume
   - Used by all timer classes for feedback

9. **StorageManager** - Centralized LocalStorage handler

   - Manages all persistence keys with error handling
   - Provides save/load methods for all data types
   - **Critical**: All state changes must flow through this manager

10. **DriftCorrectedTimer** (lines ~3900+) - High-precision timing
    - Uses Date.now() for millisecond accuracy
    - Compensates for JavaScript timer drift
    - Essential for photographic timing precision

### State Management Architecture

**appState** object structure (lines ~3650-3680):

```javascript
const appState = {
  // Transient UI state (not persisted)
  ui: {
    activeTab: "calculator",
    timerStatus: "READY FOR EXPOSURE",
    collapsibleStates: {}, // Track expanded/collapsed sections
  },

  // Runtime calculator state
  calculator: {
    baseTime: 10.0,
    currentStop: 0,
    currentTotalTime: 10.0,
    thisExposureTime: 10.0,
    accumulatedTime: 0,
    currentTime: 10.0,
    isRunning: false,
    isPaused: false,
    isCountdown: false,
    lastExposureTime: 10.0,
  },

  // Timer instances state (Dev, Stop, Fix, Flo)
  timers: {},

  // Persistent settings (synced with StorageManager)
  settings: {},

  // Persistent data (loaded from StorageManager)
  persistent: {
    currentProfile: null,
    currentChemicalPreset: null,
    currentTestStripProfile: null,
  },
};
```

**Storage Keys** (lines ~3686-3695):

- `darkroom_timer_settings` - All user preferences
- `darkroom_timer_profiles` - Saved timer profiles
- `darkroom_timer_current_profile` - Active profile name
- `darkroom_timer_color_scheme` - Theme preference
- `darkroom_timer_chemical_presets` - Chemistry presets
- `darkroom_timer_capacity_tracker` - Developer usage
- `darkroom_timer_shelf_life` - Chemical expiration tracking
- `darkroom_timer_custom_filter_banks` - Custom contrast filters
- `relayStates` - Relay on/off states (managed by RelayManager)
- `calc_collapsed` - Calculator collapsible sections state

**Default Settings** (lines ~3708-3740):

- Base time: 10.0s, timer defaults: Dev=60s, Stop=30s, Fix=60s, Flo=30s
- Countdown: 5s delay, enabled, pattern='every-second'
- Test strip: auto-advance disabled by default (1s delay)
- Safelight auto-off: enabled by default
- Stop denominator: 3 (for f-stop fractions)
- Base time slider limits: 0.4-50s (main), 1-50s (test)
- **Recent Update**: Enhanced live settings with debouncing (150ms)

## GPIO & Relay Control

### Pin Mapping (BCM Mode)

```python
RELAY_PINS = {
    25: {"name": "Enlarger Timer", "state": False},
    17: {"name": "Safelight", "state": False},
    27: {"name": "Ventilation", "state": False},
    22: {"name": "White Light", "state": False}
}
```

### Client-Side Relay Mapping

The HTML client maps relays 1-4 to GPIO pins:

- **Relay 1** → GPIO 25 (Enlarger Timer) - **Primary exposure control**
- **Relay 2** → GPIO 17 (Safelight) - **Auto-controlled during exposure**
- **Relay 3** → GPIO 27 (Ventilation)
- **Relay 4** → GPIO 22 (White Light)

### Critical Hardware Pattern

Relays are **active-LOW**: Set `GPIO.HIGH` to turn relay OFF, `GPIO.LOW` to turn it ON. The `set_relay_state(pin, state)` function handles this inversion. Never write GPIO values directly.

### Safelight Auto-Off Flow (Critical Integration)

When auto-trigger is enabled and safelight auto-off is active:

1. User starts exposure (CALC, TEST, or TIMER with auto-trigger)
2. `RelayManager.triggerTimerRelay()` checks if safelight (relay 2) is on
3. If on, it remembers state and turns safelight OFF before starting timer
4. Server starts GPIO 25 timer for specified duration
5. After duration + 0.5s buffer, safelight is automatically restored
6. This prevents safelight fogging during exposure

**This flow is implemented in `RelayManager.triggerTimerRelay()` and must be preserved in any modifications.**

## API Endpoints

### Production API (v3.0.3)

- `GET /ping` - Connection test, returns `{"status": "ok"}`
- `GET /relay?gpio=25&state=on` - Control single relay (state: `on`|`off`)
- `GET /timer?gpio=25&duration=5.0` - Timed relay activation (max 3600s)
- `GET /status` - Get all relay states
- `GET /all?state=on` - Control all relays simultaneously
- `GET /shutdown` - Graceful system shutdown (3s delay)
- `GET /reboot` - System reboot (3s delay)

**All endpoints support OPTIONS for CORS preflight**. Query parameters use GPIO pin numbers, not relay numbers.

### API Response Patterns

**Success Response Example:**

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

**Error Response Example:**

```json
{
  "error": "Invalid GPIO pin: 99. Valid pins: [25, 17, 27, 22]"
}
```

### Timing Precision Notes

- Server uses `time.sleep()` in daemon threads for timing
- Client uses `Date.now()` for millisecond accuracy
- Maximum timer duration: 3600 seconds (1 hour)
- Server logs all timer start/stop events with timestamps

## Client-Side Architecture

### Key Design Patterns

1. **Manager Classes** - Each major feature has a dedicated manager class:

   - **Timer** (lines ~4509-4650) - Individual timer instances for Dev, Stop, Fix, Flo
   - **RelayManager** (lines ~6537-7100) - Central hub for server communication and relay state
   - **IncrementalTimer** (lines ~7487+) - Dodge/burn calculator with step progression
   - **FStopTestStripGenerator** (lines ~8502+) - Test strip generation with base/step calculations
   - **CountdownManager** (lines ~4704+) - Visual countdown before exposure starts
   - **ChemicalManager** (lines ~5876+) - Darkroom chemistry tracking and mix calculator
   - **SettingsManager** (lines ~4886+) - Global preferences and LocalStorage persistence
   - **AudioService** (lines ~3781+) - Web Audio API for beep patterns
   - **StorageManager** - Centralized localStorage handler with error handling
   - **DriftCorrectedTimer** (lines ~3900+) - High-precision millisecond timing

2. **CSS Consolidation** - Heavy use of CSS variable theming and class reuse:

   ```css
   :root {
     --bg, --text, --accent, --panel, --border, --slider-track
   }
   body.light-scheme { /* overrides */ }
   body.day-scheme { /* overrides */ }
   ```

   Many classes consolidated (e.g., `.shelf-life-item` replaces 15+ similar classes, `.settings-btn` replaces 20+ button classes).

3. **State Management Architecture** - Sophisticated three-tier state system:

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

   All state changes must flow through StorageManager for persistence.

4. **No Build Step** - Entire client is deployable as single HTML file. All CSS and JavaScript inline.

5. **Click-to-Apply Integration** - Recent enhancement allows clicking test strip steps to apply their time to CALC tab, creating seamless workflow between TEST and CALC tabs.

6. **Theme-Aware UI** - Dynamic visual feedback that adapts to dark/light/day schemes with appropriate color palettes for each theme.

### Relay Integration Pattern

The client connects to the server via user-configured IP/port (default `192.168.1.100:5000`):

```javascript
// In RelayManager class
async sendRequest(endpoint, params = {}) {
  const url = `http://${this.serverIP}:${this.serverPort}/${endpoint}`;
  const queryString = Object.keys(params)
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join("&");
  const fullUrl = queryString ? `${url}?${queryString}` : url;

  // Triple-fallback strategy for maximum compatibility
  try {
    // 1. CORS mode (Chrome/Safari)
    const response = await fetch(fullUrl, { method: "GET", mode: "cors" });
    if (response.ok) return true;
  } catch (error) {
    // 2. no-cors mode
    try {
      await fetch(fullUrl, { method: "GET", mode: "no-cors" });
      return true;
    } catch (noCorsError) {
      // 3. Image object (works for GET requests)
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = fullUrl + `&_=${Date.now()}`; // Cache busting
        setTimeout(() => resolve(false), 3000); // 3s timeout
      });
    }
  }
}

// Triggering exposure with safelight handling
async triggerTimerRelay(durationSeconds) {
  if (!this.autoTrigger) return;

  // Safelight auto-off: turn off if enlarger is starting
  if (this.safelightAutoOff && this.relayStates[2]) {
    this.safelightWasOn = true;
    await this.setRelay(2, false); // Turn off safelight
  }

  // Start timer on GPIO 25 (enlarger)
  await this.sendRequest("timer", { gpio: 25, duration: durationSeconds.toFixed(3) });

  // Restore safelight after duration + 0.5s buffer
  if (this.safelightAutoOff && this.safelightWasOn) {
    setTimeout(async () => {
      if (!this.relayStates[2]) await this.setRelay(2, true);
      this.safelightWasOn = false;
    }, durationSeconds * 1000 + 500);
  }
}
```

**Auto-trigger**: When enabled, timers automatically trigger GPIO 25 (enlarger) on start. Timer controllers call `window.relayManager.triggerTimerRelay(duration)`.

### Client Tools (HTML Tabs)

- **CALC**: Exposure calculator with `IncrementalTimer`, `CountdownManager`, and `AudioService`. Updates `appState.ui.timerStatus` and, when auto-trigger is enabled, calls `window.relayManager.triggerTimerRelay(appState.calculator.thisExposureTime)` after countdown.
- **TEST (F-Stop Test Strip)**: `FStopTestStripGenerator` supports cumulative/incremental methods, countdown, and `autoAdvance`. Uses `DEFAULT_SETTINGS.testBaseTime*` and `appState.settings.stopDenominator`. Triggers enlarger via `RelayManager` when configured.
- **TIMER**: Four independent `Timer` instances (`Dev`, `Stop`, `Fix`, `Flo`) with `isRunning/isEnabled` state, default times from `DEFAULT_TIMER_TIMES`, and optional auto-chain (`autoStart`). Beep patterns use `AudioService` presets.
- **CONTROL (Relay)**: `RelayManager` manages server IP/port, connection tests, and relay actions. UI IDs: `relayServerIP`, `relayServerPort`, `testRelayConnection`, `relayStatus`, `autoTriggerRelay`, `testTimerRelay`, `testTimerSeconds`, `allRelaysOn`, `allRelaysOff`. Relay map: 1→GPIO25 (Enlarger), 2→GPIO17 (Safelight), 3→GPIO27 (Ventilation), 4→GPIO22 (White Light). `safelightAutoOff` turns safelight off while enlarger is on, restores afterward.
- **CHEMICAL**: `ChemicalManager` handles mix calculator, presets, developer capacity (paper-area based), and shelf-life tracking. Uses storage keys `STORAGE_KEYS.CHEMICAL_PRESETS`, `CAPACITY_TRACKER`, `SHELF_LIFE`. Helpers like `getChemicalName()` support custom naming.
- **CHART**: `updateChart()` renders an f-stop table based on current base time and stop settings via `formatStop`, `calculateTime`, and settings limits.
- **SETTINGS**: `SettingsManager` persists preferences: sound toggles, `autoStart`, color scheme, countdown options (`countdownDelay`, `countdownBeep`, `countdownPattern`), test strip `autoAdvance`, and `safelightAutoOff`.

### Key Client Identifiers

- **Storage keys**: `STORAGE_KEYS` object defines `SETTINGS`, `PROFILES`, `CURRENT_PROFILE`, `COLOR_SCHEME`, `CHEMICAL_PRESETS`, `CAPACITY_TRACKER`, `SHELF_LIFE`, `CUSTOM_FILTER_BANKS`, `SESSION_VALUES`.
- **Defaults**: `DEFAULT_SETTINGS` includes countdown and auto-advance fields; `DEFAULT_TIMER_TIMES` holds seconds for `Dev/Stop/Fix/Flo`.
- **Element ID patterns**: Timers use `display<name>`, `btn<name>`, and `timer<name>` (e.g., `displayDev`, `btnDev`). Relay tab uses IDs listed above; ensure event handlers read/write via `RelayManager`.
- **Tab Structure**: 7 tabs with IDs: `calc`, `fstop-test`, `timer`, `relay`, `chemical`, `chart`, `settings`. Each tab has corresponding content div with class `tab-content`.

### UI Tab Functions

- **CALC**: Base time slider (0.4-50s), stop increment selector, exposure calculator with start/stop/reset buttons
- **TEST**: F-stop test strip generator with cumulative/incremental methods, base time, step settings, auto-advance
- **TIMER**: Four independent timers (Dev, Stop, Fix, Flo) with adjust buttons, start/stop/reset controls
- **CONTROL**: Relay server configuration, connection test, individual relay toggles, all relays controls, shutdown/reboot
- **CHEMICAL**: Mix calculator, presets list, developer capacity tracker, shelf-life management
- **CHART**: F-stop calculation table based on current base time and stop denominator
- **SETTINGS**: Color scheme, sound preferences, countdown settings, auto-trigger options, safelight auto-off toggle

### Integration Flows

- **Exposure flow**: CALC countdown → `AudioService` beeps → `RelayManager.sendRequest('timer', { gpio: 25, duration })` → server toggles GPIO 25 active-low → client status updates.
- **Safelight flow**: When enlarger turns ON, `RelayManager.handleSafelightAutoOff()` ensures GPIO17 OFF; on completion, restores previous safelight state.
- **Persistence flow**: UI changes → `SettingsManager.saveGlobalSettings()` → `StorageManager.saveSettings()` → `appState.settings` synced → render functions update.

### Critical Timing Patterns

- **DriftCorrectedTimer**: Uses `Date.now()` for millisecond precision, not `setInterval`
- **Countdown**: Configurable delay (default 5s) with multiple beep patterns
- **Test Strip Auto-advance**: Optional delay between steps (default 1s)
- **Safelight Restoration**: Timer adds 0.5s buffer after exposure before restoring safelight

### Critical Integration Points

1. **Auto-Trigger Integration**: When `autoTrigger` is enabled in RelayManager, all timer-based features (CALC, TEST, TIMER) must call `window.relayManager.triggerTimerRelay(duration)` after countdown completion.

2. **Safelight Auto-Off**: This feature is controlled by `safelightAutoOff` setting in SettingsManager and implemented in RelayManager. It automatically turns off safelight (GPIO 17) when enlarger (GPIO 25) starts, and restores it after exposure + 0.5s buffer.

3. **Countdown System**: Before any exposure starts, the CountdownManager provides visual/audio preparation. This is critical for user safety and must be preserved.

4. **State Synchronization**: All UI changes must update `appState` and persist to LocalStorage via StorageManager. Never bypass this flow. **Recent Update**: Enhanced state management with separate runtime vs persistent state.

5. **Audio Feedback**: All timer operations use AudioService for beeps. Frequency, duration, and volume are configurable via CONFIG constants.

6. **Click-to-Apply Functionality**: Test strip steps can be clicked to apply their total exposure time to the CALC tab's base time slider. This is implemented in `FStopTestStripGenerator.applyStepToCalc()` method.

7. **Theme-Aware Visual Feedback**: Recent updates added dynamic coloring for test strip steps based on current theme (dark/light/day schemes) and exposure intensity.

8. **Live Settings with Debouncing**: Settings changes are applied live with 150ms debouncing to prevent excessive updates while maintaining responsiveness.

9. **Enhanced State Persistence**: The system now distinguishes between transient UI state (not persisted) and persistent settings/data (saved to localStorage). All state changes must flow through StorageManager.

## Recent Updates & Patterns (as of January 2026)

### Latest Enhancements

1. **Click-to-Apply Test Strip Steps**: Test strip steps in the TEST tab are now clickable. Clicking a step applies its total exposure time to the CALC tab's base time slider, creating a seamless workflow between test strip generation and exposure calculation.

2. **Theme-Aware Visual Feedback**: Test strip steps now display dynamic colors based on the current theme:

   - **Dark scheme**: Red intensity based on exposure
   - **Light scheme**: Blue tones with gradient
   - **Day scheme**: Yellow/gold tones with gradient

3. **Enhanced Safelight Restoration**: The safelight auto-off feature now includes a 0.5-second buffer after exposure completion before restoring the safelight, preventing any potential light leaks.

4. **Live Settings with Debouncing**: Settings changes are applied live with 150ms debouncing to prevent excessive UI updates while maintaining responsiveness.

5. **Improved State Management**: Clear separation between:
   - **Transient UI state** (active tab, timer status, collapsible states) - not persisted
   - **Runtime calculator state** (current times, running status) - not persisted
   - **Persistent settings** (user preferences, configurations) - saved to localStorage
   - **Persistent data** (profiles, presets, chemical data) - saved to localStorage

### File Structure & Versioning

- **Current Production**: `Raspberry_Server_v3.0.3.py` + `Darkroom_Tools_v3.0.3.html`
- **Legacy Files**: `Raspberry_Server_3.py`, `_5.py`, `_6.py`, `_7.py` - **DO NOT MODIFY**
- **Line Count**: HTML client is ~10,754 lines, Python server is ~467 lines

### Critical Patterns for AI Agents

1. **Always use StorageManager**: All localStorage operations must go through the StorageManager class for consistent error handling and key management.

2. **Respect the triple-fallback fetch strategy**: When making HTTP requests to the Flask server, always use the CORS → no-cors → Image object fallback pattern.

3. **Preserve safelight auto-off flow**: The sequence is critical: turn off safelight → start enlarger → wait duration → add 0.5s buffer → restore safelight.

4. **Use DriftCorrectedTimer for precision**: Never use setInterval for photographic timing. Always use the DriftCorrectedTimer class which uses Date.now() for millisecond accuracy.

5. **CSS variable theming**: All styling changes should use CSS custom properties in :root and theme classes, not individual component styles.

6. **Event delegation pattern**: Use event delegation for dynamic elements instead of individual event listeners.

7. **State synchronization**: Always update appState before making UI changes, and ensure changes flow through the appropriate manager classes.

## Development Workflow

### Testing the Server

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

1. **GPIO Safety**: Server always calls `cleanup_gpio()` on exit via `atexit.register()` to reset pins to safe state (all OFF).

2. **Threading**: Timer operations use daemon threads to prevent blocking. Active timers tracked in `active_timers` dict for cancellation.

3. **CORS Headers**: Server adds CORS headers to ALL responses via `@app.after_request` decorator. Never remove CORS handling.

4. **Timer Precision**: Client uses `Date.now()` for millisecond accuracy, not `setInterval`. Critical for photographic timing.

5. **CSS Custom Properties**: When editing styles, modify CSS variables in `:root` and theme classes, not individual component styles.

6. **LocalStorage Keys**: Use descriptive prefixed keys (e.g., `darkroomTimer_profiles`, `relayManager_ip`). Always handle missing keys gracefully.

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

1. Add key to `STORAGE_KEYS` object (lines ~3686-3695)
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

- [ ] Server starts and logs local IP correctly
- [ ] `/ping` endpoint responds
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
- [ ] Shutdown/reboot commands work with 3-second delay
- [ ] **NEW**: Click-to-apply test strip steps work (click step → applies to CALC tab)
- [ ] **NEW**: Theme-aware visual feedback on test strip steps (colors adapt to theme)
- [ ] **NEW**: Live settings with debouncing (150ms delay prevents excessive updates)
- [ ] **NEW**: Enhanced safelight restoration with 0.5s buffer after exposure
- [ ] **NEW**: State persistence correctly separates transient vs persistent data
