# "Start All" Button Logging Changes

## Summary

Modified the logging tool to also end the current session and start a new session when the user presses the "Start All" button, not only when individual timer Start buttons are pressed.

## Changes Made

### 1. "Start All" Button - New Sequence (Lines 10540-10560)

**Location:** `Darkroom_Tools_v3.0.3.html` - Timer Manager "Start All" button click handler

**Change:** Added logging call after countdown completes and before starting the timer sequence

```javascript
// Log timer start and end current session
if (window.exposureLogManager) {
  const timerData = {
    dev: appState.timers.Dev.timeLeft,
    stop: appState.timers.Stop.timeLeft,
    fix: appState.timers.Fix.timeLeft,
    flo: appState.timers.Flo.timeLeft,
  };
  window.exposureLogManager.addTimerPhaseAndEnd(timerData);
}

// Start the timer as part of a sequence
window.startAllState.isRunning = true;
firstEnabledTimer.reset();
firstEnabledTimer.start(true);
updateStartAllButton();
```

**Impact:**

- When user clicks "Start All" and countdown completes, the current session is ended
- A new session starts automatically after 500ms delay
- The timer sequence then begins

### 2. "Start All" Button - Resume Paused Sequence (Lines 10498-10515)

**Location:** `Darkroom_Tools_v3.0.3.html` - Timer Manager "Start All" button click handler

**Change:** Added logging call when resuming a paused sequence

```javascript
// RESUME paused sequence
if (window.startAllState.isPaused) {
  // Find the first timer that has time left and resume it
  const timerToResume = this.timers.find(
    (t) => t.state.isEnabled && t.state.timeLeft > 0 && !t.state.isRunning
  );
  if (timerToResume) {
    // Log timer start and end current session
    if (window.exposureLogManager) {
      const timerData = {
        dev: appState.timers.Dev.timeLeft,
        stop: appState.timers.Stop.timeLeft,
        fix: appState.timers.Fix.timeLeft,
        flo: appState.timers.Flo.timeLeft,
      };
      window.exposureLogManager.addTimerPhaseAndEnd(timerData);
    }

    window.startAllState.isPaused = false;
    window.startAllState.isRunning = true;
    timerToResume.start(true); // Start as sequence
    updateStartAllButton();
  }
  return;
}
```

**Impact:**

- When user resumes a paused "Start All" sequence, the current session is ended
- A new session starts automatically after 500ms delay
- The timer sequence resumes from where it was paused

## Behavior Comparison

### Before Changes

| Action                        | Session End | New Session |
| ----------------------------- | ----------- | ----------- |
| Individual timer Start button | ✅ Yes      | ✅ Yes      |
| "Start All" button (new)      | ❌ No       | ❌ No       |
| "Start All" button (resume)   | ❌ No       | ❌ No       |

### After Changes

| Action                        | Session End | New Session |
| ----------------------------- | ----------- | ----------- |
| Individual timer Start button | ✅ Yes      | ✅ Yes      |
| "Start All" button (new)      | ✅ Yes      | ✅ Yes      |
| "Start All" button (resume)   | ✅ Yes      | ✅ Yes      |

## Workflow Examples

### Example 1: "Start All" after a printing session

1. User has an active session with CALC exposures
2. User clicks "Start All" button
3. Countdown starts on first enabled timer
4. Countdown completes
5. **NEW:** Current session ends with TIMER phase
6. **NEW:** New session starts automatically (500ms delay)
7. Timer sequence begins

### Example 2: Resume paused "Start All" sequence

1. User starts "Start All" sequence
2. User pauses the sequence
3. User clicks "Start All" again to resume
4. **NEW:** Current session ends with TIMER phase
5. **NEW:** New session starts automatically (500ms delay)
6. Timer sequence resumes

### Example 3: Individual timer Start (unchanged)

1. User has an active session
2. User clicks Start on Dev timer
3. Current session ends with TIMER phase
4. New session starts automatically (500ms delay)
5. Dev timer starts

## Technical Details

### Logging Call Pattern

Both changes use the same pattern:

```javascript
if (window.exposureLogManager) {
  const timerData = {
    dev: appState.timers.Dev.timeLeft,
    stop: appState.timers.Stop.timeLeft,
    fix: appState.timers.Fix.timeLeft,
    flo: appState.timers.Flo.timeLeft,
  };
  window.exposureLogManager.addTimerPhaseAndEnd(timerData);
}
```

This pattern:

- Checks if the logging manager exists
- Captures current timer values for all four timers
- Calls `addTimerPhaseAndEnd()` which:
  1. Adds TIMER phase to current session
  2. Ends the current session
  3. Automatically starts a new session after 500ms delay

### Why This Works

1. **Individual timer Start button:** Calls `Timer.start(isSequence=false)` which triggers logging
2. **"Start All" button (new):** After countdown, calls logging before starting sequence
3. **"Start All" button (resume):** When resuming, calls logging before starting timer

All three paths now properly end the current session and start a new one.

## Files Modified

- `Darkroom_Tools_v3.0.3.html` - Added logging calls in Timer Manager

## Files Created

- `LOGGING_VERIFICATION_UPDATED.md` - Updated verification document
- `START_ALL_LOGGING_CHANGES.md` - This change summary

## Testing

To test the changes:

1. Open the Darkroom Timer application
2. Create a session by using CALC or TEST tabs
3. Click "Start All" button
4. Verify:
   - Current session ends with TIMER phase
   - New session starts automatically
   - Notifications appear for both actions
5. Pause the sequence
6. Click "Start All" again to resume
7. Verify:
   - Current session ends with TIMER phase
   - New session starts automatically
   - Sequence resumes correctly

## Conclusion

✅ **The logging tool now correctly ends sessions and starts new sessions for all timer start actions:**

- Individual timer Start buttons
- "Start All" button (new sequence)
- "Start All" button (resume paused sequence)

The implementation maintains consistency across all timer start methods and provides a seamless workflow for the photographer.
