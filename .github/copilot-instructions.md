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

2. **Web Client** (`Darkroom_Tools_v3.0.3.html`) - ~10,800 line single-file application
   - Pure vanilla JavaScript, no frameworks
   - CSS custom properties for theming (dark/light/day schemes)
   - LocalStorage-based state persistence
   - Modular class-based architecture despite being single-file

### File Versioning Pattern

Multiple numbered server files exist (`Raspberry_Server_3.py`, `_5.py`, etc.) representing development iterations. **Current production version is `Raspberry_Server_v3.0.3.py`** which pairs with `Darkroom_Tools_v3.0.3.html`. Always work with matching version numbers.

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

### Critical Hardware Pattern

Relays are **active-LOW**: Set `GPIO.HIGH` to turn relay OFF, `GPIO.LOW` to turn it ON. The `set_relay_state(pin, state)` function handles this inversion. Never write GPIO values directly.

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

## Client-Side Architecture

### Key Design Patterns

1. **Manager Classes** - Each major feature has a dedicated manager class:

   - `TimerManager` - Four simultaneous f-stop timers with decimal precision
   - `RelayManager` - Handles server communication and relay state
   - `IncrementalTimer` - Dodge/burn calculator with step progression
   - `FStopTestGenerator` - Test strip generation with base/step calculations
   - `CountdownManager` - Visual countdown before exposure starts

2. **CSS Consolidation** - Heavy use of CSS variable theming and class reuse:

   ```css
   :root {
     --bg, --text, --accent, --panel, --border, --slider-track
   }
   body.light-scheme { /* overrides */ }
   body.day-scheme { /* overrides */ }
   ```

   Many classes consolidated (e.g., `.shelf-life-item` replaces 15+ similar classes).

3. **State Persistence** - Extensive LocalStorage usage:

   - All timer settings, profiles, presets, chemical trackers
   - Collapsible section states per data-id attribute
   - Relay server IP/port configuration
   - User preferences (sound, auto-trigger, color scheme)

4. **No Build Step** - Entire client is deployable as single HTML file. All CSS and JavaScript inline.

### Relay Integration Pattern

The client connects to the server via user-configured IP/port (default `192.168.1.100:5000`):

```javascript
// In RelayManager class
async sendRequest(endpoint, params = {}) {
  const url = `http://${this.ip}:${this.port}/${endpoint}?${new URLSearchParams(params)}`;
  const response = await fetch(url);
  return await response.json();
}

// Triggering exposure
await this.sendRequest("timer", { gpio: 25, duration: 5.5 });
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

### Integration Flows

- **Exposure flow**: CALC countdown → `AudioService` beeps → `RelayManager.sendRequest('timer', { gpio: 25, duration })` → server toggles GPIO 25 active-low → client status updates.
- **Safelight flow**: When enlarger turns ON, `RelayManager.handleSafelightAutoOff()` ensures GPIO17 OFF; on completion, restores previous safelight state.
- **Persistence flow**: UI changes → `SettingsManager.saveGlobalSettings()` → `StorageManager.saveSettings()` → `appState.settings` synced → render functions update.

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

## Critical Conventions

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

## Testing Checklist

- [ ] Server starts and logs local IP correctly
- [ ] `/ping` endpoint responds
- [ ] Relay control toggles GPIO pins (verify with multimeter or LED)
- [ ] Client connects and shows "Connected successfully!"
- [ ] Timer countdown plays sound and triggers relay
- [ ] All relays turn OFF on server shutdown
- [ ] Settings persist across page reloads
- [ ] Test in all three color schemes (dark/light/day)
