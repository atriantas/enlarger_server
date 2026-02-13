# Auto-Update Feature - Installation & Usage Guide

## Overview

The Darkroom Timer now supports automatic updates from GitHub! When you push new files to your GitHub repository, the Pico app can fetch and install updates automatically without needing manual file uploads via Thonny or ampy.

## How It Works

### High-Level Flow

```
Browser Settings Tab → "Check for Updates" Button
    ↓
HTTP GET /update-check
    ↓
UpdateManager checks GitHub API for latest release
    ↓
If newer version found:
  - Downloads all files from Back_Up branch
  - Safely writes with .tmp → atomic rename
  - Updates version.json
  - Auto-restarts Pico
    ↓
Browser reloads → New version active
```

### Key Features

✅ **No Authentication Required** - Uses public GitHub API (60 req/hr limit, plenty for manual checks)  
✅ **Safe Installation** - Downloads to .tmp files first, verifies size, then atomic rename  
✅ **Manual Control** - User clicks "Check for Updates" button (not automatic)  
✅ **Auto-Restart** - Pico restarts 3 seconds after successful update  
✅ **Version Tracking** - Stores version in `version.json` on Pico  
✅ **Memory Safe** - Uses chunked downloads (512-byte), calls `gc.collect()`  

---

## Installation (Already Done!)

The feature has been implemented across these files:

### Backend (Pico)

1. **`lib/update_manager.py`** (NEW)
   - Core update logic
   - Version checking and comparison
   - Safe file downloads and writes
   - GitHub API integration

2. **`lib/http_server.py`** (MODIFIED)
   - Added `update_manager` parameter to `__init__`
   - New endpoint: `GET /update-check`
   - Handler: `_handle_update_check()`

3. **`boot.py`** (MODIFIED)
   - Imports `UpdateManager`
   - Initializes with repo credentials
   - Passes to HTTPServer

4. **`version.json`** (NEW)
   - Current version: `1.0.0`
   - Tracks last check and update times

### Frontend (Browser)

5. **`index.html`** (MODIFIED)
   - New class: `UpdateStatusManager`
   - Update button in Settings tab
   - Progress bar and status display
   - Auto-reload on success

### Testing

6. **`test_update_manager.py`** (NEW)
   - Run with: `python3 test_update_manager.py`
   - Tests: version parsing, comparison, file list, URL building
   - All tests pass ✅

---

## Usage: How to Update the Pico

### Step 1: Prepare New Version on GitHub

1. Update files in your local workspace
2. Commit and push to `Back_Up` branch:
   ```bash
   git add .
   git commit -m "v1.0.1: Added new features"
   git push origin Back_Up
   ```

3. **Create a GitHub Release** (optional but recommended):
   ```
   Go to: https://github.com/atriantas/enlarger_server/releases/new
   - Tag: v1.0.1
   - Title: Version 1.0.1
   - Describe changes
   - Publish Release
   ```

### Step 2: Update on the Pico

1. Open the Darkroom Timer web interface
   - `http://192.168.4.1/` (hotspot mode)
   - `http://darkroom.local/` (WiFi router mode)

2. Go to **Settings** tab

3. Look for **"Check for Updates"** section at the bottom

4. Click **"Check for Updates"** button

5. Watch progress bar fill (downloading files)

6. See status message: "✓ Updated X files. Restarting..."

7. Automatically waits 3 seconds, then restarts Pico

8. Browser reloads → You're on the new version!

### Step 3: Verify Update

Check version display in Settings > "Check for Updates" section:
- Current version should match latest on GitHub
- Last check timestamp shows when it ran

---

## What Gets Updated

The following files are automatically updated:

```
boot.py                        (main entry point)
index.html                     (web UI, ~610KB)
lib/gpio_control.py            (relay control)
lib/http_server.py             (HTTP endpoints)
lib/light_sensor.py            (TSL2591X sensor)
lib/paper_database.py          (paper/filter database)
lib/splitgrade_enhanced.py     (Heiland algorithm)
lib/temperature_sensor.py      (DS1820 sensor)
lib/timer_manager.py           (timer logic)
lib/update_manager.py          (this update feature!)
lib/wifi_ap.py                 (hotspot mode)
lib/wifi_sta.py                (router mode)
```

---

## Technical Details

### Update Endpoint

**Request:**
```
GET http://darkroom.local/update-check
```

**Response (Success):**
```json
{
  "success": true,
  "current_version": "1.0.0",
  "latest_version": "1.0.1",
  "available": true,
  "updated_files": [
    "boot.py",
    "index.html",
    "lib/http_server.py"
  ],
  "updated_count": 3,
  "restart_required": true,
  "message": "Updated 3 files"
}
```

**Response (Already Up-to-Date):**
```json
{
  "success": true,
  "available": false,
  "current_version": "1.0.0",
  "latest_version": "1.0.0",
  "message": "Already on latest version"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Failed to connect to GitHub",
  "current_version": "1.0.0"
}
```

### Version Comparison

Versions are compared as tuples after parsing:
- `v1.0.0` → `(1, 0, 0)`
- `v2.1.3` → `(2, 1, 3)`
- Tuple comparison: `(2, 1, 3) > (2, 1, 0)` = True

### Safe File Write

Each file is written safely:
1. Download to `filename.tmp` first
2. Verify downloaded size matches expected
3. Remove old file (if exists)
4. Rename `.tmp` → final (atomic on filesystem)
5. Call `gc.collect()` to free memory

---

## Configuration

All configuration is in `boot.py`:

```python
# Update manager initialization (view/edit boot.py lines ~95-103)
self.update_manager = UpdateManager(
    repo_owner='atriantas',
    repo_name='enlarger_server',
    version_file='version.json'
)
```

To change repo/branch, edit boot.py:
- `repo_owner` - GitHub username/organization
- `repo_name` - Repository name
- Branch is hardcoded to `Back_Up` (edit in `lib/update_manager.py` line ~119)

---

## Troubleshooting

### "Check for Updates" Button Not Appearing?

1. **Clear browser cache:** Press Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Reload page:** F5
3. **Check browser console:** Press F12 → Console tab, look for errors

### Update Check Fails?

**Error: "UpdateManager not initialized"**
- Pico boot.py hasn't been updated with UpdateManager
- Re-upload boot.py to Pico via Thonny/ampy

**Error: "Failed to connect to GitHub"**
- WiFi not connected or blocked DNS
- Check WiFi Settings tab
- Verify Pico can reach internet

**Error: "File not found on GitHub"**
- File wasn't pushed to Back_Up branch
- Check branch name is exactly `Back_Up` (capital B and U)
- Verify files exist: `https://github.com/atriantas/enlarger_server/tree/Back_Up`

### Update Started But Pico Unresponsive?

- **Don't interrupt!** Pico is downloading files
- Takes 30-60 seconds for large files (index.html is 610KB)
- Progress bar shows download status
- Auto-restart after 3 seconds

### Successful Update But New Version Not Showing?

1. **Hard refresh browser:** Ctrl+Shift+R (clear cache)
2. **Check version.json on Pico:**
   - Via browser: Settings → "Current version" should show latest
3. **Manual restart:**
   - Power cycle Pico (remove USB, reconnect)
   - Or click "Force Hotspot Mode" then restart

### Want to Rollback (Go Back to Old Version)?

Currently, no automatic rollback. Options:

1. **Manual Restore:** Upload previous files via Thonny/ampy
2. **Git Revert:** On your computer:
   ```bash
   git revert <commit-hash>
   git push origin Back_Up
   ```
   Then click "Check for Updates" on Pico

---

## Testing the Feature

### Without Pico Hardware

Run the test suite (tests version logic without MicroPython):

```bash
python3 test_update_manager.py
```

Expected output: All ✓ tests pass

### With Pico Hardware

1. **Mock Test:** Check that `/update-check` endpoint is reachable:
   ```bash
   curl http://192.168.4.1/update-check
   ```

2. **Dry Run:** Click "Check for Updates" without making any GitHub changes
   - Should report: "Already on latest version"

3. **Real Update:**
   - Update a file on GitHub (e.g., add comment to boot.py)
   - Commit and push to `Back_Up` branch
   - Create a release tag `v1.0.1`
   - Click "Check for Updates" on Pico
   - Watch progress bar
   - Verify Pico restarts and new version is active

---

## How to Create a GitHub Release

1. Go to https://github.com/atriantas/enlarger_server
2. Click **"Releases"** (right sidebar)
3. Click **"Create a new release"** or **"Draft a new release"**
4. **Tag:** Enter version (e.g., `v1.0.1`)
5. **Title:** Short description (e.g., "Version 1.0.1 - Bug fixes")
6. **Description:** List changes
7. Click **"Publish release"**

Version tags are checked even if you don't attach file assets to the release. The Pico will download from the `Back_Up` branch using raw.githubusercontent.com URLs.

---

## FAQ

**Q: Can users without pushing to GitHub branches use this?**  
A: You must have push access to the `Back_Up` branch. Private repo users can set up personal access tokens for authentication (future enhancement).

**Q: Will this work with WiFi disconnected?**  
A: No. Pico must be connected to router (via saved WiFi) or can access GitHub. If only AP mode (hotspot), it cannot reach GitHub.

**Q: What if a file is corrupted after download?**  
A: The `.tmp` file is cleaned up automatically. Next update attempt will retry. No data loss.

**Q: Can I force users to update?**  
A: No, currently user-initiated. Future: could add auto-check on startup + optional "required update" flag.

**Q: How do I include release notes?**  
A: Add them to the GitHub release description. Currently, Pico doesn't display them, but you can add that feature later (would show in browser).

---

## Future Enhancements

Possible additions (not yet implemented):

- [ ] Auto-check for updates on boot (configurable)
- [ ] Required update flag (blocks certain features until updated)
- [ ] Release notes display in browser
- [ ] Automatic rollback if restart fails
- [ ] Partial update (only specific files)
- [ ] Schedule updates (e.g., every week)
- [ ] Signature verification for security
- [ ] Beta/Stable channel selection

---

## Files Modified/Created

| File | Type | Change |
|------|------|--------|
| `lib/update_manager.py` | NEW | Core update logic (432 lines) |
| `lib/http_server.py` | MODIFIED | Added UpdateManager parameter, /update-check endpoint |
| `boot.py` | MODIFIED | Initialize UpdateManager, pass to HTTPServer |
| `index.html` | MODIFIED | UpdateStatusManager class + Settings UI button |
| `version.json` | NEW | Version tracking config |
| `test_update_manager.py` | NEW | Test suite (all tests pass) |

---

## Summary

Your Darkroom Timer now has a complete auto-update system! Push changes to GitHub, click a button on the web interface, and the Pico automatically downloads, installs, and restarts with the new version.

**Next steps:**
1. Push this code to your `Back_Up` branch
2. Create a release tag (e.g., `v1.0.0`)
3. Deploy to Pico
4. Test by clicking "Check for Updates" in Settings tab
5. You're ready to ship updates! 🚀

---

For questions or bugs, check the copilot-instructions.md for full system documentation.
