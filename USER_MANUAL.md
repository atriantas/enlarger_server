# Darkroom Timer & Tools - Professional User Guide

**Version:** 3.0.3  
**Application:** Professional Darkroom Exposure Timer & Darkroom Management System

---

## Welcome to Darkroom Timer & Tools

### Your Complete Darkroom Workflow Solution

Darkroom Timer & Tools is designed to be your darkroom's command center. It combines precision timing, exposure calculation, chemical management, and hardware control into a single, integrated system. This guide will help you understand not just _how_ to use each feature, but _why_ it's designed the way it is, and how to build efficient workflows that produce consistent, professional results.

### The Philosophy: Precision, Integration, and Workflow

**Precision**: Every timing function uses millisecond-accurate drift-corrected timers. F-stop calculations maintain photographic precision. No compromises.

**Integration**: All features work together seamlessly. Test strip results flow into exposure calculations. Hardware control integrates with timing. Chemical tracking connects to your workflow.

**Workflow**: The application is organized to match how you actually work in the darkroom—from test strips to final exposures, from setup to cleanup.

### Quick Start: Your First Exposure

If you're new to the system, here's the essential workflow:

1. **CALC Tab**: Set base time (10s), select increment (1/3 stop), adjust stop slider
2. **CONTROL Tab**: Verify server connection, test safelight auto-off
3. **Start Exposure**: Click Start → Countdown begins → Exposure runs → Completes with beep
4. **Review**: Check results, adjust as needed

That's it. The system handles all the technical details—you focus on your image.

---

## SETTINGS Tab - System Configuration

The SETTINGS tab is your command center for customizing how the system behaves. Think of it as setting up your darkroom's "operating parameters" once, so every subsequent session works exactly the way you want.

### Why These Settings Matter

Every darkroom is different. Different developers, different paper sizes, different working rhythms. These settings let you tailor the system to _your_ darkroom, not force you to adapt to the software.

### Sound Settings: Your Audio Feedback System

**The Philosophy**: In a darkroom, you often can't look at a screen. Audio feedback lets you work confidently without constant visual checking.

- **Calc Warning Beep**: Gives you a 3-second heads-up before exposure ends. You can prepare to stop the exposure or get ready for the next step.
- **Calc End Beep**: Confirms exposure completion with a distinct pattern. No guessing if it finished.
- **Timer Warning Beep**: Same concept for chemistry timers. You'll hear when developer is about to finish, so you can prepare the stop bath.
- **Timer End Beep**: Confirms timer completion. You can work in another part of the darkroom and still know when to act.

**Recommended**: Enable all four for maximum workflow awareness.

### Countdown Settings: Your Preparation Window

**The Philosophy**: Rushing leads to mistakes. A countdown gives you time to position paper, cover your eyes, or make final adjustments.

- **Countdown Delay**: 0-30 seconds. Most users prefer 5 seconds. This is enough time to get ready without feeling rushed.
- **Countdown Beep**: Master switch. If you prefer silence, disable all countdown audio.
- **Countdown Pattern**: Choose based on your preference:
  - **every-second**: Constant feedback, builds anticipation
  - **last3**: Minimal but sufficient warning
  - **last5**: Early warning, then quiet focus
  - **none**: Silent operation (not recommended for beginners)

**Workflow Tip**: Use "last3" pattern. It gives you the first 2 seconds of silence (for final positioning), then audible warnings for the last 3 seconds.

### Timer Settings: Chemistry Automation

**The Philosophy**: Chemistry timing is critical but repetitive. Automate the chain so you can focus on handling paper, not buttons.

- **Default Times**: Set your standard processing times once. These load automatically every session.

  - Developer: 60 seconds (typical)
  - Stop Bath: 30 seconds (typical)
  - Fixer: 60 seconds (typical)
  - Final Wash/Flo: 30 seconds (typical)

- **Auto-Start**: The game-changer. When enabled:

  1. You start the Developer timer
  2. System counts down, beeps
  3. Automatically starts Stop timer
  4. Continues through Fixer and Flo
  5. You just move paper from tray to tray

  **Without Auto-Start**: You manually start each timer, watch for completion, then start the next.

- **Default Photo Flo**: When disabled, Flo timer won't auto-start. Useful if you only use it for certain workflows.

**Recommended**: Enable Auto-Start. This transforms timer management from 4 separate tasks into 1 continuous workflow.

### Test Strip Settings: Automated Test Strips

**The Philosophy**: Test strips should be systematic and repeatable. Manual test strips often have inconsistent timing between steps.

- **Auto-Advance**: When enabled, test strip steps progress automatically. Set it, start it, walk away.
- **Auto-Advance Delay**: Time between steps.
  - 1 second: Fast progression, good for quick evaluation
  - 3-5 seconds: Gives you time to glance at each step
  - 10 seconds: Thorough evaluation time

**Workflow Tip**: Use 3-second delay. It's fast enough to maintain momentum but gives you time to evaluate each step before the next begins.

### Hardware Settings: Safety and Precision

**The Philosophy**: Hardware control must be safe, automatic, and precise. You shouldn't have to manually manage safelights or remember f-stop math.

- **Safelight Auto-Off**: **CRITICAL SAFETY FEATURE**

  - What it does: Automatically turns off safelight when enlarger starts, restores it after exposure
  - Why it matters: Safelight fogging ruins prints. This eliminates human error
  - How it works: Remembers safelight state → turns it off → starts exposure → waits 0.5s → restores safelight
  - **Always enable this unless you have a specific reason not to**

- **Stop Denominator**: Determines f-stop increment size

  - **2 (1/2 stops)**: Coarse adjustments. Good for beginners learning f-stops
  - **3 (1/3 stops)**: Standard photographic increments. Most precise for test strips
  - **4 (1/4 stops)**: Very fine adjustments. For critical work

  **Recommendation**: Use 3 (1/3 stops). It's the industry standard and provides excellent precision without excessive steps.

### Base Time Limits: Range Control

**The Philosophy**: Limit sliders to your working range to avoid accidental extreme values and make fine adjustments easier.

- **Calculator Min/Max**: If you never expose less than 2 seconds or more than 30 seconds, set these limits. The slider becomes more sensitive in your actual working range.
- **Test Strip Min/Max**: Separate limits for test strips. Test strips often use different base times than final exposures.

**Example**: If your typical base time is 10 seconds, setting min=5 and max=20 makes the slider much more precise in that range.

### Color Scheme: Visual Comfort

**The Philosophy**: Different lighting conditions require different visual approaches.

- **Dark**: Original scheme. Designed for darkroom use with red accents that preserve night vision
- **Light**: For working with safelights on or in brighter conditions
- **Day**: For daytime use or when you need to reference the app with normal lighting

**Recommendation**: Use Dark in the darkroom, Light for setup/cleanup, Day for planning.

### Data Management: Backup and Restore

**The Philosophy**: Your time and settings are valuable. Never lose them.

- **Export All Data**: Creates a complete backup of:

  - All timer profiles
  - Chemical presets and capacity data
  - Shelf-life tracking
  - Custom filter banks
  - All settings and preferences

  **When to use**: Before software updates, periodically (monthly), or before major workflow changes

- **Import All Data**: Restores everything from a backup file

- **Reset All Settings**: Nuclear option. Returns to factory defaults. Use only if everything is broken.

**Best Practice**: Export your data after any significant configuration change. Store the file somewhere safe (cloud storage, email to yourself).

---

## Understanding the Workflow Philosophy

### The Three-Phase Workflow

Darkroom Timer & Tools is designed around a natural three-phase workflow:

**Phase 1: Setup & Testing** (TEST tab)

- Determine correct exposure through systematic test strips
- Click-to-apply results to CALC tab
- Save successful configurations as profiles

**Phase 2: Production** (CALC & TIMER tabs)

- Use calculated exposures for final prints
- Automate chemistry timing with Auto-Start
- Focus on print quality, not timing

**Phase 3: Management** (CHEMICAL tab)

- Track developer capacity
- Monitor chemical shelf-life
- Plan maintenance and reordering

### Integration Philosophy

Each tab feeds into the others:

- **TEST → CALC**: Click test strip step → applies to CALC base time
- **CALC → CONTROL**: Start exposure → triggers hardware
- **TIMER → CHEMICAL**: Track prints processed → update capacity
- **SETTINGS → EVERYTHING**: Configure once, use everywhere

This eliminates redundant data entry and reduces errors.

### Precision Philosophy

- **F-stops, not linear time**: F-stops maintain consistent density relationships
- **Millisecond accuracy**: No rounding errors accumulate
- **Drift correction**: JavaScript timers drift; this system compensates
- **Visual + audio feedback**: Multiple confirmation methods

### Safety Philosophy

- **Automatic safelight control**: Eliminates forgetfulness
- **Countdown warnings**: Prevents surprises
- **Status displays**: Always know what's happening
- **Graceful shutdown**: Hardware turns off safely

---

## TEST Tab - F-Stop Test Strip Generator

### The Problem Test Strips Solve

Every paper, every enlarger, every negative is different. You can't just "know" the correct exposure. You need to test.

Traditional test strips:

- Manual timing (inconsistent)
- Guesswork about increment size
- Difficult to reproduce exact results
- No record of what you did

**This system solves these problems through automation and precision.**

### How It Works: The Science

**F-Stop Principle**: Each stop doubles or halves light. Between stops, the math is precise:

- 1/3 stop = 1.19× multiplier
- 2/3 stop = 1.41× multiplier
- 1 stop = 2× multiplier

**Why this matters**: If your test strip shows step 3 is perfect, and you used 1/3 stop increments, you know your final exposure should be 1.19× your base time. This is mathematically precise, not guesswork.

### Core Controls Explained

**Base Time**: Your starting point. This is typically a guess or previous experience.

- **How to choose**: Start with what you think is close. The system will refine it.
- **Typical range**: 5-20 seconds for most enlarger setups

**Step Increment**: Size of each step in fractional stops.

- **1/3 stop (recommended)**: Industry standard. Provides good resolution without too many steps
- **1/2 stop**: Faster, coarser. Good for initial rough tests
- **1/4 stop**: Very fine resolution. Use when you're very close to final exposure

**Number of Steps**: How many strips to generate.

- **5-6 steps**: Standard test strip range
- **7-8 steps**: When you're very uncertain about exposure
- **4 steps**: Quick test when you're close

**Method**: Two calculation approaches

**Cumulative Method** (Recommended for test strips):

- Each step adds to the previous total
- Creates a continuous gradient
- Best for finding the "sweet spot"
- Example: 10s base, 1/3 stop, 6 steps
  - Step 1: 10s
  - Step 2: 11.9s (total)
  - Step 3: 14.2s (total)
  - Step 4: 16.9s (total)
  - Step 5: 20.1s (total)
  - Step 6: 23.9s (total)

**Incremental Method**:

- Each step independent from base
- All steps calculated from original base
- Best for comparing multiple exposures to same base
- Example: 10s base, 1/3 stop, 6 steps
  - Step 1: 10s
  - Step 2: 11.9s
  - Step 3: 14.1s
  - Step 4: 16.8s
  - Step 5: 20s
  - Step 6: 23.8s

**Auto-Advance**: Hands-off operation

- When enabled: System progresses automatically
- When disabled: You manually advance each step
- **Use case**: Enable for routine tests, disable when evaluating each step carefully

**Auto-Advance Delay**: Time between steps

- **1-2 seconds**: Fast-paced testing
- **3-5 seconds**: Standard (recommended)
- **6-10 seconds**: Thorough evaluation time

### Visual Test Strip Preview

**What you see**: Horizontal bars representing each step, with time and stop value displayed.

**Interactive features**:

- **Click any step**: Sends that step's total time to CALC tab for fine-tuning
- **Active highlight**: Shows current step during execution
- **Theme-aware colors**: Adapts to your chosen color scheme

**Why this matters**: Visual confirmation before you start. You see exactly what sequence will run.

### Timer Controls: Execution

**Start Test**: Begins the sequence

1. Countdown (if enabled)
2. First step exposure
3. Safelight restores
4. Wait for evaluation or auto-advance
5. Next step...

**Stop Test**: Immediate halt

- Use if you see a problem
- Use if you found your answer early
- Use if you need to adjust something

**Reset**: Returns to beginning

- Clears current progress
- Ready to start fresh
- Settings remain unchanged

**Next Step**: Manual advancement

- Only available when paused or stopped
- Gives you control when you need it
- Use with Auto-Advance disabled for maximum control

### Profile Management: Save Your Work

**Why save profiles?**:

- Repeat tests without reconfiguring
- Document successful configurations
- Share settings with others
- Build a library of paper/exposure combinations

**Save Profile**:

- Name it descriptively: "Ilford MGIV 8x10 1/3stop"
- Saves: base time, increment, steps, method, auto-advance settings

**Load Profile**:

- One-click restoration
- Instant recall of successful configurations

**Clear Profiles**:

- Housekeeping when list gets long
- Removes outdated configurations

### Complete Test Strip Workflow

**Step 1: Initial Setup**

1. Go to TEST tab
2. Set base time (guess or use previous experience)
3. Choose increment (1/3 stop recommended)
4. Select number of steps (6 is standard)
5. Choose method (Cumulative for test strips)
6. Decide on auto-advance (enable for routine work)

**Step 2: Visual Review**

1. Look at the preview bars
2. Verify the sequence makes sense
3. Check that times are in reasonable range
4. Adjust if needed

**Step 3: Execute Test**

1. Click Start Test
2. System counts down (5 seconds default)
3. First step exposes
4. Safelight restores
5. Evaluate the step
6. Either:
   - Wait for auto-advance (3 seconds)
   - Click Next Step manually
   - Click Stop if you found the answer

**Step 4: Find Your Answer**

1. Identify which step looks best
2. Click that step in the preview
3. System switches to CALC tab
4. That step's time is now the base time

**Step 5: Fine-Tune (Optional)**

1. In CALC tab, make small adjustments
2. Test the final exposure
3. Save as profile if successful

**Step 6: Document**

1. Save the test strip profile
2. Note the paper, enlarger height, filter, etc.
3. Build your reference library

### Advanced Tips

**When to use Incremental vs Cumulative**:

- **Cumulative**: Standard test strips, finding optimal exposure
- **Comparing different papers**: Use incremental
- **Testing specific exposures**: Use incremental

**Multiple test strips**:

- Run one test to find approximate range
- Adjust base time based on results
- Run second test with narrower range
- Repeat until you have precise answer

**Paper size considerations**:

- Test strips should be same paper as final print
- Different papers have different contrast responses
- Always test with the paper you'll use

---

## CALC Tab - Exposure Calculator & Incremental Timer

### The Problem It Solves

Once you know your base exposure, you need to:

1. Calculate adjusted times for different stops
2. Execute exposures precisely
3. Manage dodging/burning sequences
4. Adjust for physical changes (height, aperture, paper size)

This tab handles all of this.

### Main Controls: Basic Exposure Calculation

**Base Time Slider**: Your reference exposure

- Range: 0.4-50 seconds (configurable in SETTINGS)
- Fine adjustment: Use small movements
- Quick adjustment: Click slider track to jump

**Stop Increment Selector**: Choose your increment size

- Matches SETTINGS denominator
- Affects how the stop slider behaves
- 1/3 stop is standard

**Stop Slider**: Add or subtract stops

- Range: Typically -2 to +2 stops
- Negative values: Less exposure (darker)
- Positive values: More exposure (lighter)
- Real-time calculation updates display

**Result Display**: Shows calculated time and stop value

- **Result Time**: Final calculated exposure
- **Stop Value**: Current stop adjustment
- Updates instantly as you move sliders

### Incremental Exposure Mode: Dodging & Burning

**The Philosophy**: Complex exposures need step-by-step execution. This mode tracks your progress and calculates cumulative times automatically.

**State Tracking**:

- **Current Step**: Which step you're on (starts at 1)
- **This Exposure**: Time for current step only
- **Total Time**: Cumulative time across all steps
- **Accumulated Time**: Previous total before current step

**Why this matters**: When dodging or burning, you need to know:

- How long has the print been exposed so far?
- How long for this specific step?
- What's the total when done?

**Controls**:

- **Start**: Begins countdown then exposure
- **Stop**: Pauses current exposure (you can resume)
- **Reset**: Returns to step 1, clears all accumulated time
- **Next Step**: Adds current increment to total, advances step counter
- **Repeat**: Repeats the last exposure time exactly

**Complete Dodging/Burning Example**:

You're printing a landscape with a bright sky. Your base exposure is 10 seconds, but the sky needs 2 stops less (burning in the sky would be 4 stops more, so you dodge it).

**Workflow**:

1. Set base: 10s, increment: 1/3 stop
2. Step 1 (base exposure): Start → 10s → Stop
   - Current: 1, This: 10s, Total: 10s, Accumulated: 0s
3. Click Next Step
   - Current: 2, This: 11.9s, Total: 11.9s, Accumulated: 10s
4. Step 2 (dodge sky): Start → 11.9s → Stop
   - Sky gets 10s (base) - 11.9s (dodge) = 1.9s less exposure
5. Click Next Step
   - Current: 3, This: 14.2s, Total: 14.2s, Accumulated: 11.9s
6. Step 3 (full exposure): Start → 14.2s → Stop
   - Print gets full 14.2s total

**Result**: Sky gets 10s, foreground gets 14.2s. Perfect balance.

### Height Calculator: Adjusting for Physical Changes

**The Problem**: You change enlarger height, lens aperture, paper size, or filter grade. How do you calculate the new exposure time?

**The Formula** (built into the calculator):

```
New Time = Original Time × (Height Ratio)² × (Aperture Ratio)² × (Area Ratio)² × Filter Factor
```

**Why squared?**: Light follows inverse square law. Double the distance = 1/4 the light.

**Input Fields**:

**Original Height / New Height**:

- Measure from negative to paper
- Example: Original 8", new 10"
- Ratio: 10÷8 = 1.25
- Factor: 1.25² = 1.56 (56% more time needed)

**Original F-Stop / New F-Stop**:

- Lens aperture values (f/8, f/5.6, etc.)
- Example: Original f/8, new f/5.6
- Ratio: 5.6÷8 = 0.7
- Factor: 0.7² = 0.49 (49% of original time)

**Original Paper Area / New Paper Area**:

- Width × Height in square inches
- Example: Original 8×10 (80 sq in), new 11×14 (154 sq in)
- Ratio: √154÷√80 = 1.39
- Factor: 1.39² = 1.93 (93% more time needed)

**Filter Factor**:

- Contrast filter multiplier
- Grade 2 = 1.0 (baseline)
- Grade 4 = 1.5 (50% more time)
- Grade 0 = 0.7 (30% less time)

**Example Calculation**:

- Original: 10s at 8" height, f/8, 8×10 paper, Grade 2
- New: 10" height, f/5.6, 11×14 paper, Grade 4
- Height: (10÷8)² = 1.56
- Aperture: (5.6÷8)² = 0.49
- Area: (√154÷√80)² = 1.93
- Filter: 1.5
- Result: 10 × 1.56 × 0.49 × 1.93 × 1.5 = 22.5 seconds

**Why use this?**:

- Saves hours of test strips
- Accurate to within 5-10%
- Perfect for moving between paper sizes
- Essential for filter changes

### Custom Filter Banks

**The Philosophy**: Every printer has favorite contrast settings. Save them for quick recall.

**Structure**: 3 groups (A, B, C) × 12 slots (Grade 00-5)

**Use cases**:

- Group A: Your standard papers
- Group B: Your variable contrast papers
- Group C: Experimental or special papers

**Each slot**: Label + filter factor

- Example: "Grade 3 - 1.25" (25% more time than Grade 2)

**Integration**: These values feed directly into the Height Calculator's Filter Factor field.

---

## CALC Tab - Exposure Calculator - Deep Dive

The CALC tab calculates exposure times using f-stop increments and manages incremental exposures.

### Main Controls

**Base Time Slider**: Your reference exposure time (0.4-50 seconds)

**Stop Increment Selector**: Choose 1/2, 1/3, or 1/4 stop increments

**Stop Slider**: Select stops to add/subtract from base (typically -2 to +2 stops)

**Result Display**: Shows calculated time and stop value

### Incremental Exposure Mode

This is for step-by-step exposure work (dodging/burning sequences):

**State Tracking**:

- **Current Step**: Which step you're on (starts at 1)
- **This Exposure**: Time for current step only
- **Total Time**: Cumulative time across all steps
- **Accumulated Time**: Previous total before current step

**Controls**:

- **Start**: Begins countdown then starts exposure
- **Stop**: Pauses current exposure
- **Reset**: Returns to step 1, clears accumulated time
- **Next Step**: Adds current increment to total, advances step counter
- **Repeat**: Repeats the last exposure time

**Example Workflow**:

1. Base: 10s, Increment: 1/3 stop
2. Start exposure for 10s (step 1)
3. Stop at 8s (you decide it's enough)
4. Click Next Step → step 2, this exposure: 11.9s, total: 11.9s
5. Start exposure for 11.9s
6. Stop at full time
7. Click Next Step → step 3, this exposure: 14.2s, total: 14.2s
8. Continue for dodging/burning sequence

### Height Calculator

Below main calculator, adjusts exposure time based on physical changes:

**Input Fields**:

- **Original Height**: Current enlarger height
- **New Height**: Proposed new height
- **Original F-Stop**: Current lens aperture
- **New F-Stop**: Proposed new aperture
- **Original Paper Area**: Current paper size (sq inches)
- **New Paper Area**: New paper size (sq inches)
- **Filter Factor**: Contrast filter multiplier

**Formula**:

```
New Time = Original Time × (New Height ÷ Original Height)²
           × (New F-Stop ÷ Original F-Stop)²
           × (√New Area ÷ √Original Area)²
           × Filter Factor
```

**Example**:

- Original: 10s, 8" height, f/8, 8×10 paper
- New: 10" height, f/5.6, 11×14 paper, filter factor 1.5
- Height factor: (10÷8)² = 1.56
- Aperture factor: (5.6÷8)² = 0.49
- Area factor: (√154÷√80)² = 1.93
- Filter factor: 1.5
- Result: 10 × 1.56 × 0.49 × 1.93 × 1.5 = 22.5 seconds

### Custom Filter Banks

Three groups (A, B, C) with 12 slots each (Grade 00 through Grade 5). Each slot has a filter factor that feeds into the height calculator.

---

## TIMER Tab - Chemistry Management

### The Problem It Solves

Chemistry timing is critical but tedious:

- Developer too short = weak highlights
- Developer too long = excessive contrast, grain
- Stop bath too short = developer carryover
- Fixer too short = archival problems
- You have to watch the clock constantly

**Solution**: Automate the entire chain so you can focus on handling paper, not watching timers.

### Four Independent Timers

Each timer is identical in function but serves a different purpose:

**Dev (Developer)**: Most critical timing

- Typical: 60 seconds (varies by developer)
- Accuracy: ±1 second maximum
- Warning: Last 3 seconds beep

**Stop (Stop Bath)**: Short but important

- Typical: 30 seconds
- Purpose: Neutralize developer
- Can be shorter (15-20s) with vigorous agitation

**Fix (Fixer)**: Archival critical

- Typical: 60 seconds minimum
- Double-fix for archival work: 2×60s
- This timer handles one cycle

**Flo (Final Wash/Flo)**: Water conservation

- Typical: 30 seconds to 2 minutes
- Can be automated or manual
- Often skipped in water-saving workflows

### Timer States & Visual Feedback

**Ready (Normal)**:

- Gray background
- Shows default time
- Ready to start

**Running**:

- Border turns accent color (red in dark mode)
- Background lightens
- Countdown updates in real-time
- Last 3 seconds: flashing warning

**Warning (Last 3 Seconds)**:

- Rapid flashing
- Audio beep pattern
- Prepares you for completion

**Complete**:

- Border accent
- Background changes
- Completion beep plays
- Ready for next timer (if Auto-Start enabled)

**Disabled**:

- Grayed out
- Excluded from auto-chain
- Manual control only

### Auto-Start: The Game Changer

**Without Auto-Start**:

1. Start Dev timer → watch → beep → stop
2. Move paper to stop bath
3. Start Stop timer → watch → beep → stop
4. Move paper to fixer
5. Start Fix timer → watch → beep → stop
6. Move paper to wash
7. Start Flo timer → watch → beep → stop
8. **Total attention required: 4 separate tasks**

**With Auto-Start**:

1. Start Dev timer
2. Move paper to stop bath when Dev beeps
3. Move paper to fixer when Stop beeps
4. Move paper to wash when Fix beeps
5. **Total attention required: 1 task (starting Dev)**

**Time saved**: 3 button presses per print × 20 prints = 60 actions eliminated

**Attention saved**: You can focus on handling paper cleanly, not watching clocks

### Profile Management

**Why save timer profiles?**:

- Different developers need different times
- Different paper sizes may need different times
- You may have multiple darkrooms or setups
- Documentation for reproducibility

**Example profiles**:

- "Dektol 8x10": Dev 60s, Stop 30s, Fix 60s, Flo 30s
- "Dektol 11x14": Dev 75s, Stop 30s, Fix 90s, Flo 60s
- "Pyro 4x5": Dev 90s, Stop 45s, Fix 120s, Flo 120s

### Complete Chemistry Workflow

**Setup**:

1. Load appropriate timer profile
2. Verify Auto-Start is enabled in SETTINGS
3. Prepare all trays with chemistry
4. Have paper ready

**Execution**:

1. Click Start on Dev timer
2. System counts down (5s default)
3. Dev timer runs (60s)
4. Dev beeps → move paper to stop bath
5. Stop automatically starts (30s)
6. Stop beeps → move paper to fixer
7. Fix automatically starts (60s)
8. Fix beeps → move paper to wash
9. Flo automatically starts (30s)
10. Flo beeps → process complete

**During this time**: You handle paper. System handles timing.

### Advanced Timer Features

**Manual Adjustment**:

- ±1 buttons: Fine-tune while running
- ±10 buttons: Quick adjustment
- Use if you need to extend/shorten mid-run

**Reset**:

- Returns to default time
- Clears any adjustments
- Ready for next use

**Enable/Disable Toggle**:

- Exclude specific timers from chain
- Use if you don't need certain steps
- Example: Skip Flo if you do final wash separately

---

## CONTROL Tab - Hardware Integration

### The Problem It Solves

You have hardware (enlarger, safelight, ventilation, white light) that needs control. Manual switches are fine, but integration with timing creates powerful automation.

### Server Configuration

**Server IP**: Your Raspberry Pi's network address

- Find it: On Pi, run `hostname -I`
- Typical: 192.168.1.100 or similar
- Must be accessible from your browser device

**Server Port**: Flask server port

- Default: 5000
- Can be changed if needed
- Must match server configuration

**Test Connection**: Verify communication

- Sends /ping request
- Returns "OK" if working
- **Always test before starting work**

### Relay Controls: Individual Hardware

**Relay 1 - Enlarger Timer (GPIO 25)**:

- Primary exposure control
- Active-LOW: Button shows "ON" when GPIO is LOW (relay energized)
- Connects to enlarger power
- Used by CALC, TEST, and TIMER tabs

**Relay 2 - Safelight (GPIO 17)**:

- Controls safelight power
- Auto-controlled during exposure (if enabled)
- Critical for safety
- Should be normally ON, turns OFF during exposure

**Relay 3 - Ventilation (GPIO 27)**:

- Manual control for ventilation
- Not auto-controlled
- Use for clearing fumes between sessions

**Relay 4 - White Light (GPIO 22)**:

- Manual control for white light
- Not auto-controlled
- Use for inspection, loading paper

### System Controls

**Test Timer Relay**: Quick exposure test

- Enter duration in seconds
- Click to trigger enlarger
- Use for calibration or testing

**All Relays On/Off**: Master control

- Emergency stop: All Off
- Setup: All On (for inspection)
- Use sparingly

**Shutdown Pi**: Graceful system shutdown

- Sends shutdown command to Raspberry Pi
- 3-second delay for safety
- Wait for Pi to fully shut down before power off

**Reboot Pi**: System restart

- Use if server becomes unresponsive
- 3-second delay
- Wait for full reboot

### Auto-Trigger & Safelight Integration

**Auto-Trigger**:

- When enabled: Any timer start triggers enlarger
- When disabled: Manual control only
- **Always enable for integrated workflow**

**Safelight Auto-Off**:

- **CRITICAL SAFETY FEATURE**
- What happens:

  1. Timer starts (CALC, TEST, or TIMER)
  2. System checks safelight state
  3. If ON, remembers state
  4. Turns safelight OFF
  5. Starts enlarger timer
  6. After exposure + 0.5s buffer
  7. Restores safelight to previous state

- **Why 0.5s buffer?**: Prevents light leaks during transition
- **Why it matters**: Safelight fogging ruins prints. This eliminates human error.

### Status Display

Shows real-time state of all four relays and connection status. Use this to verify everything is working before starting critical work.

### Hardware Setup Checklist

**Before first use**:

1. ✓ Raspberry Pi running Flask server
2. ✓ Relays properly wired (active-LOW)
3. ✓ Enlarger connected to Relay 1
4. ✓ Safelight connected to Relay 2
5. ✓ IP address and port configured
6. ✓ Test Connection successful
7. ✓ Safelight Auto-Off enabled
8. ✓ Test each relay manually

**Safety verification**:

- Safelight turns OFF when enlarger starts
- Safelight restores after exposure
- Enlarger turns OFF if timer stops
- All relays respond to manual controls

---

## CHEMICAL Tab - Chemistry Management

### The Problem It Solves

Darkroom chemistry is expensive and time-sensitive. You need to:

- Mix dilutions correctly
- Track how much you've used
- Know when to replace
- Monitor expiration dates

This tab handles all chemical management.

### Mix Calculator: Precise Dilutions

**The Philosophy**: Wrong dilutions ruin chemistry and waste money. Precision matters.

**Inputs**:

- **Total Volume**: What you need (e.g., 1000ml)
- **Stock Parts**: Concentrated chemical ratio (e.g., 1)
- **Water Parts**: Diluent ratio (e.g., 3)

**Calculation**:

```
Stock = Total × (Stock ÷ (Stock + Water))
Water = Total × (Water ÷ (Stock + Water))
```

**Example**: 1000ml of 1+3 dilution

- Stock = 1000 × (1÷4) = 250ml
- Water = 1000 × (3÷4) = 750ml

**Why use this?**:

- Eliminates math errors
- Works for any dilution
- Scales to any volume
- Perfect for mixing fresh chemistry

### Chemical Presets: Save Common Recipes

**Why save presets?**:

- One-click mixing for frequently used chemistry
- Prevents mistakes
- Documents your recipes
- Shares with others

**Example presets**:

- "Dektol 1+2": Stock 1, Water 2
- "Stop Bath 1+63": Stock 1, Water 63
- "Fixer 1+4": Stock 1, Water 4

### Developer Capacity Tracker: Usage Monitoring

**The Problem**: Developer exhausts with use. Each print consumes developer capacity. Without tracking, you risk weak development.

**The Science**: Developer capacity is measured in ml per 8×10 equivalent. Typical values:

- Dektol: 50-80ml per 8×10
- Selectol: 40-60ml per 8×10
- Pyro: 100-150ml per 8×10

**Inputs**:

- **Paper Size**: Standard or custom
- **Number of Prints**: How many you've processed
- **Tray Volume**: Total developer in tray
- **Capacity**: ml per 8×10 (from manufacturer or experience)

**Calculation**:

```
Paper Area = Width × Height (sq inches)
Max Prints = (Capacity × Tray Volume ÷ 1000) ÷ (Paper Area ÷ 80)
Remaining = Max Prints - Prints Processed
```

**Example**:

- Developer: Dektol (60ml/8×10)
- Tray: 500ml
- Paper: 8×10 (80 sq in)
- Prints: 15
- Max = (60 × 500 ÷ 1000) ÷ (80 ÷ 80) = 30 prints
- Remaining = 30 - 15 = 15 prints

**Alerts**:

- > 20% remaining: Green (OK)
- 10-20%: Yellow (Warning)
- <10%: Red (Replace soon)

**Why this matters**:

- Prevents weak development mid-session
- Avoids wasting prints on exhausted developer
- Plans reordering
- Documents actual capacity vs theoretical

### Shelf-Life Tracker: Expiration Management

**The Problem**: Chemistry expires. Using expired chemistry produces unpredictable results. You need to track when bottles were opened.

**Inputs**:

- **Chemical Name**: Descriptive (e.g., "Dektol - Tray 1")
- **Date Opened**: When you first opened the bottle
- **Shelf Life**: Days until expiration (from manufacturer)

**Calculation**:

```
Days Remaining = (Date Opened + Shelf Life) - Today
```

**Visual Indicators**:

- **>30 days**: Green background (Good)
- **15-30 days**: Yellow background, warning border (Use soon)
- **<15 days**: Orange background, bold text (Replace now)
- **≤0 days**: Red background, pulsing animation (Expired - DO NOT USE)

**Typical shelf lives**:

- Liquid developers: 3-6 months opened
- Powder developers: 1-2 years unopened, 6 months mixed
- Stop bath: 6-12 months
- Fixer: 6-12 months
- Hypo clearing agent: 6 months

**Why this matters**:

- Prevents using expired chemistry
- Ensures consistent results
- Plans purchasing
- Avoids wasted paper and time

### Complete Chemical Management Workflow

**When mixing fresh chemistry**:

1. Go to CHEMICAL tab
2. Use Mix Calculator to determine volumes
3. Mix and transfer to storage bottles
4. Add to Shelf-Life Tracker:
   - Name: "Dektol - Fresh 1/11/2026"
   - Date: Today
   - Shelf Life: 180 days (6 months)
5. Add to Capacity Tracker if using immediately

**During printing session**:

1. Check Capacity Tracker before starting
2. If <20% remaining, consider mixing fresh
3. Track prints as you go
4. Check Shelf-Life Tracker for all chemistry

**End of session**:

1. Update Capacity Tracker with final print count
2. Check Shelf-Life for all chemicals
3. Note any that need replacement soon
4. Plan next mixing session

---

## CHART Tab - F-Stop Reference

### The Problem It Solves

Sometimes you need quick reference for f-stop calculations without going through the full calculator. This tab provides a complete table.

### Features

**Base Time Slider**: Reference time for table

- Set to your typical base time
- Table updates instantly
- Range: 0.4-50 seconds

**Stop Denominator**: Increment size

- Matches your working preference
- Affects table granularity
- 1/3 stop is standard

**Time Table**: Two-column reference

- **Stop**: Fractional stop value
- **Time**: Calculated exposure

### Use Cases

1. **Test Strip Planning**: See the full range before starting
2. **Manual Calculation**: Quick lookup without calculator
3. **Verification**: Double-check calculator results
4. **Teaching**: Show students f-stop relationships
5. **Documentation**: Reference for notes

### Example Table Interpretation

Base: 10s, Denominator: 3

| Stop  | Time  | Interpretation               |
| ----- | ----- | ---------------------------- |
| -2.00 | 2.5s  | 4 stops less (1/4 the light) |
| -1.67 | 3.3s  | 3.3 stops less               |
| -1.33 | 4.4s  | 2.7 stops less               |
| -1.00 | 5.0s  | 2 stops less (1/4 the light) |
| -0.67 | 6.7s  | 1.3 stops less               |
| -0.33 | 8.4s  | 0.7 stops less               |
| 0.00  | 10.0s | Base exposure                |
| +0.33 | 11.9s | 0.3 stops more               |
| +0.67 | 14.1s | 0.7 stops more               |
| +1.00 | 16.8s | 1 stop more (2× the light)   |
| +1.33 | 20.0s | 1.3 stops more               |
| +1.67 | 23.8s | 1.7 stops more               |
| +2.00 | 28.3s | 2 stops more (4× the light)  |

**Reading the table**: If your test strip shows you need 1 stop more exposure than your 10s base, you know immediately: 16.8s.

---

## Cross-Tab Integration: The Complete System

### The Philosophy: One Workflow, Not Seven Apps

Each tab is designed to work with the others, creating a seamless workflow.

### Integration Points

**TEST → CALC**:

- Click any test strip step
- Time automatically applied to CALC base
- No manual entry, no errors

**CALC → CONTROL**:

- Start exposure in CALC
- System triggers hardware (if Auto-Trigger enabled)
- Safelight managed automatically

**TIMER → CHEMICAL**:

- Track prints processed in Capacity Tracker
- Know when chemistry needs replacement
- Plan mixing sessions

**SETTINGS → EVERYTHING**:

- Configure once
- Used by all tabs
- Consistent behavior

### Audio Feedback System

**Centralized Service**: One audio system for all tabs

**Patterns**:

- **Countdown**: 5-4-3-2-1 (or pattern from SETTINGS)
- **Warning**: Single beep, last 3 seconds
- **Completion**: Two quick beeps
- **Test Step**: Single beep at start

**Why this matters**: Consistent audio language. You learn what each sound means, work without looking.

### State Persistence

**What gets saved**:

- All settings
- All profiles (timers, test strips)
- All chemical data (presets, capacity, shelf-life)
- Custom filter banks
- Color scheme preference

**Where**: Browser LocalStorage
**When**: Automatically on every change
**How long**: Until you clear browser data or import new data

**Backup**: Use Export All Data regularly

### Theme-Aware UI

**Visual feedback adapts**:

- Test strip preview colors
- Countdown display colors
- Timer state colors
- Alert colors

**Why**: Consistent visual language across all themes. You can switch themes without learning new visual cues.

---

## Complete Workflow Examples

### Example 1: New Print from Negative

**Goal**: Print a new negative for the first time

**Phase 1: Test Strip (TEST tab)**

1. Estimate base time: 10 seconds
2. Configure: 1/3 stop, 6 steps, Cumulative, Auto-advance ON
3. Start test
4. Evaluate: Step 4 looks best (16.9s)
5. Click Step 4 → switches to CALC tab

**Phase 2: Fine-Tune (CALC tab)**

1. Base time now 16.9s
2. Try +0.33 stop: 20.1s
3. Try -0.33 stop: 14.2s
4. Test 20.1s - looks perfect
5. Save as profile: "Portrait - 8x10 - MGIV"

**Phase 3: Production (CALC + TIMER + CONTROL)**

1. Set CALC to 20.1s
2. Verify Auto-Trigger and Safelight Auto-Off enabled
3. Prepare chemistry in trays
4. Start exposure in CALC
5. System: Countdown → Exposure → Completes
6. Move paper to chemistry
7. Start Dev timer (Auto-Start chains through all)
8. Handle paper, system handles timing
9. Print complete

**Phase 4: Management (CHEMICAL tab)**

1. Update Capacity: +1 print processed
2. Check: Developer at 60% capacity
3. Check: Fixer expires in 45 days
4. All good for next session

### Example 2: Multiple Prints, Same Exposure

**Goal**: Print 10 copies of same image

**Setup**:

1. Load saved profile
2. Verify chemistry capacity
3. Prepare all trays

**Production Loop** (repeat 10 times):

1. Place paper in easel
2. Click Start in CALC
3. System: Countdown → Exposure → Beep
4. Move paper to developer
5. Start Dev timer
6. System chains through all timers
7. Move paper as timers beep
8. Repeat

**Time saved**: 4 button presses × 10 prints = 40 actions eliminated

### Example 3: Changing Paper Size

**Goal**: Print same negative, different paper size

**Before**: 8×10, 20.1s exposure

**Change to**: 11×14

**Using Height Calculator (CALC tab)**:

1. Original: 20.1s, 8" height, f/8, 8×10 (80 sq in)
2. New: 10" height, f/8, 11×14 (154 sq in)
3. Height factor: (10÷8)² = 1.56
4. Area factor: (√154÷√80)² = 1.93
5. Result: 20.1 × 1.56 × 1.93 = 60.6 seconds

**Test**: Run test strip around 60s to verify
**Adjust**: Fine-tune as needed
**Save**: New profile for 11×14

### Example 4: Complex Dodging/Burning

**Goal**: Print with 3 dodging areas and 2 burning areas

**Using Incremental Mode (CALC tab)**:

1. Base: 10s, increment: 1/3 stop
2. Step 1 (base): 10s - full exposure
3. Step 2 (dodge area 1): 11.9s - mask area 1
4. Step 3 (dodge area 2): 14.2s - mask area 2
5. Step 4 (dodge area 3): 16.9s - mask area 3
6. Step 5 (burn area 1): 20.1s - expose area 1
7. Step 6 (burn area 2): 23.9s - expose area 2

**Execution**:

1. Start Step 1 → expose 10s
2. Click Next Step
3. Start Step 2 → expose 11.9s with dodge tool 1
4. Click Next Step
5. Continue through all steps
6. System tracks cumulative time automatically

**Result**: Complex exposure with precise timing for each step

---

## Troubleshooting & Best Practices

### Connection Issues

**Problem**: "Connection failed"

**Checklist**:

1. ✓ Pi is powered on and running Flask server
2. ✓ Correct IP address in SETTINGS
3. ✓ Correct port (default 5000)
4. ✓ Network connectivity (can you ping the Pi?)
5. ✓ Firewall not blocking port 5000
6. ✓ Test Connection button works

**Solution**: Work through checklist systematically

### Audio Not Working

**Problem**: No beeps

**Checklist**:

1. ✓ Click any button first (browser requires interaction)
2. ✓ Browser volume not muted
3. ✓ System volume not muted
4. ✓ Audio context initialized (click any button)
5. ✓ Try different browser

**Solution**: Most common issue is browser requiring user interaction before audio

### Timer Not Starting

**Problem**: Click Start, nothing happens

**Checklist**:

1. ✓ Auto-Trigger enabled in CONTROL tab
2. ✓ Server connection working
3. ✓ Relay 1 (enlarger) responding to manual test
4. ✓ No JavaScript errors in console

**Solution**: Verify hardware control works manually first

### Data Loss

**Problem**: Settings/profiles disappeared

**Checklist**:

1. ✓ Browser LocalStorage enabled
2. ✓ Not in private/incognito mode
3. ✓ Didn't clear browser data
4. ✓ Export data regularly as backup

**Solution**: Import from backup, enable auto-export

### Relay Not Responding

**Problem**: Hardware doesn't turn on/off

**Checklist**:

1. ✓ Relay wired correctly (active-LOW)
2. ✓ GPIO pin matches configuration
3. ✓ Power supply adequate
4. ✓ Relay coil voltage matches Pi output
5. ✓ Test with manual control

**Solution**: Verify wiring and power, test each relay individually

### Best Practices Summary

**Safety**:

1. Always use countdown
2. Enable Safelight Auto-Off
3. Test connections before critical work
4. Export data regularly

**Accuracy**:

1. Use f-stops, not linear time
2. Calibrate timers periodically
3. Test strips before final prints
4. Document successful configurations

**Workflow**:

1. Build profile library
2. Track chemistry usage
3. Monitor expiration dates
4. Plan maintenance

**Maintenance**:

1. Export data monthly
2. Check chemical dates weekly
3. Verify hardware connections periodically
4. Update software when available

---

## Advanced Features & Tips

### Custom Filter Banks

**Setup**:

1. Create three groups (A, B, C)
2. Fill with your common grades
3. Label clearly
4. Use in Height Calculator

**Example**:

- Group A (MG Paper): Grade 0=0.7, Grade 1=0.85, Grade 2=1.0, etc.
- Group B (Graded): Grade 1=0.5, Grade 2=1.0, Grade 3=1.5, etc.
- Group C (Experimental): Your custom values

### Multiple Profiles

**Organization**:

- Name descriptively: "Paper-Size-Setup"
- Example: "MGIV-8x10-Dektol-1+2"
- Build library over time
- Share with other printers

### Keyboard Shortcuts (if available)

**Efficiency**:

- Space bar: Start/Stop
- R: Reset
- N: Next step
- Arrow keys: Adjust sliders

### Mobile/Tablet Use

**Optimization**:

- Larger touch targets
- Swipe gestures
- Portrait/landscape support
- Works on any device with browser

### Data Export Strategy

**Recommended schedule**:

- After major configuration changes
- Monthly as routine backup
- Before software updates
- Share with team members

**Storage**:

- Cloud storage (Google Drive, Dropbox)
- Email to yourself
- USB drive
- Multiple locations

---

## Conclusion: Mastering the System

### The Learning Curve

**Day 1**: Learn basic exposure calculation and timer operation
**Week 1**: Build profile library, learn test strip workflow
**Month 1**: Master incremental mode, chemical tracking
**Ongoing**: Refine workflows, expand profile library

### Key Principles

1. **Precision**: Use f-stops, millisecond timing
2. **Integration**: Let tabs work together
3. **Automation**: Eliminate repetitive tasks
4. **Documentation**: Save successful configurations
5. **Safety**: Never compromise on safelight control

### Support & Resources

**When you need help**:

1. Check this manual first
2. Review troubleshooting section
3. Verify settings against examples
4. Test individual components

### Final Thoughts

Darkroom Timer & Tools is designed to become invisible. You shouldn't think about the software—you should think about your image. The system handles the technical details so you can focus on the creative work.

Start simple. Master the basics. Build complexity as needed. Your darkroom workflow will become faster, more consistent, and more professional.

**Welcome to precision darkroom printing.**

---

**Manual End** - Version 3.0.3 - For the latest updates, check the application footer
