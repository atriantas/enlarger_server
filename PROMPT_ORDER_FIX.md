# Prompt Order Fix

## Summary

Modified the order of prompts in the "Save to Permanent" dialog to show "Enter custom name" first, then "Enter session notes".

## Changes Made

**Location:** `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.saveToPermanentPrompt() method

**Before:**

```javascript
saveToPermanentPrompt(sessionId) {
  const session = appState.logging.tempSessions.find(
    (s) => s.id === sessionId
  );
  if (!session) return;

  const notes = prompt(
    "Enter session notes (optional):",
    session.notes || ""
  );
  if (notes === null) return;

  const name = prompt("Enter custom name (optional):", session.name);
  if (name === null) return;

  this.saveToPermanent(sessionId, notes, name);
}
```

**After:**

```javascript
saveToPermanentPrompt(sessionId) {
  const session = appState.logging.tempSessions.find(
    (s) => s.id === sessionId
  );
  if (!session) return;

  const name = prompt("Enter custom name (optional):", session.name);
  if (name === null) return;

  const notes = prompt(
    "Enter session notes (optional):",
    session.notes || ""
  );
  if (notes === null) return;

  this.saveToPermanent(sessionId, notes, name);
}
```

## Prompt Flow Comparison

### Before Fix

1. User clicks "Save" button
2. **First prompt:** "Enter session notes (optional):"
3. User enters notes (or leaves blank)
4. **Second prompt:** "Enter custom name (optional):"
5. User enters name (or leaves blank)
6. Session saved to permanent storage

### After Fix

1. User clicks "Save" button
2. **First prompt:** "Enter custom name (optional):"
3. User enters name (or leaves blank)
4. **Second prompt:** "Enter session notes (optional):"
5. User enters notes (or leaves blank)
6. Session saved to permanent storage

## Benefits

1. **Better Workflow:** Custom name is more important than notes for identification
2. **Consistency:** Name first, then additional notes
3. **User Experience:** Easier to identify sessions by name first

## Testing

To verify the fix:

1. Create a session in the LOGS tab
2. Click "Save" button on the session
3. Verify the first prompt asks for "Enter custom name (optional):"
4. Enter a name and click OK
5. Verify the second prompt asks for "Enter session notes (optional):"
6. Enter notes and click OK
7. Verify the session is saved to permanent storage with the correct name and notes

## Files Modified

- `Darkroom_Tools_v3.0.3.html` - ExposureLogManager.saveToPermanentPrompt() method

## Conclusion

✅ **The prompt order has been changed to show "Enter custom name" first, then "Enter session notes".**

This provides a more logical workflow where the user first identifies the session with a name, then adds additional notes if needed.
