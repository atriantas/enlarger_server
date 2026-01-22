# Quick Start: Fixed Auto-Gain + Manual Control

## The Problem (Solved)

Auto-gain was constantly switching, making lux readings jump around wildly. You couldn't get stable shadow/highlight readings.

## The Fix

✅ **Auto-gain is now DISABLED by default** - much more stable  
✅ **Enhanced hysteresis** - requires 3 consecutive readings before switching (if enabled)  
✅ **Manual gain control** - lock to specific gain level for your conditions

## How to Use

### Default Behavior (RECOMMENDED)

1. Open **METER** tab in browser
2. See new **SENSOR GAIN** section with buttons:

   ```
   AUTO  FIXED    ← Buttons (FIXED is selected by default)
   1x  25x  428x  MAX    ← Gain level buttons
   ```

3. **Choose gain for your light level**:
   - **1x** → Very bright (focus assist, well-lit enlarger)
   - **25x** → Standard darkroom (most common, recommended)
   - **428x** → Dim darkroom light, safelight only
   - **MAX (9876x)** → Very dark conditions

4. **Take reading**: Click 📷 READ button
5. **Add shadow reading**: Position sensor on shadow area → Click + ADD (repeat 3-5 times)
6. **Add highlight reading**: Position sensor on highlight area → Click + ADD (repeat 3-5 times)
7. **Capture**: Click CAPTURE for each reading type
8. **Calculate**: Results show exposure, grade, split recommendations

### Example Workflow

```
1. Set gain to 25x (standard)
   └─ Click "25x" button
   └─ Live display: "Gain: 25x"

2. Take shadow reading
   └─ Hold sensor on shadow area
   └─ Click "📷 READ" → See lux value
   └─ Click "+ ADD" 5 times (steady readings)
   └─ Click "CAPTURE" → Saved average

3. Take highlight reading
   └─ Hold sensor on highlight area
   └─ Click "📷 READ" → See lux value
   └─ Click "+ ADD" 5 times (steady readings)
   └─ Click "CAPTURE" → Saved average

4. View results
   └─ Exposure time shown
   └─ Grade filter recommended
   └─ Can send to Calculator tab
```

## Troubleshooting

### "Lux values keep changing"

- **Make sure you clicked the gain button** (e.g., "25x")
- Verify "FIXED" is selected (not "AUTO")
- Lux readings naturally fluctuate ±5% due to sensor noise (normal)
- If fluctuation >10%, try higher gain (e.g., 428x)

### "Reading is too bright (numbers in millions)"

- Click lower gain button (1x)
- Check that light isn't directly hitting sensor

### "Reading is too dark (0-10 lux)"

- Click higher gain button (428x or MAX)
- Make sure safelight is on
- Check sensor isn't in complete darkness

### "Gain keeps changing"

- Make sure FIXED button is selected (not AUTO)
- FIXED = manual gain locked (no auto-switching)
- AUTO = allows automatic switching (less stable, not recommended for metering)

## Advanced: Auto-Gain Mode (Optional)

If you want automatic gain switching (not recommended for meter readings):

1. Click "AUTO" button in SENSOR GAIN section
2. System will now auto-adjust as light changes
3. Takes ~3 consecutive readings before each gain change
4. Much more stable than before, but less predictable

**Use case**: If you're working with varying light conditions and want the system to adapt automatically.

## API Reference (for developers)

Set gain via HTTP:

```bash
# Lock to 25x gain
curl "http://192.168.4.1/meter/gain?action=25x"

# Enable auto-gain
curl "http://192.168.4.1/meter/gain?action=auto"

# Disable auto-gain
curl "http://192.168.4.1/meter/gain?action=disable"

# Response example:
{"message": "Gain set to 25x", "auto_gain": false, "gain": "25x"}
```

## FAQ

**Q: Why is auto-gain disabled by default now?**  
A: Darkroom metering requires stable readings. Auto-gain switching caused lux to jump around. Manual control is more predictable.

**Q: Can I still use auto-gain?**  
A: Yes, click "AUTO" button. It's now more stable (requires 3 readings before switching), but manual control is still recommended.

**Q: What gain should I use?**  
A: Start with 25x for standard darkroom. If readings look too noisy, try 428x.

**Q: Does this affect the CALC, SPLIT, or TIMER tabs?**  
A: No. This is only for the METER tab light sensor. All other functions unchanged.

**Q: Can I lock gain per paper profile?**  
A: Not yet. Set manually before each session. Future version may add this.

## Technical Notes

- Hysteresis buffer: ±5000 (prevents gain jitter)
- Stability threshold: 3 readings (wait for stable measurement)
- Default gain: 25x (medium, good for most darkrooms)
- Integration time: Auto-adjusted (100ms bright to 600ms dim)
- Noise filtering: 5-point median + 10-point moving average

---

**Last Updated**: 2026-01-20 | Version 1.0
