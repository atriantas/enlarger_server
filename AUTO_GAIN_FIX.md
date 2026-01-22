# Auto-Gain Stability Fix

## Problem Analysis

The light sensor's auto-gain mechanism was switching gains too frequently due to:

1. **Aggressive Thresholds**: Thresholds at 100 and 36000 were too tight for darkroom environments
2. **No Hysteresis Applied**: The `AUTO_GAIN_HYSTERESIS = 500` value was defined but never used in comparisons
3. **Immediate Switching**: Gain changed on every single read when values bounced near thresholds
4. **Normal Noise Triggers Gain Changes**: In low-light darkroom conditions, sensor fluctuations caused constant oscillation

### Example of the Problem

- Shadow reading at 105 → gain switches UP (ch0 < 100)
- Next reading at 98 → gain switches DOWN (ch0 > 100)
- This cycle repeats causing unreliable lux values

## Solution Implemented

### 1. Enhanced Hysteresis (lib/light_sensor.py)

**Before:**

```python
AUTO_GAIN_HYSTERESIS = 500  # Defined but unused
```

**After:**

```python
AUTO_GAIN_HYSTERESIS = 5000         # Increased 10x
AUTO_GAIN_STABILITY_SAMPLES = 3     # Require N consecutive readings
```

### 2. Auto-Gain Disabled by Default

**Before:**

```python
self.auto_gain_enabled = True
```

**After:**

```python
self.auto_gain_enabled = False  # DISABLED by default for stable meter readings
```

**Rationale**: For darkroom metering, users need stable readings. Auto-gain can be manually enabled if needed, but manual gain control (1x, 25x, 428x, 9876x) is recommended.

### 3. Improved `_auto_adjust_gain()` Logic

**New Algorithm**:

- Adds hysteresis buffer zone around thresholds
- Requires N consecutive out-of-range readings before switching gain
- Resets stability counter when reading returns to normal range
- Prevents single spikes from triggering gain changes

```
Hysteresis range:
├─ LOW_THRESHOLD = 100
│  └─ Buffer: -5000 to 100 (requires 3 consecutive readings below -4900)
├─ HIGH_THRESHOLD = 36000
│  └─ Buffer: 36000 to 41000 (requires 3 consecutive readings above 41000)
```

### 4. New Gain Control Methods

Added to `LightSensor` class:

```python
def set_manual_gain(gain_level)
    # Set fixed gain, disable auto-gain

def enable_auto_gain()
    # Enable auto-gain with enhanced stability

def disable_auto_gain()
    # Disable auto-gain for stable readings
```

### 5. New HTTP Endpoint

**`GET /meter/gain?action=<action>`**

Actions:

- `auto` - Enable auto-gain
- `disable` - Disable auto-gain (keep current gain)
- `1x`, `25x`, `428x`, `9876x`, `low`, `med`, `high`, `max` - Set manual gain

Example:

```bash
# Disable auto-gain and lock to 25x
curl "http://192.168.4.1/meter/gain?action=25x"

# Response:
{"message": "Gain set to 25x", "auto_gain": false, "gain": "25x"}
```

### 6. UI Control Panel (index.html)

Added **SENSOR GAIN** section in METER tab with:

- **AUTO** / **FIXED** toggle buttons
- **Manual gain level buttons**: 1x, 25x, 428x, MAX
- Visual feedback showing current gain setting

**Default**: FIXED mode (auto-gain DISABLED)

**Workflow**:

1. Start in FIXED mode with 25x or 428x gain
2. Take readings for Shadow/Highlight
3. If readings show noise, switch to higher gain or try lower gain if overexposed
4. Once stable, proceed with calculation
5. Only enable AUTO if working in varying light conditions

## Testing Recommendations

### Manual Gain Testing

1. **Set 25x gain** (standard darkroom)

   ```
   Take 5 shadow readings → should show stable lux values (±5%)
   ```

2. **Test each gain level**

   ```
   1x  → Very bright conditions (focus assist)
   25x → Standard (recommended for meter)
   428x → Dim conditions
   9876x → Very dark conditions
   ```

3. **Verify no auto-switching**
   - Disable auto-gain
   - Hold sensor steady for 10 readings
   - Gain display should NOT change
   - Lux values should vary <10%

### Auto-Gain Stability Testing (if enabled)

1. **Enable auto-gain**
   - Set to low light (9876x)
   - Gradually increase light level
   - Should transition: 9876x → 428x → 25x → 1x
   - Each transition requires 3 consecutive stable readings
   - Should NOT oscillate at boundaries

## Files Modified

1. **lib/light_sensor.py**
   - Updated hysteresis constants
   - Rewrote `_auto_adjust_gain()` method
   - Added stability tracking (`_out_of_range_count`)
   - Disabled auto-gain by default
   - Added `set_manual_gain()`, `enable_auto_gain()`, `disable_auto_gain()` methods

2. **lib/http_server.py**
   - Added `_handle_meter_gain()` endpoint handler
   - Added `/meter/gain` route

3. **index.html**
   - Added **SENSOR GAIN** control panel with 6 buttons
   - Added `setGain()` method to LightMeterManager class
   - Added event listeners for gain control buttons
   - Default: FIXED mode (auto-gain disabled)

## Backward Compatibility

- All existing endpoints and calculations unchanged
- Auto-gain defaults to OFF (more stable readings)
- Manual API calls still work:
  ```
  /meter/read → returns lux with current gain
  /meter/calculate?mode=exposure → works as before
  ```

## Known Limitations

- Hysteresis tuned for darkroom use (low-light environments)
- Gain changes take ~600ms (longest integration time)
- For very dynamic light changes, may need to manually switch gain
- Split-grade integration still uses averaged shadow/highlight readings

## Future Enhancements

1. Add per-gain-level calibration factors
2. Implement adaptive hysteresis based on light level
3. Add "auto-gain sweep" mode to find optimal gain
4. Temperature compensation for sensor drift
5. Persistent gain preference per paper profile
