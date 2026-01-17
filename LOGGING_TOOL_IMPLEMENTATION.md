# Exposure Logging Tool Implementation

## Overview

Implemented a comprehensive logging tool that automatically tracks printing sessions across TEST, SPLIT, CALC, and TIMER tabs. Sessions are auto-saved (max 6 temporary) and can be permanently saved with user notes.

## Features Implemented

### 1. New LOGS Tab

- **Location**: Added as the 9th tab (after SETTINGS)
- **Purpose**: View and manage all exposure sessions
- **UI Components**:
  - Session statistics display
  - Temporary sessions list (auto-saved, max 6)
  - Permanent sessions list (user-saved, unlimited)
  - Export/Import buttons (CSV, JSON)
  - Clear all logs button

### 2. Automatic Session Management

- **Session Start**: Triggered automatically on first exposure
  - TEST countdown finishes → Session starts
  - SPLIT sends to CALC → Session starts
  - CALC exposure completes → Session starts
- **Session End**: Triggered when TIMER starts
  - Any timer (Dev, Stop, Fix, Flo) starts → Session ends
  - Session saved to temporary list

### 3. Session Data Structure

```javascript
{
  id: "temp-1234567890",
  name: "Exposure: 28.28s",
  created: "2026-01-15T14:30:00",
  source: "calc",
  type: "exposure",
  phases: {
    test: { baseTime, method, steps, selectedStep, selectedStop, transferDestination, notes },
    split: { neutralTime, paperBrand, softFilter, hardFilter, filterBrand, highlightsBase, shadowsBase, softTime, hardTime, totalTime, burnPercent },
    calc: [{ baseTime, stopAdjustment, finalTime, filterContext, timestamp, notes }],
    timer: { dev, stop, fix, flo }
  },
  notes: "",
  isTemporary: true,
  ended: "2026-01-15T14:35:00"
}
```

### 4. Filter Brand and Names Logging

When SPLIT is used, the tool captures:

- **Paper brand**: Ilford, Kodak, FOMA, Custom
- **Soft filter name**: F00, F0, F1, F2, F3, F4 (for highlights)
- **Hard filter name**: F1, F2, F3, F4, F5 (for shadows)
- **Filter brand**: Ilford, Kodak, etc. (from SPLIT tab selection)

### 5. Notes System

- **CALC Tab**: Notes input field for each exposure
- **TEST Tab**: Notes input field for test strip session
- **Session Notes**: Can be added when saving permanently
- **Step Notes**: Captured per exposure in CALC phase

### 6. Storage Strategy

- **Temporary Sessions** (max 6):
  - Auto-saved to `darkroom_timer_temp_sessions`
  - Overwrites oldest when limit reached
  - Lost on page reload unless saved permanently
- **Permanent Sessions** (unlimited):
  - Saved to `darkroom_timer_permanent_sessions`
  - Persist across page reloads
  - Never auto-deleted

### 7. Export/Import

- **CSV Format**: For spreadsheet import
  - Columns: Session, Date, Phase, Source, BaseTime, Stop, FinalTime, SoftFilter, HardFilter, FilterBrand, PaperBrand, Notes
- **JSON Format**: For backup/restore
  - Complete session data with all phases

### 8. Integration Points

#### CALC Tab

- **Notes Input**: Added below timer display
- **Auto-logging**: When exposure completes, logs:
  - Base time
  - Stop adjustment
  - Final exposure time
  - Filter context (if from SPLIT)
  - User notes
- **Session Status**: Active session indicator

#### TEST Tab

- **Notes Input**: Added below test strip controls
- **Auto-logging**: When countdown finishes, logs:
  - Test base time
  - Method (cumulative/incremental)
  - All steps
  - Selected step
  - Transfer destination
  - User notes

#### SPLIT Tab

- **Auto-logging**: When "Send to CALC" is clicked, logs:
  - Neutral time
  - Paper brand
  - Soft filter (name + brand)
  - Hard filter (name + brand)
  - Highlights base time
  - Shadows base time
  - Soft time (with filter factor)
  - Hard time (with filter factor)
  - Total time
  - Burn percentage

#### TIMER Tab

- **Auto-logging**: When ANY timer starts, logs:
  - Dev, Stop, Fix, Flo times
  - Ends current session
  - Saves to temporary list

### 9. Session Names

Auto-generated based on first CALC exposure:

- "Exposure: 28.28s"
- "Test Strip: 10.0s"
- "Split: F00/F5"
- User can rename when saving permanently

### 10. Visual Design

Uses existing CSS classes:

- `.incremental-timer` for session containers
- `.shelf-life-list` for session lists
- `.shelf-life-item` for each session
- `.settings-btn` for action buttons
- `.info-box` for statistics
- `.label-sm` and `.value-display` for data
- Collapsible sections for session details

## Usage Workflow

### Automatic Session Flow

1. **Start working** → First exposure happens
2. **TEST countdown** → Session starts (temp-1)
3. **SPLIT sends to CALC** → Add SPLIT data to temp-1
4. **CALC exposure** → Add CALC data to temp-1
5. **TIMER starts** → End temp-1, save to temp list
6. **Next session** → temp-2 created
7. **Max 6 temp sessions** → Oldest overwritten

### Manual Actions

1. **View session**: Click "View" button
2. **Save permanently**: Click "Save" button
   - Add notes (optional)
   - Add custom name (optional)
   - Session moves from temp to permanent
3. **Export**: Click "Export CSV" or "Export JSON"
4. **Import**: Click "Import JSON" to restore
5. **Delete**: Click "Delete" button

## Storage Keys Added

- `darkroom_timer_temp_sessions`: Temporary sessions (max 6)
- `darkroom_timer_permanent_sessions`: Permanent sessions (unlimited)

## Files Modified

- `Darkroom_Tools_v3.0.3.html`:
  - Added STORAGE_KEYS for logging
  - Added appState.logging object
  - Added LOGS tab button and content
  - Added ExposureLogManager class
  - Modified IncrementalTimer to log CALC exposures
  - Modified FStopTestStripGenerator to log TEST sessions
  - Modified SplitGradeCalculator to log SPLIT phases
  - Modified Timer.start() to end sessions
  - Added notes input fields to CALC and TEST tabs
  - Added event listeners for LOGS tab buttons

## Testing Checklist

- [ ] TEST tab countdown auto-logs session
- [ ] SPLIT tab "Send to CALC" auto-logs split-grade data
- [ ] CALC tab exposure auto-logs with notes
- [ ] TIMER tab start auto-ends session
- [ ] Temporary sessions limited to 6
- [ ] Save to permanent works with notes
- [ ] CSV export includes all data
- [ ] JSON export/import works
- [ ] Session view shows all phases
- [ ] Filter brands and names captured correctly
- [ ] CALC Total only includes CALC exposures
- [ ] Notes appear in session details

## Example Session

```
Session: "Exposure: 28.28s"
Created: 2026-01-15 14:30:00
Ended: 2026-01-15 14:35:00

TEST Phase:
  Base Time: 5.0s
  Method: Cumulative
  Steps: [2.5, 5.0, 10.0, 20.0]
  Selected: 10.0s (F1.0)
  Transfer: CALC
  Notes: "Portrait - find base exposure"

SPLIT Phase:
  Neutral Time: 10.0s
  Paper: Ilford Multigrade
  Soft Filter: F00 (Ilford)
  Hard Filter: F5 (Ilford)
  Highlights: 5.0s
  Shadows: 7.5s
  Total: 12.5s

CALC Phase:
  Exposure 1: 10.0s × 2^(+1.5) = 28.28s [F00/F5]
  Notes: "Added 1 stop - perfect"
  CALC Total: 28.28s

TIMER Phase:
  Dev: 60s, Stop: 30s, Fix: 60s, Flo: 30s
```

## CSV Export Example

```
Session,Date,Phase,Source,BaseTime,Stop,FinalTime,SoftFilter,HardFilter,FilterBrand,PaperBrand,Notes
"Exposure: 28.28s",2026-01-15,TEST,TEST,5.0,N/A,N/A,N/A,N/A,N/A,N/A,"Portrait - find base exposure"
"Exposure: 28.28s",2026-01-15,SPLIT,SPLIT,10.0,N/A,12.5,F00,F5,Ilford,Ilford,N/A
"Exposure: 28.28s",2026-01-15,CALC,CALC,10.0,+1.5,28.28,F00,F5,Ilford,Ilford,"Added 1 stop - perfect"
"Exposure: 28.28s",2026-01-15,TIMER,TIMER,N/A,N/A,N/A,N/A,N/A,N/A,N/A,"Dev:60,Stop:30,Fix:60,Flo:30"
```

## JSON Export Example

```json
{
  "exported": "2026-01-15T14:35:00",
  "permanentSessions": [
    {
      "id": "perm-1234567890",
      "name": "Exposure: 28.28s",
      "created": "2026-01-15T14:30:00",
      "source": "calc",
      "phases": {
        "test": {
          "baseTime": 5.0,
          "method": "cumulative",
          "selectedStep": 10.0,
          "notes": "Portrait - find base exposure"
        },
        "split": {
          "neutralTime": 10.0,
          "softFilter": "F00",
          "hardFilter": "F5",
          "filterBrand": "Ilford",
          "paperBrand": "Ilford"
        },
        "calc": [
          {
            "baseTime": 10.0,
            "stopAdjustment": 1.5,
            "finalTime": 28.28,
            "notes": "Added 1 stop - perfect"
          }
        ],
        "timer": { "dev": 60, "stop": 30, "fix": 60, "flo": 30 }
      },
      "notes": "Print #5 - Portrait of Sarah",
      "savedAt": "2026-01-15T14:36:00"
    }
  ]
}
```

## Key Design Decisions

### 1. Automatic vs Manual

- **Automatic**: Session start/end, data capture
- **Manual**: Save to permanent, add notes, export

### 2. Temporary vs Permanent

- **Temporary**: Auto-saved, max 6, for current workflow
- **Permanent**: User-saved, unlimited, for archive

### 3. Session Identification

- **Auto-generated names**: Based on first CALC exposure
- **User-editable**: Can rename when saving permanently

### 4. Filter Information

- **Captured from SPLIT**: Brand and names for both filters
- **Stored in CALC phase**: As filter context string

### 5. Notes System

- **Per-exposure**: CALC tab notes field
- **Per-session**: TEST tab notes + permanent save notes
- **Flexible**: Can add notes after session ends

## Future Enhancements (Optional)

- Auto-expire temporary sessions after X days
- Search/filter sessions by date, type, or notes
- Session statistics (average exposure time, most used filter)
- Print session summary
- Duplicate session functionality
- Session tags/categories

## Implementation Status

✅ Storage keys added
✅ appState.logging object added
✅ LOGS tab UI created
✅ ExposureLogManager class implemented
✅ CALC tab integration (auto-log + notes)
✅ TEST tab integration (auto-log + notes)
✅ SPLIT tab integration (auto-log)
✅ TIMER tab integration (auto-end session)
✅ Temporary session management (max 6)
✅ Permanent session saving
✅ CSV export
✅ JSON export/import
✅ Session view/details
✅ Filter brand and names logging
✅ Notes system
✅ CALC Total calculation (only CALC exposures)
✅ CSS styling using existing classes
✅ Event listeners for LOGS tab buttons

## Ready for Use

The logging tool is fully implemented and ready for use. All sessions are automatically tracked, temporary sessions are auto-saved (max 6), and users can save permanent sessions with notes. CSV/JSON export provides data for spreadsheet analysis and backup.
