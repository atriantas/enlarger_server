# Highlights/Shadows Button Reset Fix

## Summary

Modified the HIGHLIGHTS and SHADOWS button event listeners to reset the CALC timer when clicked.

## Changes Made

**Location:** `Darkroom_Tools_v3.0.3.html` - Event listeners for applyHighlights and applyShadows buttons

### applyHighlights Button

**Before:**

```javascript
document.getElementById("applyHighlights")?.addEventListener("click", () => {
  if (
    appState.calculator.splitGrade.enabled &&
    appState.calculator.splitGrade.softTime !== null
  ) {
    const time = appState.calculator.splitGrade.softTime;
    const baseSlider = document.getElementById("baseTimeSlider");
    if (baseSlider) {
      baseSlider.value = time;
      baseSlider.dispatchEvent(new Event("input", { bubbles: true }));
      playBeep(800, 0.3, 0.3);
      settingsManager.showAllProfilesFeedback(
        `Applied Highlights (F${
          appState.calculator.splitGrade.softFilter
        }): ${time.toFixed(2)}s`,
        "success"
      );
    }
  }
});
```

**After:**

```javascript
document.getElementById("applyHighlights")?.addEventListener("click", () => {
  if (
    appState.calculator.splitGrade.enabled &&
    appState.calculator.splitGrade.softTime !== null
  ) {
    const time = appState.calculator.splitGrade.softTime;
    const baseSlider = document.getElementById("baseTimeSlider");
    if (baseSlider) {
      baseSlider.value = time;
      baseSlider.dispatchEvent(new Event("input", { bubbles: true }));
      // Reset CALC timer
      if (window.incrementalTimer) {
        window.incrementalTimer.reset();
      }
      playBeep(800, 0.3, 0.3);
      settingsManager.showAllProfilesFeedback(
        `Applied Highlights (F${
          appState.calculator.splitGrade.softFilter
        }): ${time.toFixed(2)}s`,
        "success"
      );
    }
  }
});
```

### applyShadows Button

**Before:**

```javascript
document.getElementById("applyShadows")?.addEventListener("click", () => {
  if (
    appState.calculator.splitGrade.enabled &&
    appState.calculator.splitGrade.hardTime !== null
  ) {
    const time = appState.calculator.splitGrade.hardTime;
    const baseSlider = document.getElementById("baseTimeSlider");
    if (baseSlider) {
      baseSlider.value = time;
      baseSlider.dispatchEvent(new Event("input", { bubbles: true }));
      playBeep(800, 0.3, 0.3);
      settingsManager.showAllProfilesFeedback(
        `Applied Shadows (F${
          appState.calculator.splitGrade.hardFilter
        }): ${time.toFixed(2)}s`,
        "success"
      );
    }
  }
});
```

**After:**

```javascript
document.getElementById("applyShadows")?.addEventListener("click", () => {
  if (
    appState.calculator.splitGrade.enabled &&
    appState.calculator.splitGrade.hardTime !== null
  ) {
    const time = appState.calculator.splitGrade.hardTime;
    const baseSlider = document.getElementById("baseTimeSlider");
    if (baseSlider) {
      baseSlider.value = time;
      baseSlider.dispatchEvent(new Event("input", { bubbles: true }));
      // Reset CALC timer
      if (window.incrementalTimer) {
        window.incrementalTimer.reset();
      }
      playBeep(800, 0.3, 0.3);
      settingsManager.showAllProfilesFeedback(
        `Applied Shadows (F${
          appState.calculator.splitGrade.hardFilter
        }): ${time.toFixed(2)}s`,
        "success"
      );
    }
  }
});
```

## How It Works

### Before Fix

1. User clicks HIGHLIGHTS or SHADOWS button
2. Base time slider is updated with the split-grade time
3. CALC timer continues running (if it was running)
4. User needs to manually reset the timer

### After Fix

1. User clicks HIGHLIGHTS or SHADOWS button
2. Base time slider is updated with the split-grade time
3. **CALC timer is automatically reset**
4. Timer is ready for new exposure with the applied time

## Benefits

1. **Consistency:** Timer is reset when applying split-grade times
2. **User Experience:** No need to manually reset the timer
3. **Safety:** Prevents accidental exposure with old timer state
4. **Workflow:** Matches the expected behavior when applying new times

## Testing

To verify the fix:

1. Open the SPLIT tab and calculate split-grade times
2. Go to CALC tab
3. Start the CALC timer (let it run for a few seconds)
4. Click the HIGHLIGHTS or SHADOWS button
5. **Verify:** The CALC timer is reset to the new time
6. **Verify:** The timer display shows the new time
7. **Verify:** The timer is ready to start

## Files Modified

- `Darkroom_Tools_v3.0.3.html` - Event listeners for applyHighlights and applyShadows buttons

## Technical Details

### Reset Method

The `window.incrementalTimer.reset()` method:

- Stops any running timer
- Resets accumulated time to 0
- Updates current time to the new base time
- Updates the display
- Sets status to "READY FOR EXPOSURE"

### Integration

The reset is called after:

1. Base time slider is updated with the split-grade time
2. The input event is dispatched to update calculations
3. Before the audio feedback and success message

This ensures the timer is reset with the correct new time.

## Conclusion

✅ **The HIGHLIGHTS and SHADOWS buttons now automatically reset the CALC timer when clicked.**

This provides a consistent and safe workflow when applying split-grade times to the calculator.
