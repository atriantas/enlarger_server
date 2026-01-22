# ⚡ Update Speed Quick Start

## TL;DR - Just Tell Me What To Do

**Problem**: Sensor updates are slow ❌  
**Solution**: New UPDATE SPEED control 🎉

### What Changed?

- **Before**: Always slow (2000ms delay)
- **After**: Choose your speed! (100-2000ms options)

### How to Use (30 seconds)

1. Open **METER** tab in browser
2. Scroll to **UPDATE SPEED** section
3. Click your preferred mode:
   - 🟢 **STABLE** - Smooth (use for reference)
   - 🟡 **BALANCED** - Recommended (use for metering) ⭐
   - 🔴 **FAST** - Instant (use for quick checks)

That's it!

---

## Three Modes Explained Simply

### 🟡 BALANCED (Default - Recommended)

```
Speed: ⚡⚡ (500-1000ms)
Smoothness: ✓✓ (very smooth)
Use: Normal metering ⭐

Why: Perfect balance. Updates in ~1 second, smooth results.
```

### 🟢 STABLE (Smoothest)

```
Speed: 🐌 (1500-2000ms)
Smoothness: ✓✓✓ (ultra-smooth)
Use: Reference comparison

Why: Ultra-stable readings, but slow.
```

### 🔴 FAST (Fastest)

```
Speed: ⚡⚡⚡ (100-200ms)
Smoothness: ✓ (may be noisy)
Use: Quick checks

Why: Instant response, but shows sensor noise.
```

---

## Real Examples

### Example 1: Metering

```
You: "I need to meter this negative"
Action:
  1. Open METER tab
  2. Mode should already be BALANCED (default)
  3. Position on shadow
  4. Click READ 5 times
  5. Click CAPTURE
  6. Position on highlight
  7. Click READ 5 times
  8. Click CAPTURE
Result: Done in 30 seconds!
```

### Example 2: Quick Check

```
You: "Is there enough light here?"
Action:
  1. Open METER tab
  2. Click FAST mode
  3. Move sensor around
  4. Watch lux change instantly
Result: Instant feedback!
```

### Example 3: Getting Reference

```
You: "I want a perfectly stable baseline"
Action:
  1. Open METER tab
  2. Click STABLE mode
  3. Hold sensor still
  4. Wait 2 seconds
  5. Read perfectly smooth value
Result: Rock-solid reference!
```

---

## Visual Comparison

```
Light changes: 100 → 1000 lux

FAST:    ▯▯▯▯▯▯▯▯▯ 100-200ms ✓ INSTANT
BALANCED: ▯▯▯▯▯▯▯▯▯▯▯▯▯▯ 500-1000ms ✓ QUICK
STABLE:   ▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯ 1500-2000ms ✓ SMOOTH
```

---

## Quick Decision Guide

Choose based on your task:

| Task             | Mode         | Reason                      |
| ---------------- | ------------ | --------------------------- |
| Meter a negative | **BALANCED** | Good speed + smooth results |
| Focus assist     | **FAST**     | Need instant feedback       |
| Compare readings | **STABLE**   | Need ultra-smooth           |
| General use      | **BALANCED** | Best all-around             |

---

## What Each Mode Does

### BALANCED (Recommended)

- Applies moving average filter (10 samples)
- Smooth results with ~1 second response time
- Best for normal darkroom metering
- Default setting

### STABLE

- Applies both median AND moving average filters
- Smoothest possible readings
- Takes ~2 seconds to respond
- Use when perfect stability matters

### FAST

- No filtering - raw sensor data
- Responds in ~100-200ms
- Shows sensor noise but very quick
- Use for quick light checks

---

## FAQ

**Q: Why isn't BALANCED faster by default?**  
A: Because metering needs smooth results to average. BALANCED is the sweet spot.

**Q: Can I damage the sensor using FAST mode?**  
A: No. FAST just disables filtering - completely safe.

**Q: Should I always use STABLE?**  
A: No, it's too slow for normal use. Use BALANCED (default).

**Q: Does switching modes clear my readings?**  
A: Yes, filters reset when you change modes. That's OK.

**Q: Can I use FAST for metering?**  
A: Not recommended - results will be noisier. Use BALANCED for metering.

---

## API Commands

If you want to control it via HTTP:

```bash
# Set to BALANCED (default, recommended)
curl "http://darkroom.local/meter/response-mode?mode=balanced"

# Set to FAST (quick checks)
curl "http://darkroom.local/meter/response-mode?mode=fast"

# Set to STABLE (smooth reference)
curl "http://darkroom.local/meter/response-mode?mode=stable"
```

---

## You're All Set!

✅ **Feature**: UPDATE SPEED control is ready  
✅ **Default**: BALANCED mode (good for everything)  
✅ **Alternative**: FAST mode (instant checks), STABLE mode (smooth)

### Next Steps:

1. Deploy updated files to Pico
2. Open METER tab
3. Try different modes
4. Pick your favorite (probably BALANCED)
5. Enjoy faster updates! ⚡

---

For more details, see **FAST_RESPONSE_MODE.md** or **BEFORE_AFTER_UPDATE_SPEED.md**
