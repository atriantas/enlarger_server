# CALC Phase Display Fix

## Problem

In the LOGS tab, the CALC phase steps were displaying incorrectly:

- **Before:** `Exposure 1: 10s × 2^(1) = 20s`
- **Issue:** The "× 2^(1)" format is not user-friendly and doesn't match the CALC tab display

## Solution

Updated the viewSession() method in ExposureLogManager to use the same format as the CALC tab's "Selected Stop Display".

### Changes Made

**Location:** `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.viewSession() method

**Before:**

```javascript
details += `  Exposure ${i + 1}: ${calc.baseTime}s × 2^(${
  calc.stopAdjustment
}) = ${calc.finalTime}s`;
```

**After:**

```javascript
// Format the stop adjustment for display
const stopDisplay = formatStop(calc.stopAdjustment);
details += `  Exposure ${i + 1}: ${calc.baseTime}s × ${stopDisplay} = ${
  calc.finalTime
}s`;
```

## Display Comparison

### Before Fix

```
CALC PHASE:
  Exposure 1: 10s × 2^(1) = 20s
  Exposure 2: 10s × 2^(2) = 40s
```

### After Fix

```
CALC PHASE:
  Exposure 1: 10s × 1⅓ = 20s
  Exposure 2: 10s × 2⅔ = 40s
```

## Format Details

The `formatStop()` function converts the stop adjustment to a user-friendly format based on the denominator setting:

### Denominator 2 (½ stop increments)

- `0.5` → `½`
- `1.0` → `1.0`
- `1.5` → `1½`

### Denominator 3 (⅓ stop increments - DEFAULT)

- `0.33` → `⅓`
- `0.67` → `⅔`
- `1.0` → `1.0`
- `1.33` → `1⅓`
- `1.67` → `1⅔`

### Denominator 4 (¼ stop increments)

- `0.25` → `¹⁄₄`
- `0.5` → `²⁄₄`
- `0.75` → `³⁄₄`
- `1.0` → `1.0`

## Examples

### Example 1: Base time 10s, +1 stop (denominator 3)

- **Before:** `10s × 2^(1) = 20s`
- **After:** `10s × 1⅓ = 20s`

### Example 2: Base time 5s, +2 stops (denominator 3)

- **Before:** `5s × 2^(2) = 20s`
- **After:** `5s × 2⅔ = 20s`

### Example 3: Base time 8s, +0.5 stops (denominator 2)

- **Before:** `8s × 2^(0.5) = 11.31s`
- **After:** `8s × ½ = 11.31s`

## Benefits

1. **Consistency:** Matches the format shown in the CALC tab's "Selected Stop Display"
2. **Clarity:** Uses familiar stop notation (⅓, ½, ¼) instead of mathematical notation
3. **User-Friendly:** Easier to read and understand at a glance
4. **Accurate:** Uses the same `formatStop()` function as the CALC tab

## Files Modified

- `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.viewSession() method

## Testing

To verify the fix:

1. Open the Darkroom Timer application
2. Go to CALC tab
3. Set base time to 10s
4. Set stop adjustment to +1 (or any value)
5. Click "Start Exposure"
6. After completion, go to LOGS tab
7. Click "View" on the session
8. Verify the CALC phase shows the correct format:
   - Should show: `Exposure 1: 10s × 1⅓ = 20s`
   - Should NOT show: `Exposure 1: 10s × 2^(1) = 20s`

## Technical Details

### Function Used

```javascript
function formatStop(value) {
  const denom = window.stopDenominator || 3;
  const val = value / denom; // actual stops
  // ... formatting logic ...
  return formattedString;
}
```

### Integration

The `formatStop()` function is already used throughout the application:

- CALC tab: "Selected Stop Display"
- CHART tab: Stop values in the table
- TEST tab: Stop values for test strip steps
- SPLIT tab: Stop values for split-grade calculations

Now it's also used in the LOGS tab for consistency.

## Conclusion

This fix ensures that the CALC phase display in the LOGS tab matches the format used throughout the rest of the application, providing a consistent and user-friendly experience for the photographer.
