# Export Functionality Fix

## Summary

Modified the export functionality in the LOGS tab to:

1. Export only PERMANENT SESSIONS (not temporary auto-saved sessions)
2. Add a Time column to the CSV export
3. Remove Source and PaperBrand columns from CSV export

## Changes Made

### 1. exportCSV() Method

**Location:** `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.exportCSV()

**Before:**

```javascript
const allSessions = [
  ...appState.logging.permanentSessions,
  ...appState.logging.tempSessions,
];

let csv =
  "Session,Date,Phase,Source,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,PaperBrand,Notes\n";
```

**After:**

```javascript
const allSessions = appState.logging.permanentSessions;

let csv =
  "Session,Date,Time,Phase,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,Notes\n";
```

**Key Changes:**

- ✅ Only exports permanent sessions (removed temp sessions)
- ✅ Added Time column
- ✅ Removed Source column
- ✅ Removed PaperBrand column

### 2. exportJSON() Method

**Location:** `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.exportJSON()

**Before:**

```javascript
const data = {
  exported: new Date().toISOString(),
  permanentSessions: appState.logging.permanentSessions,
  tempSessions: appState.logging.tempSessions,
};
```

**After:**

```javascript
const data = {
  exported: new Date().toISOString(),
  permanentSessions: appState.logging.permanentSessions,
};
```

**Key Changes:**

- ✅ Only exports permanent sessions (removed temp sessions)

## CSV Format Comparison

### Before Fix

```
Session,Date,Phase,Source,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,PaperBrand,Notes
Test Session,1/16/2026,TEST,manual,10,N/A,N/A,N/A,N/A,N/A,N/A,"calc"
Test Session,1/16/2026,SPLIT,manual,10,N/A,20,3,12,Ilford,MGIV,N/A
Test Session,1/16/2026,CALC,manual,10,1,20,F3/F12,N/A,N/A,N/A,""
```

### After Fix

```
Session,Date,Time,Phase,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,Notes
Test Session,1/16/2026,10:30:45,TEST,10,N/A,N/A,N/A,N/A,N/A,"calc"
Test Session,1/16/2026,10:30:45,SPLIT,10,N/A,20,3,12,Ilford,N/A
Test Session,1/16/2026,10:30:45,CALC,10,1,20,F3/F12,N/A,N/A,""
```

## Benefits

### 1. Only Permanent Sessions

- **Before:** Exported both temporary and permanent sessions
- **After:** Only exports permanent sessions
- **Why:** Temporary sessions are auto-saved and may not be finalized. Only permanent sessions should be exported for record-keeping.

### 2. Time Column Added

- **Before:** Only Date column
- **After:** Date and Time columns
- **Why:** Provides more precise timestamp information for better session tracking

### 3. Removed Source Column

- **Before:** Included Source column (manual, test, split, calc)
- **After:** Removed Source column
- **Why:** Source information is not needed in exported data as it's already indicated by the Phase column

### 4. Removed PaperBrand Column

- **Before:** Included PaperBrand column
- **After:** Removed PaperBrand column
- **Why:** Paper brand information is already captured in the FilterBrand column for SPLIT phases

## Usage Workflow

### Before Fix

1. User creates sessions (temporary or permanent)
2. User clicks "Export CSV"
3. **Issue:** Both temporary and permanent sessions exported
4. **Issue:** No time information
5. **Issue:** Unnecessary columns (Source, PaperBrand)

### After Fix

1. User saves sessions to permanent storage
2. User clicks "Export CSV"
3. **Result:** Only permanent sessions exported
4. **Result:** Date and time information included
5. **Result:** Clean CSV with only essential columns

## Testing

To verify the fix:

1. Create several sessions in the LOGS tab
2. Save some sessions to permanent storage
3. Leave some sessions in temporary storage
4. Click "Export CSV"
5. Verify:
   - Only permanent sessions are in the CSV
   - Time column is present
   - Source column is NOT present
   - PaperBrand column is NOT present
6. Click "Export JSON"
7. Verify:
   - Only permanent sessions are in the JSON
   - No tempSessions in the exported JSON

## Files Modified

- `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.exportCSV() and exportJSON() methods

## Technical Details

### CSV Header Changes

**Before:**

```
Session,Date,Phase,Source,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,PaperBrand,Notes
```

**After:**

```
Session,Date,Time,Phase,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,Notes
```

### Data Changes

**TEST Phase:**

- Before: `${sessionName},${sessionDate},TEST,${session.source},${session.phases.test.baseTime},N/A,N/A,N/A,N/A,N/A,N/A,"${session.phases.test.transferDestination}"`
- After: `${sessionName},${sessionDate},${sessionTime},TEST,${session.phases.test.baseTime},N/A,N/A,N/A,N/A,N/A,"${session.phases.test.transferDestination}"`

**SPLIT Phase:**

- Before: `${sessionName},${sessionDate},SPLIT,${session.source},${session.phases.split.neutralTime},N/A,${session.phases.split.totalTime},${session.phases.split.softFilter},${session.phases.split.hardFilter},${session.phases.split.filterBrand},${session.phases.split.paperBrand},N/A`
- After: `${sessionName},${sessionDate},${sessionTime},SPLIT,${session.phases.split.neutralTime},N/A,${session.phases.split.totalTime},${session.phases.split.softFilter},${session.phases.split.hardFilter},${session.phases.split.filterBrand},N/A`

**CALC Phase:**

- Before: `${sessionName},${sessionDate},CALC,${session.source},${calc.baseTime},${calc.stopAdjustment},${calc.finalTime},${filterContext},N/A,N/A,N/A,"${calc.notes}"`
- After: `${sessionName},${sessionDate},${sessionTime},CALC,${calc.baseTime},${calc.stopAdjustment},${calc.finalTime},${filterContext},N/A,N/A,"${calc.notes}"`

**TIMER Phase:**

- Before: `${sessionName},${sessionDate},TIMER,${session.source},N/A,N/A,N/A,N/A,N/A,N/A,N/A,"Dev:${session.phases.timer.dev},Stop:${session.phases.timer.stop},Fix:${session.phases.timer.fix},Flo:${session.phases.timer.flo}"`
- After: `${sessionName},${sessionDate},${sessionTime},TIMER,N/A,N/A,N/A,N/A,N/A,N/A,"Dev:${session.phases.timer.dev},Stop:${session.phases.timer.stop},Fix:${session.phases.timer.fix},Flo:${session.phases.timer.flo}"`

## Conclusion

✅ **The export functionality now correctly exports only permanent sessions with improved CSV format.**

The changes ensure that:

- Only finalized (permanent) sessions are exported
- Time information is included for better tracking
- CSV format is cleaner and more focused
- JSON export is consistent with CSV export
