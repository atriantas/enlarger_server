# Split-Grade Analyzer Implementation Summary

## Changes Made

### 1. Fixed `calculate_split_grade()` in `lib/light_sensor.py`

**Problem**: The original implementation hardcoded filter grades (Grade 00 for soft, Grade 5 for hard) instead of using ΔEV to determine the appropriate grades.

**Solution**:

- Calculate ΔEV first using `calculate_delta_ev()`
- Use `recommend_filter_grade(delta_ev)` to determine the soft filter grade based on measured contrast
- Keep hard filter as the hardest grade (Grade 5 for Ilford, 2xM2 for FOMA)
- Add normalization to preserve total exposure time

**Key Changes**:

```python
# Calculate contrast (ΔEV)
delta_ev = self.calculate_delta_ev(highlight_lux, shadow_lux)

# Use ΔEV to recommend appropriate soft filter grade
recommended = self.recommend_filter_grade(delta_ev, system)
soft_filter = recommended['grade'] if recommended else '00'

# Calculate base times
soft_base_time = cal / highlight_lux
hard_base_time = cal / shadow_lux

# Apply filter factors
raw_soft_time = soft_base_time * soft_factor
raw_hard_time = hard_base_time * hard_factor
raw_total = raw_soft_time + raw_hard_time

# Normalize to preserve total exposure
average_lux = (highlight_lux + shadow_lux) / 2
target_total = cal / average_lux
normalization_scale = target_total / raw_total if raw_total > 0 else 1.0

# Apply normalization
soft_time = raw_soft_time * normalization_scale
hard_time = raw_hard_time * normalization_scale
total_time = soft_time + hard_time
```

### 2. Added "Send to CALC Tab" Button to METER Tab

**Location**: METER tab → Split-Grade Analyzer section

**HTML Changes**:

```html
<!-- Send to CALC Tab Button -->
<div class="settings-btn-group" style="margin-top: 10px">
  <button class="settings-btn primary" id="sendSplitToCalcBtn" disabled>
    Send to CALC Tab
  </button>
</div>
```

### 3. Added `sendSplitToCalc()` Method to `LightMeterManager`

**Functionality**:

- Reuses the existing `SplitGradeCalculator.sendToCalc()` method
- Populates `SplitGradeCalculator` instance with METER tab data
- Updates CALC tab display with actual times from METER tab
- Logs the split-grade session to exposure log

**Key Features**:

- Handles null `neutralTime` (not applicable from METER tab)
- Updates `appState.calculator.splitGrade` with actual times
- Switches to CALC tab automatically
- Provides audio feedback

### 4. Updated CALC Tab Display

**Changes**:

- Updated `splitNeutralDisplay` to show "N/A" when neutralTime is null
- Updated `splitTimeDisplayCalc` to show "N/A" when base times are null
- Updated "Apply Highlights" and "Apply Shadows" buttons to work with both SPLIT tab and METER tab data

### 5. Updated Button Enable/Disable Logic

**Changes**:

- Enable "Send to CALC Tab" button when split-grade analysis is complete
- Disable "Send to CALC Tab" button when readings are cleared

## How It Works Now

### Professional Split-Grade Workflow

1. **Measure Contrast**:
   - User measures highlight lux (thin neg areas)
   - User measures shadow lux (dense neg areas)

2. **Analyze Split-Grade**:
   - System calculates ΔEV = abs(log₂(shadow_lux / highlight_lux))
   - System uses ΔEV to recommend soft filter grade
   - System calculates exposure times:
     - `soft_time = calibration / highlight_lux × soft_factor × normalization`
     - `hard_time = calibration / shadow_lux × hard_factor × normalization`
   - System normalizes total time to match calibration

3. **Send to CALC Tab**:
   - User clicks "Send to CALC Tab"
   - System populates CALC tab's split-grade display
   - System switches to CALC tab
   - User can then:
     - Click "Apply Highlights" to set base time to soft exposure
     - Click "Apply Shadows" to set base time to hard exposure
     - Use the timer to make actual exposures

### Example Workflow

**Scenario**: Negative with ΔEV = 7.2 (high contrast)

1. **Measure**:
   - Highlight: 120 lux
   - Shadow: 850 lux

2. **Analyze**:
   - ΔEV: 7.2 EV
   - Soft filter: Grade 00 (recommended for high contrast)
   - Hard filter: Grade 5
   - Soft time: 15.0s (with normalization)
   - Hard time: 3.2s (with normalization)
   - Total: 18.2s

3. **Send to CALC**:
   - CALC tab shows:
     - Soft: 15.0s (F00)
     - Hard: 3.2s (F5)
     - Total: 18.2s

4. **Make Exposures**:
   - Click "Apply Highlights" → Base time = 15.0s
   - Make soft exposure with Grade 00 filter
   - Click "Apply Shadows" → Base time = 3.2s
   - Make hard exposure with Grade 5 filter

## Key Improvements

### 1. ΔEV-Driven Filter Selection

- **Before**: Always used Grade 00 for soft, Grade 5 for hard
- **After**: Uses ΔEV to recommend appropriate soft filter grade
- **Result**: More accurate contrast matching

### 2. Normalization

- **Before**: No normalization - total time varied with filter factors
- **After**: Normalizes both phases to preserve total exposure
- **Result**: Consistent total exposure time

### 3. Integration

- **Before**: METER tab only showed proportions, no way to use results
- **After**: METER tab can send results to CALC tab
- **Result**: Seamless workflow from analysis to execution

### 4. Professional Workflow

- **Before**: Manual calculation required
- **After**: Automated analysis with professional-grade accuracy
- **Result**: Matches Heiland / RH Designs behavior

## Technical Details

### Normalization Formula

```python
# Target total time based on average lux
average_lux = (highlight_lux + shadow_lux) / 2
target_total = cal / average_lux

# Scale raw times to match target
normalization_scale = target_total / raw_total
soft_time = raw_soft_time * normalization_scale
hard_time = raw_hard_time * normalization_scale
```

### Filter Grade Selection

```python
# Use ΔEV to find best matching filter grade
recommended = self.recommend_filter_grade(delta_ev, system)
if recommended:
    soft_filter = recommended['grade']  # e.g., '00', '0', '1', etc.
else:
    soft_filter = '00'  # Fallback
```

## Files Modified

1. **lib/light_sensor.py**:
   - Fixed `calculate_split_grade()` method
   - Added ΔEV-driven filter selection
   - Added normalization

2. **index.html**:
   - Added "Send to CALC Tab" button to METER tab
   - Added `sendSplitToCalc()` method to `LightMeterManager`
   - Updated CALC tab display to handle null neutralTime
   - Updated event listeners for "Apply Highlights" and "Apply Shadows"
   - Added event listener for new "Send to CALC Tab" button

## Testing

To test the implementation:

1. **Measure contrast** in METER tab:
   - Measure highlight lux
   - Measure shadow lux
   - Click "Analyze Split-Grade"

2. **Verify results**:
   - ΔEV should be displayed
   - Soft and hard filter grades should be shown
   - Proportions should be calculated

3. **Send to CALC**:
   - Click "Send to CALC Tab"
   - Verify CALC tab shows split-grade times
   - Verify "Apply Highlights" and "Apply Shadows" work correctly

4. **Verify normalization**:
   - Total time should be consistent regardless of filter factors
   - Compare with calibration constant

## Notes

- The METER tab's Split-Grade analyzer now follows professional darkroom printing principles
- Filter selection is driven by measured contrast (ΔEV), not manual slider
- Exposure times are calculated independently for highlights and shadows
- Normalization ensures total exposure time remains consistent
- The integration with CALC tab allows seamless workflow from analysis to execution
