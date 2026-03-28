# Darkroom Timer — User Manual

**Software Version:** 1.0.0  
**Last Updated:** March 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Navigation & Interface](#navigation--interface)
4. [METERING Tab — Light Meter & Analysis](#metering-tab--light-meter--analysis)
5. [TEST STRIP Tab — F-Stop Test Strip Generator](#test-strip-tab--f-stop-test-strip-generator)
6. [SPLIT GRADE Tab — Split-Grade Exposure Calculator](#split-grade-tab--split-grade-exposure-calculator)
7. [EXPOSURE & CALCULATOR Tab — Exposure Timer & Adjustments](#exposure--calculator-tab--exposure-timer--adjustments)
8. [TIMER Tab — Chemistry Processing](#timer-tab--chemistry-processing)
9. [CHEMICAL Tab — Chemical Management](#chemical-tab--chemical-management)
10. [CONTROLLER Tab — Device Control & Configuration](#controller-tab--device-control--configuration)
11. [LOGS Tab — Exposure Session Logging](#logs-tab--exposure-session-logging)
12. [SETTINGS Tab — System Configuration](#settings-tab--system-configuration)
13. [Cross-Tab Integration & Workflows](#cross-tab-integration--workflows)
14. [WiFi & Network Configuration](#wifi--network-configuration)
15. [Over-the-Air Updates](#over-the-air-updates)
16. [Data Management — Export, Import & Backup](#data-management--export-import--backup)
17. [Audio Feedback Reference](#audio-feedback-reference)
18. [Troubleshooting](#troubleshooting)
19. [Appendix A — F-Stop Reference Tables](#appendix-a--f-stop-reference-tables)
20. [Appendix B — Paper & Filter Database](#appendix-b--paper--filter-database)

---

## Introduction

### About Darkroom Timer

Darkroom Timer is a professional-grade darkroom exposure and workflow management system. It combines precision timing, f-stop exposure calculation, light metering, split-grade printing, chemical tracking, and relay control into a single integrated platform.

The system creates its own WiFi network and hosts a web interface. You connect to it from any device with a web browser — phone, tablet, or laptop — and control your entire darkroom from a single screen.

### Design Principles

**Precision** — All timing uses drift-corrected millisecond-accurate timers. F-stop calculations maintain full photographic precision throughout every operation.

**Safety** — Relays default to OFF on startup. Automatic safelight control eliminates fogging risk during exposures.

**Integration** — Test strip results flow directly into exposure calculations. Split-grade measurements feed into timers. Chemistry tracking connects to your printing sessions. Every feature is designed to work together.

**Workflow** — The interface follows the natural order of darkroom work: metering → testing → calculating → exposing → processing → logging.

### Quick Start

1. Power on the Darkroom Timer
2. Connect your device to the **DarkroomTimer** WiFi network (password: **darkroom123**)
3. Open a browser and navigate to **http://192.168.4.1** (or **http://darkroom.local** if mDNS is supported)
4. The EXPOSURE & CALCULATOR tab opens by default — you're ready to work

---

## Getting Started

### First-Time Setup

**Step 1 — Power On**

Connect the Darkroom Timer to a USB power source. The system boots in approximately 3–5 seconds.

**Step 2 — Connect to WiFi**

The Darkroom Timer creates a WiFi access point automatically:

| Parameter | Value |
|-----------|-------|
| SSID | DarkroomTimer |
| Password | darkroom123 |
| IP Address | 192.168.4.1 |
| mDNS Hostname | darkroom.local |

Connect your phone, tablet, or laptop to this network.

**Step 3 — Open the Interface**

Navigate to `http://192.168.4.1` in any modern web browser. The single-page application loads completely and is fully functional.

**Step 4 — Configure Your Preferences**

Go to the SETTINGS tab and configure:

- Color scheme (Darkroom / Day / Night)
- Default stop increment (1/3 stop recommended)
- Countdown delay (5 seconds recommended)
- Default chemistry times
- Audio preferences

**Step 5 — Verify Your Setup**

Go to the CONTROLLER tab and:

1. Tap **Test Connection** to verify communication
2. Test each relay individually using the ON/OFF toggles
3. If using a light meter, go to METERING and take a test reading

---

## Navigation & Interface

### Tab Bar

The application is organized into 9 tabs, accessible from a dropdown menu at the top of the screen:

| Tab | Purpose |
|-----|---------|
| **METERING** | Light meter readings, contrast analysis, split-grade analysis, virtual proof |
| **TEST STRIP** | Automated f-stop test strip generation and execution |
| **SPLIT GRADE** | Split-grade exposure calculation with paper-specific filter factors |
| **EXPOSURE & CALCULATOR** | Main exposure timer, f-stop calculations, enlarger adjustments |
| **TIMER** | Chemistry processing timers with auto-chain capability |
| **CHEMICAL** | Chemical mixing, developer capacity tracking, shelf-life monitoring |
| **CONTROLLER** | Relay control, temperature monitoring, WiFi configuration, updates |
| **LOGS** | Exposure session logging, export, and review |
| **SETTINGS** | System preferences, audio, display, data management |

The **EXPOSURE & CALCULATOR** tab is the default active tab on launch.

### Color Schemes

Three color schemes are available, selectable from SETTINGS:

| Scheme | Description | Best For |
|--------|-------------|----------|
| **Darkroom** | Dark background with red accents | Working under safelight conditions; preserves night vision |
| **Day** | Light background with warm grey-yellow tones | Daytime setup, planning, or brightly-lit environments |
| **Night** | Dark background with blue accents | Low-light use when red accents are not preferred |

The color scheme affects all UI elements including timer states, test strip previews, countdown animations, and status indicators.

### Fullscreen Mode

Available from SETTINGS, the **Toggle Fullscreen** button switches the browser to full-screen mode, hiding the address bar and browser chrome. This maximizes the usable display area on phones and tablets.

### Collapsible Sections

Many tabs contain collapsible sections (marked with ▼ / ▲ icons). Tap the section header to expand or collapse. Collapse positions are remembered across page reloads.

---

## METERING Tab — Light Meter & Analysis

> **Requires:** Light meter sensor (optional accessory)

The METERING tab provides four related tools for measuring and analyzing the light projected through your negative onto the easel: a Direct Metering panel, a Contrast Analyzer, a Split-Grade Analyzer, and a Virtual Proof system.

### Direct Metering

**Sensor Configuration:**

| Control | Options | Description |
|---------|---------|-------------|
| **Gain** | Low, Medium, High, Max, Auto | Sensitivity level. **Auto** adjusts dynamically. Use Low/Medium under bright enlarger light; High/Max for dense negatives or small apertures |
| **Integration Time** | 100–600 ms | How long the sensor collects light per reading. Longer = more accurate but slower. 200–400 ms is a good starting point |
| **Samples** | 1–20 | Number of readings averaged per measurement. More samples = more consistent results at the cost of measurement time |
| **Filter Factor** | Numeric | Multiplier applied to the exposure reading to compensate for the currently selected contrast filter |

**Taking a Reading:**

1. With the enlarger on, position the sensor under the projected image on the easel
2. Press **Read** to take a single measurement, or enable **Live Mode** for continuous updating
3. The display shows the raw lux value and a calculated exposure time

**Calculated Exposure:**

```
Exposure Time = Calibration Constant ÷ Lux × Filter Factor
```

The calibration constant is set per paper during calibration (see below).

### Paper-Specific Calibration

Because different papers have different sensitivities, the light meter supports per-paper calibration:

1. Select your **Paper Brand** (Ilford or FOMA) and **Paper Type**
2. Make a properly exposed test print using the EXPOSURE or TEST STRIP tab
3. Note the exposure time that produced the correct result
4. Press **Calibrate** and enter this known-good exposure time
5. The system calculates and stores a calibration constant for this specific paper

Once calibrated, all subsequent metering with this paper type will produce accurate exposure recommendations. You can calibrate independently for each of the 11 supported paper types.

### Contrast Analyzer

Measures the contrast range of your projected image and recommends an appropriate contrast grade.

**How to Use:**

1. Place the sensor under the **brightest highlight area** of the projected image
2. Press **Highlight** — the lux value is stored
3. Move the sensor to the **deepest shadow area** that should hold detail
4. Press **Shadow** — the lux value is stored
5. The analyzer calculates:
   - **ΔEV** (delta exposure value): the difference in stops between highlight and shadow
   - **Recommended Grade**: the contrast filter grade that best maps the scene's range to the paper

**Interpreting ΔEV:**

| ΔEV Range | Scene Contrast | Recommended Action |
|-----------|----------------|-------------------|
| < 1.5 | Very flat (low contrast) | Use a hard filter (Grade 4–5) to add contrast |
| 1.5–2.5 | Low contrast | Grade 3–4 |
| 2.5–3.5 | Normal contrast | Grade 2–3 (neutral filtration) |
| 3.5–4.5 | High contrast | Grade 1–2 (soft filtration) |
| > 4.5 | Very contrasty | Use a soft filter (Grade 00–1) or consider split-grade printing |

### Split-Grade Analyzer (Heiland Method)

An advanced analysis mode that goes beyond single-grade recommendations. Based on the Heiland densitometry approach, it calculates optimal **two-exposure** (soft + hard) printing parameters.

**How It Works:**

After taking highlight and shadow readings:

1. The system computes ΔEV from the lux ratio
2. Using the selected paper's filter data, it selects the optimal soft and hard filter pair
3. It calculates the exposure time for each filter to produce correct highlight density (via the soft exposure) and correct shadow density (via the hard exposure)
4. Results include specific filter names, times, and the contrast ratio

**Results Display:**

| Field | Description |
|-------|-------------|
| **Soft Filter** | The recommended yellow/soft filter (e.g., "Grade 00" for Ilford, "2×Yellow" for FOMA) |
| **Soft Time** | Exposure duration with the soft filter |
| **Hard Filter** | The recommended magenta/hard filter (e.g., "Grade 5" for Ilford, "2×Magenta 2" for FOMA) |
| **Hard Time** | Exposure duration with the hard filter |
| **ΔEV** | Measured contrast range in stops |

Press **Send to SPLIT GRADE** to transfer these values to the SPLIT GRADE tab for further refinement, or **Send to EXPOSURE** to load the base exposure time directly.

### Virtual Proof

The Virtual Proof system lets you predict how different areas of your print will render **before making an exposure**, acting like a zone-system spot meter for enlarging.

**How It Works:**

1. A reference cell is established from your first stable reading (this represents your exposure baseline)
2. Move the sensor to different areas of the projected image
3. Each measurement is compared to the reference and expressed as a **relative density value** (0 = paper white, 10 = maximum black)
4. This shows you which print zones each area will fall into under the current exposure settings

**Controls:**

| Control | Description |
|---------|-------------|
| **Read Cell** | Takes a single cell measurement |
| **Live Mode** | Continuously measures and updates the zone prediction |
| **Reset Reference** | Clears the reference cell so a new baseline can be established |
| **Stability Indicator** | Shows when readings have stabilized (configurable sensitivity in SETTINGS) |

**Stability Detection:**

The Virtual Proof uses configurable stability detection to ensure accurate readings. When enabled, the system waits for multiple consecutive readings within a tolerance window before accepting a measurement. An audible beep confirms when a stable reading is captured. Configure tolerance, required stable reads, and maximum wait time in SETTINGS → Metering Settings.

**Practical Use:**

- Map the tonal range of your projected image before committing paper
- Identify areas that will block up (too dark) or blow out (too light)
- Decide whether to burn, dodge, or change grade before the first exposure
- Verify that split-grade filter choices will produce the expected tonal separation

---

## TEST STRIP Tab — F-Stop Test Strip Generator

The TEST STRIP tab automates the creation of f-stop-based test strips, replacing the traditional method of adding equal time increments.

### Why F-Stop Test Strips?

Traditional test strips add the same number of seconds to each step (e.g., 5, 10, 15, 20, 25 seconds). This produces **unequal perceptible differences** between steps — the jump from 5s to 10s is massive (a full stop) while 20s to 25s is barely noticeable (less than 1/3 stop).

F-stop test strips use **geometric** (multiplicative) increments. Each step differs from the next by the same fraction of a stop, producing **visually uniform** steps that are far easier to evaluate.

### Configuration

| Control | Options | Description |
|---------|---------|-------------|
| **Base Time Slider** | Configurable range (default 0.4–50s) | The starting exposure time for the first step |
| **Stop Increment** | 1/2, 1/3, 1/4, 1/6 | Size of each step. 1/3 stop is recommended for most work |
| **Number of Steps** | 3–16 | Total steps in the test strip |
| **Method** | Cumulative / Sequential | How the test strip is exposed |
| **Transfer Destination** | EXPOSURE / SPLIT GRADE | Where the selected step's time is sent when tapped |

### Methods Explained

**Cumulative (Recommended):**

Each step adds exposure to the entire sheet. The paper is uncovered one section at a time during the sequence.

- Step 1: Expose entire sheet for *t₁* seconds
- Step 2: Cover the first section; expose remaining sheet for *t₂ − t₁* additional seconds
- Step 3: Cover the next section; expose remaining for *t₃ − t₂* additional seconds
- Continue until all steps are complete

This is the traditional enlarging test-strip technique adapted to f-stop spacing.

**Sequential:**

Each step is an independent, separate exposure of the stated duration. This is useful when testing individual exposure times on separate pieces of paper.

### Step Preview

Before running the strip, a visual preview shows:

| Column | Description |
|--------|-------------|
| **Step** | Step number (1, 2, 3, …) |
| **Exposure** | Total exposure time for this step |
| **Increment** | Time added in this step (cumulative mode) or full time (sequential) |
| **±Stops** | The f-stop offset from the base time |
| **Visual Bar** | Proportional dark-to-light bar representing expected density |

**Transfer Destination:** Tap any step in the preview to send its exposure time to the selected destination tab (EXPOSURE or SPLIT GRADE).

### Running the Test Strip

Controls during the automated exposure sequence:

| Button | Action |
|--------|--------|
| **Start** | Begins the automated test strip sequence. A pre-exposure countdown runs first (configurable in SETTINGS). |
| **Pause / Resume** | Suspends or continues the current step |
| **Next Step** | Manually advances to the next step (skipping the remainder of the current step) |
| **Cancel** | Aborts the entire test strip |

**Auto-Advance** (configurable in SETTINGS): When enabled, each step automatically advances after a configurable delay (default: 1 second pause between steps). This provides hands-free operation — you only need to cover the next section of paper during each pause.

### Profiles

Test strip configurations can be saved and loaded:

| Action | Description |
|--------|-------------|
| **Save Profile** | Saves base time, increment, step count, and method with a custom name |
| **Load Profile** | Restores a saved test strip configuration |
| **Delete Profile** | Removes the currently loaded profile |
| **Clear All** | Removes all saved test strip profiles |

### Test Strip Tips

- **Start with 1/3-stop increments, 7 steps**: This covers about 2 stops of range, usually enough to bracket the correct exposure.
- **Center the strip on your estimate**: If you think 10 seconds is about right, set the base time to about 6 seconds for a 7-step strip. The correct exposure will likely fall in the middle.
- **Evaluate under a white light**: Switch to the White Light relay in CONTROLLER to inspect your test strip under consistent illumination.
- **Select your best step**: Tap it in the preview to transfer its time directly to the EXPOSURE or SPLIT GRADE tab.

---

## SPLIT GRADE Tab — Split-Grade Exposure Calculator

Split-grade printing uses two separate exposures — one with a soft (low-contrast) filter and one with a hard (high-contrast) filter — to independently control highlight and shadow density. This provides more control than a single-grade approach and is especially effective with contrasty negatives.

### Controls

| Control | Options | Description |
|---------|---------|-------------|
| **Paper Brand** | Ilford / FOMA | Selects the filter naming system and ISO R data. Synchronized globally — changing brand here updates all other tabs |
| **Paper Type** | 11 paper variants | Selects the specific paper for filter factor lookup |
| **Soft Filter** | Brand-specific grades | The low-contrast filter for highlight control |
| **Hard Filter** | Brand-specific grades | The high-contrast filter for shadow control |
| **Neutral Time Slider** | Configurable range | The base exposure time assuming a Grade 2 (neutral) filter |
| **Burn %** | 0–100% | Shifts the time balance between soft and hard exposures. 0% = all soft/hard equally weighted; increasing the percentage shifts emphasis toward one filtration |

### How Split-Grade Times Are Calculated

```
Soft Time  = Neutral Time × Soft Filter ISO R Factor × (1 + Burn% adjustment)
Hard Time  = Neutral Time × Hard Filter ISO R Factor × (1 − Burn% adjustment)
```

The ISO R factors come from the paper database and are manufacturer-measured values specific to each paper and filter combination. These factors compensate for the different light absorption of each filter, ensuring that the soft and hard exposures contribute the correct amount of density.

### Display

The calculator shows:

- Selected soft filter name and its calculated exposure time
- Selected hard filter name and its calculated exposure time
- Filter Factor values used (from the paper database)

### Transfer Options

| Button | Action |
|--------|--------|
| **Send to EXPOSURE** | Transfers both soft and hard filter names and times to the EXPOSURE tab's split-grade panel |

### Split-Grade Tips

- **Start at Burn 0%** and adjust from there. The Burn slider shifts the balance between soft and hard exposures after the base split has been calculated.
- **Use the METERING tab's Split-Grade Analyzer** if you have a light meter — it will calculate the optimal soft/hard filter selection and times automatically based on actual scene measurements.
- **Low-contrast negatives** benefit from a harder-biased split (less soft, more hard).
- **High-contrast negatives** benefit from a softer-biased split (more soft, less hard, or the Heiland algorithm's two-exposure approach).

---

## EXPOSURE & CALCULATOR Tab — Exposure Timer & Adjustments

The EXPOSURE & CALCULATOR tab is the primary exposure control interface. It combines a precision timer, f-stop exposure compensation, and an enlarger/contrast calculator into one unified panel.

### Exposure Timer

**Base Time Slider:** Sets the exposure time. The slider range is configurable in SETTINGS (default: 0.4–50 seconds).

**Stop Adjustment Slider:** Adjusts the exposure in fractional f-stop increments. The denominator (1/2, 1/3, 1/4, or 1/6 stop) follows the global setting. Each click on the stop slider multiplies or divides the base time by the corresponding f-stop factor.

**Calculated Time Display:** Shows the final exposure time after applying the stop adjustment:

```
Final Time = Base Time × 2^(Stop Adjustment)
```

### Countdown & Exposure Sequence

When you press **Start**:

1. A pre-exposure **countdown** begins (default: 5 seconds, configurable in SETTINGS). This gives you time to position the paper, remove the safe filter, or prepare.
2. During the last 3 seconds, urgent beeps and a visual flash alert you.
3. At zero, the exposure begins. If **Auto-Trigger Enlarger** is enabled, the enlarger relay activates automatically.
4. If **Auto Safelight Control** is enabled, the safelight turns off during the exposure and restores afterward.
5. The timer counts down, showing remaining time.
6. A **3-second warning beep** (configurable) sounds before completion.
7. At zero, an **end beep** (configurable) confirms the exposure is finished, and the enlarger relay deactivates.

**Controls During Exposure:**

| Button | Action |
|--------|--------|
| **Pause / Resume** | Pauses the exposure timer (the enlarger relay also pauses — useful for dodging) |
| **Cancel** | Aborts the exposure immediately and deactivates the enlarger relay |
| **+1 / −1 Second** | Adds or subtracts one second from the remaining time in real-time |

### Split-Grade Exposure Panel

When a split-grade recipe is sent from the SPLIT GRADE or METERING tab, a panel appears showing:

- **Soft Filter** name and exposure time
- **Hard Filter** name and exposure time

You execute each exposure separately with the appropriate filter inserted, or use the panel as a reference while working.

### Enlarger & Contrast Calculator

A comprehensive tool for recalculating exposure times when changing enlarger height, lens aperture, paper size, or contrast filter grade.

**Enlarger Height:**

| Preset | Area |
|--------|------|
| 4 × 5" | 20 sq in |
| 5 × 7" | 35 sq in |
| 8 × 10" | 80 sq in |
| 9.5 × 12" | 114 sq in |
| 11 × 14" | 154 sq in |
| 16 × 20" | 320 sq in |
| **Custom** | Enter width × height |

**Contrast Filter:**

- Paper brand toggle (Ilford / FOMA) — synchronized globally
- Paper type selector — same 11 paper variants as METERING and SPLIT GRADE tabs
- Filter grade selector — brand-specific grades
- Displays the **ISO R** value and **Filter Factor** for the selected combination

**Calculation Formula:**

```
Adjusted Time = Original Time
                × (New Height ÷ Original Height)²
                × (New F-Stop ÷ Original F-Stop)²
                × (√New Paper Area ÷ √Original Paper Area)²
                × Filter Factor
```

**Combined Factors Display:** Shows each individual factor (height, aperture, paper size, contrast, custom) and the combined multiplier. The adjusted time is displayed prominently.

**Action Buttons:**

| Button | Action |
|--------|--------|
| **Use Current** | Copies the current exposure time as the original time for calculation |
| **Apply** | Applies the calculated adjusted time back to the base time slider (clamped to the configured range) |

**Example Calculation:**

- Original: 10s at 20 cm height, f/8, 8×10" paper, Grade 2
- New: 30 cm height, f/5.6, 11×14" paper, Grade 4
- Height factor: (30 ÷ 20)² = 2.25
- Aperture factor: (5.6 ÷ 8)² = 0.49
- Area factor: (√154 ÷ √80)² = 1.925
- Filter factor: from paper database (paper-specific)
- Result: 10 × 2.25 × 0.49 × 1.925 × filter = adjusted time

### Custom Filter Banks

The Custom Filter Bank Manager provides 3 groups (A, B, C) with 12 slots each for storing custom filter factors.

**Use Cases:**

- **Group A:** Your standard variable-contrast paper grades
- **Group B:** Graded papers or alternative brands
- **Group C:** Experimental or specialty filters

Each slot has a label and a numeric filter factor. These factors feed into the Enlarger & Contrast Calculator's combined factor calculation, allowing you to layer a custom multiplier on top of the paper-specific ISO R factor.

---

## TIMER Tab — Chemistry Processing

The TIMER tab manages four independent chemistry timers that can run sequentially in an automated chain.

### Timer Grid

Four timers are displayed in a grid:

| Timer | Default Duration | Purpose |
|-------|-----------------|---------|
| **Developer** | 60 seconds | Controls development time — the most critical chemistry step |
| **Stop Bath** | 30 seconds | Neutralizes developer; prevents carryover |
| **Fixer** | 60 seconds | Removes unexposed silver; essential for print permanence |
| **Photo Wash** | 30 seconds | Final rinse; removes fixer residue |

Default durations are configurable in SETTINGS.

### Individual Timer Controls

Each timer has:

- **Time Display:** Shows remaining time in seconds during countdown
- **±1 Second Buttons:** Tap to adjust by 1 second. **Press and hold** for continuous rapid adjustment (repeats every 200 ms) — ideal for quickly changing timer values by large amounts
- **Start:** Begins the countdown
- **Pause:** Suspends the countdown; press again to resume
- **Reset:** Returns to the default duration
- **Enable/Disable Toggle:** When disabled, the timer is excluded from the auto-chain sequence and appears greyed out

### Auto-Start Chain

When the auto-start chain is invoked, starting the Developer timer triggers an automated sequence:

1. **Countdown** (if configured) → **Developer** starts
2. Developer completes → **Stop Bath** automatically starts
3. Stop Bath completes → **Fixer** automatically starts
4. Fixer completes → **Photo Wash** automatically starts (unless disabled)
5. Photo Wash completes → **Chain complete**

**Chain Controls:**

| Button | Action |
|--------|--------|
| **Start All** | Initiates the countdown and begins the Developer timer. The chain auto-advances through all enabled timers. |
| **Pause / Resume** | Pauses or resumes the currently running timer in the chain |
| **Cancel** | Stops the chain entirely and resets all timers |
| **Reset All** | Resets all four timers to their default durations |

Disabled timers are skipped in the chain. For example, if you disable Photo Wash, the chain ends after Fixer completes.

### Audio Feedback

- **10-Second Warning Beep** (configurable): Sounds 10 seconds before each timer completes
- **End Beep** (configurable): Distinct completion tone when a timer finishes
- **Chain transition**: Audio cue when auto-advancing to the next timer

### Factorial Development

The TIMER tab includes a **Factorial Development** system for advanced development control. This technique allows you to calibrate your development by visual inspection and apply that calibration consistently across prints.

**The Concept:**

Different negatives, temperatures, and developer conditions produce different development speeds. Rather than guessing whether your standard time is correct for today's conditions, factorial development uses a visual marker — the moment the first maximum black appears in the print — to calculate the correct total development time.

**Phase 1 — Calibration:**

1. Set your Developer timer to the target development time
2. Start the Developer timer
3. Watch the developing print carefully under safelight
4. When you first see pure black areas emerge, press **Mark Baseline**
5. The system records the elapsed time and calculates: `Multiplier = Target Time ÷ Elapsed Time at Black Point`

**Phase 2 — Production:**

1. Start the Developer timer for a new print
2. Watch the development
3. When black areas first appear, press **Black Point**
4. The system calculates: `New Target Time = Elapsed Time × Multiplier`
5. This new target is applied to the Developer timer after the current cycle completes

**Reset Multiplier:** Clears the calibration. Start fresh when changing developers, dilutions, or working conditions.

**Why this works:** The time from immersion to first visible black is proportional to total development time. If the multiplier is 4× and blacks appear at 15 seconds, total development should be 60 seconds. If blacks appear at 20 seconds (perhaps due to cooler developer), total development should be 80 seconds. The system adapts automatically.

### Timer Profiles

| Action | Description |
|--------|-------------|
| **Save Profile** | Saves all four timer durations plus factorial multiplier with a custom name |
| **Load Profile** | Restores a saved timer configuration |
| **Delete Profile** | Removes the currently loaded profile |
| **Clear All** | Removes all saved timer profiles |

**Example profiles:**

| Profile Name | Dev | Stop | Fix | Wash |
|-------------|-----|------|-----|------|
| Dektol 1+2 8×10 | 60s | 30s | 60s | 30s |
| Dektol 1+2 11×14 | 75s | 30s | 90s | 60s |
| Pyro PMK 4×5 | 90s | 45s | 120s | 120s |

### Complete Chemistry Workflow

1. **Before printing:** Load the appropriate timer profile for your developer/paper combination
2. **After exposing a print:** Place it in the developer tray
3. **Tap Start All:** The countdown runs, then Developer begins
4. **When Developer beeps:** Transfer paper to the stop bath tray
5. **When Stop beeps:** Transfer to the fixer tray
6. **When Fixer beeps:** Transfer to the wash tray
7. **When Photo Wash beeps:** Remove and hang to dry

You only press one button. The system handles all four timing sequences automatically. Over 10 prints, this eliminates 30 manual button presses and ensures every print receives exactly the same processing.

---

## CHEMICAL Tab — Chemical Management

The CHEMICAL tab provides three tools for managing darkroom chemistry: a mix calculator, a developer capacity tracker, and a shelf-life monitor.

### Chemical Mix Calculator

Calculates stock and water volumes for any dilution ratio.

**Controls:**

- **Total Volume Slider:** 100–5000 ml — the total amount of working solution you need
- **Dilution Ratio Presets:** Quick-select buttons for common ratios (1+9, 1+14, 1+19, 1+24, 1+29, 1+34, 1+39)
- **Custom Ratio Input:** Enter any stock:water ratio for non-standard dilutions

**Calculation:**

```
Stock Volume = Total Volume × Stock Parts ÷ (Stock Parts + Water Parts)
Water Volume = Total Volume × Water Parts ÷ (Stock Parts + Water Parts)
```

**Examples:**

| Dilution | Total Volume | Stock | Water |
|----------|-------------|-------|-------|
| 1+9 | 1000 ml | 100 ml | 900 ml |
| 1+19 | 500 ml | 25 ml | 475 ml |
| 1+39 | 2000 ml | 50 ml | 1950 ml |

### Chemical Mix Presets

Save your frequently used chemistry mixes for one-tap recall:

| Action | Description |
|--------|-------------|
| **Save Preset** | Saves current volume and dilution ratio with a custom name (e.g., "Rodinal 1+50 for 35mm") |
| **Load Preset** | Restores a saved mix configuration |
| **Delete Preset** | Removes the currently loaded preset |
| **Clear All** | Removes all saved chemical presets |

### Developer Capacity Tracker

Tracks how many prints your developer can process before exhaustion.

**Configuration:**

| Control | Range | Description |
|---------|-------|-------------|
| **Capacity Slider** | 0.1–40 m²/liter | Developer capacity per the manufacturer's specification |
| **Tray Volume** | 100–5000 ml | Amount of working developer in your tray |
| **Paper Size** | 6 presets + custom | The paper size you're printing (area in m²) |

**Calculation:**

```
Max Prints = (Capacity × Tray Volume ÷ 1000) ÷ Paper Area
Remaining  = Max Prints − Prints Processed
Usage %    = Prints Processed ÷ Max Prints × 100
```

**Print Counter:**

- **+1 Button:** Add one print to the count
- **+5 Button:** Add five prints (for batch counting)
- **Reset Button:** Clear the print count (do this when mixing fresh developer)

**Progress Bar:** A visual indicator fills as the developer is consumed.

**Status Display:**

| Field | Description |
|-------|-------------|
| **Prints Done** | Number of prints processed in this batch |
| **Area Used** | Total paper area processed in m² |
| **Usage %** | Percentage of developer capacity consumed |
| **Status** | Color-coded condition indicator |

**Status Colors:**

| Remaining Capacity | Color | Action |
|-----------|-------|--------|
| > 20% | Green | Continue printing normally |
| 10–20% | Yellow/Orange | Plan to replace soon; consider reduced print quality |
| < 10% | Red | Replace immediately; risk of underdevelopment |

### Shelf-Life Tracker

Monitors the expiration of your darkroom chemicals so you never accidentally use expired solutions.

**Adding a Chemical:**

| Field | Description |
|-------|-------------|
| **Chemical Type** | Developer, Stop Bath, Fixer, Hypo Clear, Photo Wash, or Custom |
| **Custom Name** | Free-text name (available when "Custom" type is selected, e.g., "Selenium Toner") |
| **Shelf Life (days)** | Number of days the chemical remains usable after mixing |
| **Date Mixed** | The date the chemical was mixed or opened |

**Active Chemicals List:**

Each tracked chemical displays:

- Chemical name and type
- Date mixed
- Days remaining until expiration
- Color-coded status indicator

**Status Colors:**

| Days Remaining | Visual | Meaning |
|----------------|--------|---------|
| > 30 days | Green background | Fresh — no action needed |
| 15–30 days | Orange background, warning border | Use soon or plan replacement |
| 1–14 days | Red background, bold text | Replace now — nearing expiration |
| ≤ 0 days | Red pulsing animation | **EXPIRED — Do not use** |

**Management Buttons:**

| Button | Action |
|--------|--------|
| **Renew** | Resets the mixed date to today (use when replacing with fresh chemistry of the same type) |
| **Delete** | Removes a single chemical entry |
| **Clear Expired** | Removes all expired entries in one action |

### Typical Shelf Lives (Reference)

| Chemical | Shelf Life (Mixed/Opened) |
|----------|--------------------------|
| Paper developer (liquid) | 3–6 months |
| Paper developer (powder, mixed) | 6 months |
| Stop bath (indicator type) | 6–12 months |
| Fixer (standard) | 6–12 months |
| Fixer (rapid) | 2–3 months |
| Hypo clearing agent | 6 months |
| Selenium toner | 12+ months |

---

## CONTROLLER Tab — Device Control & Configuration

The CONTROLLER tab provides direct relay control, temperature management, WiFi configuration, server settings, and firmware updates.

### Relay Controls

Four relays are available, each with a dedicated ON/OFF toggle button:

| Relay | Default Label | Function |
|-------|---------------|----------|
| **Relay 1** | Enlarger | Controls the enlarger lamp power |
| **Relay 2** | Safelight | Controls the safelight |
| **Relay 3** | Heater | Controls a heating element (for temperature-controlled processing) |
| **Relay 4** | White Light | Controls a white inspection light |

**Relay names are customizable** — you can rename them to match your specific setup.

**Bulk Controls:**

- **All ON:** Activates all four relays simultaneously
- **All OFF:** Deactivates all four relays simultaneously — use as an emergency stop

**Safety Note:** Manually turning off a relay will stop any active timer or exposure associated with that relay. This provides an immediate override for any operation in progress.

### Temperature Control

> **Requires:** Temperature sensor (optional accessory)

The temperature control system monitors your processing environment and can automatically maintain a target temperature using the heater relay.

**Controls:**

| Element | Description |
|---------|-------------|
| **Enable/Disable Toggle** | Activates or deactivates temperature monitoring and heating control |
| **Current Temperature** | Live reading from the sensor, updated periodically |
| **Target Temperature Slider** | 15–50°C — sets the desired processing temperature |
| **Heating Status Indicator** | Shows whether the heater is currently active |

**Temperature Display Colors:**

| Condition | Color | Meaning |
|-----------|-------|---------|
| Heating active | Blue | Temperature is below target; heater is running |
| At target (±0.5°C) | Green | Temperature is within range |
| Close to target | Orange | Temperature is approaching the target |

**Hysteresis Control:** The system uses a ±0.5°C dead zone to prevent rapid on/off cycling of the heater. The heater turns on when the temperature drops 0.5°C below the target and turns off when it reaches 0.5°C above the target.

**History Chart:** A 15-minute temperature history graph shows temperature stability over time, updated every 15 seconds.

**Use Case:** Maintaining consistent developer temperature (typically 20°C / 68°F) is critical for repeatable results. The temperature control system can heat a water bath or developer tray to the target temperature and hold it there throughout your printing session.

### WiFi Configuration

**Connecting to an Existing Network:**

1. Enter the **SSID** (network name) and **Password** of your home or studio WiFi network
2. Press **Connect**
3. The system attempts to connect. On success, the access point may be disabled to avoid routing conflicts
4. Connection status is displayed

**WiFi Management Buttons:**

| Button | Action |
|--------|--------|
| **Connect WiFi** | Attempts to connect to the entered SSID/password. Credentials are saved to the device |
| **Force Hotspot Mode** | Disconnects from any WiFi network and reactivates the built-in access point |
| **Clear WiFi Credentials** | Removes saved WiFi credentials from the device |

**WiFi Status Display:** Shows current connection mode (AP or STA), IP address, signal strength, and network name.

### Server Settings

| Element | Description |
|---------|-------------|
| **Server IP** | Auto-detected from the page URL. Editable if needed |
| **Server Port** | Auto-detected from URL (typically port 80). Editable if needed |
| **Test Connection** | Sends a health check request to verify communication. Shows "OK" on success |
| **Test Timer Relay** | Enter a duration in seconds and trigger the enlarger relay for a test exposure |
| **Auto-Trigger Enlarger** | When enabled, starting any timer automatically activates the enlarger relay |
| **Auto Safelight Control** | When enabled, the safelight automatically turns off during exposures and restores afterward |

### Auto Safelight Control — Detailed Behavior

This is a critical safety feature that should always be enabled during printing. When active:

1. An exposure starts (from EXPOSURE, TEST STRIP, or TIMER tabs)
2. The system checks the current safelight relay state
3. If the safelight is ON, its state is remembered
4. The safelight relay is turned OFF
5. The enlarger relay activates and the exposure runs
6. After the exposure completes, a 0.5-second buffer is added
7. The safelight relay is restored to its previous state

This eliminates the risk of safelight fogging during exposure — a common cause of ruined prints that is easy to forget, especially during long printing sessions.

### Firmware Updates

| Element | Description |
|---------|-------------|
| **Check for Updates** | Checks online for new releases |
| **Progress Bar** | Shows download progress during update installation |
| **Auto-Reload** | The browser automatically reloads after a successful update to load the new interface |

Updates can include new features, bug fixes, and improvements to both the web interface and the server modules.

---

## LOGS Tab — Exposure Session Logging

The LOGS tab provides comprehensive session-based logging of all exposure work, with export capabilities for record-keeping and analysis.

### Session Concept

A **session** represents a continuous period of darkroom work. Sessions are automatically started when you begin an exposure and can span multiple phases of work. Each session can contain multiple **phases**:

| Phase Type | Source | Data Captured |
|------------|--------|---------------|
| **Test Phase** | TEST STRIP tab | Base time, increment, steps, method, individual step results |
| **Split Phase** | SPLIT GRADE tab or METERING tab | Soft/hard filter names, times, burn percentage, paper type |
| **Calc Phase** | EXPOSURE & CALCULATOR tab | Base time, stop adjustment, final time, step count, notes |
| **Timer Phase** | TIMER tab | Dev/Stop/Fix/Wash times, marks session end |

### Session Storage

| Type | Description | Limit |
|------|-------------|-------|
| **Temporary Sessions** | Auto-saved during work. Intended for short-term review and evaluation | Maximum 6 (oldest removed automatically when limit is exceeded) |
| **Permanent Sessions** | Manually promoted from temporary sessions. Stored indefinitely for long-term reference | No limit |

### Session Management

| Action | Description |
|--------|-------------|
| **View** | Opens a detailed view of all phases within a session, showing every parameter, timing value, and note |
| **Save → Permanent** | Promotes a temporary session to permanent storage so it won't be automatically removed |
| **Delete** | Removes a specific session (temporary or permanent) |
| **Clear All Logs** | Removes all temporary and permanent sessions |

### Session Statistics

A summary panel at the top of the LOGS tab shows aggregate statistics across all logged sessions, giving you a high-level overview of your printing activity.

### Export & Import

| Format | Description |
|--------|-------------|
| **Export CSV** | Generates a downloadable CSV file. Columns: Session, Date, Time, Phase, BaseTime, Stop, FinalTime, SoftFilter, HardFilter, FilterBrand, Notes. Ideal for spreadsheet analysis. |
| **Export JSON** | Generates a structured JSON file containing all session data in full detail. Best for backup and re-import. |
| **Import JSON** | Loads previously exported JSON session data back into the application |

### Use Cases for Logging

- **Print documentation:** Record every exposure parameter so you can reproduce a successful print months later
- **Process optimization:** Compare exposure data across sessions to identify patterns and improvements
- **Client records:** Commercial labs can maintain exposure records for client work
- **Learning:** New printers can review their progression and identify areas for improvement

---

## SETTINGS Tab — System Configuration

The SETTINGS tab centralizes all application preferences. Changes are persisted to localStorage when you press **Save All Settings**.

### Display Settings

| Setting | Options | Description |
|---------|---------|-------------|
| **Toggle Fullscreen** | Button | Enters or exits browser fullscreen mode. Maximizes screen real estate on mobile devices |
| **Color Scheme** | Darkroom / Day / Night | Sets the visual theme for the entire application |

### Global Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Default Base Time** | 10s | Slider range | Starting base time for exposure calculations |
| **Default Stop Increment** | 1/3 | 1/2, 1/3, 1/4, 1/6 | Global f-stop increment denominator used across all tabs |
| **Countdown Delay** | 5s | 0–30s | Pre-exposure countdown duration. Set to 0 to disable countdown |
| **Countdown Beep** | On | Toggle | Master switch for all countdown audio |
| **Countdown Pattern** | every-second | Segmented control | When beeps sound during the countdown period |
| **Test Countdown Pattern** | Button | — | Plays a preview of the selected countdown pattern so you can hear it before committing |

**Countdown Pattern Options:**

| Pattern | Behavior | Recommended For |
|---------|----------|-----------------|
| **every-second** | Beep on every second of the countdown | Users who want continuous audio feedback |
| **last3** | Silent until the last 3 seconds, then beep each second | Most users — minimal distraction with sufficient warning |
| **last5** | Silent until the last 5 seconds, then beep each second | Users who want earlier warning |
| **none** | Completely silent countdown | Experienced users who prefer visual-only feedback |

### Metering Settings

| Setting | Description |
|---------|-------------|
| **Virtual Proof Stability Enable** | Toggle stability detection on/off for Virtual Proof cell measurements |
| **Beep on Stable** | Play audible confirmation when a stable reading is captured |
| **Tolerance %** | Percentage variation threshold (smaller = stricter stability requirement) |
| **Min Stable Reads** | Number of consecutive stable readings required before accepting |
| **Max Wait (ms)** | Maximum time to wait for stability; accepts current value if exceeded |
| **Min Delta Lux** | Minimum absolute lux change to register as a genuinely new reading |

### Test Strip Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Auto Advance** | Off | Automatically advance test strip steps after the configured delay |
| **Auto Advance Delay** | 1s | Time between auto-advance steps (increase for more evaluation time) |
| **Test Base Time Min** | 0.4s | Lower limit for the test strip base time slider |
| **Test Base Time Max** | 50s | Upper limit for the test strip base time slider |

### Exposure Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Base Time Min** | 0.4s | Lower limit for the exposure base time slider |
| **Base Time Max** | 50s | Upper limit for the exposure base time slider |
| **3-Second Warning Beep** | On | Audio alert 3 seconds before an exposure completes |
| **End Beep** | On | Audio confirmation when an exposure completes |

**Tip:** Setting the base time min/max to your typical working range (e.g., 5–30 seconds) makes the slider more sensitive and easier to adjust precisely.

### Timer Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Default Dev Time** | 60s | Default developer timer duration |
| **Default Stop Time** | 30s | Default stop bath timer duration |
| **Default Fix Time** | 60s | Default fixer timer duration |
| **Default Flo Time** | 30s | Default photo wash timer duration |
| **10-Second Warning Beep** | On | Audio alert 10 seconds before a chemistry timer completes |
| **End Beep** | On | Audio confirmation when a chemistry timer completes |

### Controller Settings

These mirror the controls in the CONTROLLER tab for convenience:

| Setting | Default | Description |
|---------|---------|-------------|
| **Auto-Trigger Enlarger** | On | Automatically trigger the enlarger relay when any timer starts |
| **Auto Safelight Control** | Off | Automatically manage safelight on/off during exposures |
| **Server IP** | Auto-detected | Server network address |
| **Server Port** | Auto-detected | Server port number |
| **Test Connection** | Button | Verify server communication |
| **Test Timer Relay** | Button + duration | Trigger the enlarger relay for a test duration |

### Data Management

| Button | Description |
|--------|-------------|
| **Save All Settings** | Persists all current settings to localStorage immediately |
| **Export All Data** | Creates a comprehensive JSON backup file containing all settings, profiles, presets, calibrations, chemical data, filter banks, and session logs |
| **Import All Data** | Restores from a previously exported backup file. Validates format version and prompts for conflict resolution (overwrite or skip) when duplicate profiles exist |
| **Reset All Settings** | Returns **all** settings to factory defaults and clears **all** saved data including profiles, presets, calibrations, chemical tracking, and logs. **This action cannot be undone.** Always export your data before resetting. |

---

## Cross-Tab Integration & Workflows

### Data Flow Between Tabs

```
METERING ──────────────────→ EXPOSURE & CALCULATOR
    │ (exposure time)                │
    │ (split-grade data)             │ (manual adjustments)
    │                                │
    └───→ SPLIT GRADE ──────→ EXPOSURE & CALCULATOR
                                     │
TEST STRIP ────→ EXPOSURE            │ (start exposure)
           ────→ SPLIT GRADE         │
                                     ▼
                              CONTROLLER
                              (relay triggers, safelight control)
                                     │
                                     ▼
                                TIMER
                              (chemistry auto-chain)
                                     │
                                     ▼
                                LOGS
                              (session recording)
                                     │
                                     ▼
                              CHEMICAL
                              (capacity tracking, shelf-life)
```

### Integration Points

| From → To | Mechanism | Data Transferred |
|-----------|-----------|-----------------|
| METERING → EXPOSURE | "Send to EXPOSURE" button | Calculated exposure time → base time slider |
| METERING → SPLIT GRADE | Split-grade analysis results | Soft/hard times, filter names, ΔEV |
| TEST STRIP → EXPOSURE | Click any step in preview (destination = EXPOSURE) | Step's total time → base time slider |
| TEST STRIP → SPLIT GRADE | Click any step (destination = SPLIT GRADE) | Step's time → neutral time slider |
| SPLIT GRADE → EXPOSURE | "Send to EXPOSURE" button | Soft time, hard time, filter names → split-grade display panel |
| EXPOSURE → CONTROLLER | Auto-trigger (when enabled) | Relay activation/deactivation during exposure |
| EXPOSURE → LOGS | Automatic | Exposure parameters recorded to current session |
| TIMER → LOGS | Automatic | Timer durations recorded; session ends after chain completes |
| TEST STRIP → LOGS | Automatic | Test strip parameters and step results recorded on completion |

### Complete Workflow: New Negative to Final Print

**1. Meter the Negative (METERING tab)**

- Set up paper brand, type, and calibration
- Use the Contrast Analyzer to measure highlight and shadow areas
- Review recommended grade, ΔEV, and suggested exposure time
- Alternatively, use the Split-Grade Analyzer for a two-exposure recommendation

**2. Run a Test Strip (TEST STRIP tab)**

- Set the metered exposure as the base time
- Configure 1/3 stop increments, 6 steps, cumulative method
- Run the automated sequence
- Process the test strip through chemistry
- Tap the best step to transfer its time to the EXPOSURE tab

**3. Fine-Tune Exposure (EXPOSURE & CALCULATOR tab)**

- Adjust the stop slider for minor corrections (±1/3 or ±1/6 stops)
- If you're changing paper size or enlarger height, use the Enlarger & Contrast Calculator
- Execute the exposure — the system handles countdown, relay triggering, and safelight management

**4. Process the Print (TIMER tab)**

- Tap **Start All** to begin the Developer timer
- The auto-chain progresses through Stop Bath → Fixer → Photo Wash
- Transfer paper between trays when each timer beeps

**5. Track Chemistry (CHEMICAL tab)**

- Increment the print counter in the Capacity Tracker
- Check remaining capacity and shelf-life status

**6. Review and Document (LOGS tab)**

- Review all exposure and processing parameters from the session
- Save as permanent if the print is a keeper
- Export CSV or JSON for your records

### Complete Workflow: Split-Grade Printing

**1. Analyze the Scene (METERING tab → Split-Grade Analyzer)**

- Measure highlight and shadow areas of the projected image
- The Heiland algorithm calculates optimal soft and hard exposures with specific filters
- Or use the SPLIT GRADE tab manually with known filter preferences

**2. Configure Split Grade (SPLIT GRADE tab)**

- Select paper brand and type
- Set soft and hard filters as recommended
- Adjust burn percentage to balance highlights and shadows
- Press "Send to EXPOSURE" to transfer the split-grade recipe

**3. Execute Two Exposures (EXPOSURE & CALCULATOR tab)**

- The split-grade panel displays both exposure times and filter names
- Insert the soft filter → expose for the soft time
- Swap to the hard filter → expose for the hard time
- The system manages safelight and relay control for each exposure

**4. Process, Log, and Track**

- Process through the TIMER auto-chain
- Session log captures both exposures with all parameters
- Update chemistry capacity tracking

### Complete Workflow: Same Print, Different Paper Size

You have a successful 8×10" print at 10 seconds and want to make an 11×14" version.

1. **Open the Enlarger & Contrast Calculator** on the EXPOSURE tab
2. Press **Use Current** to load the 10-second base time
3. Enter the original height and the new height (you'll need to raise the enlarger)
4. Select original paper size (8×10") and new paper size (11×14")
5. Adjust aperture and contrast filter if changing those too
6. Read the calculated adjusted time
7. Press **Apply** to set it as the new base time
8. Run a verification test strip centered on the calculated time
9. Fine-tune and print

---

## WiFi & Network Configuration

### Access Point Mode (Default)

On first startup (or when no WiFi credentials are saved), the Darkroom Timer creates its own WiFi network:

| Parameter | Value |
|-----------|-------|
| SSID | DarkroomTimer |
| Password | darkroom123 |
| IP Address | 192.168.4.1 |
| mDNS | darkroom.local |

Connect your device to this network and navigate to `http://192.168.4.1`. The mDNS hostname `darkroom.local` may also work depending on your device's mDNS support.

### Station Mode (Connecting to Your Network)

To connect the Darkroom Timer to your existing WiFi:

1. Go to **CONTROLLER** → WiFi Configuration
2. Enter your network's SSID and password
3. Press **Connect**
4. On successful connection, the access point is disabled to avoid routing conflicts
5. Credentials are saved and persist across reboots

**Benefits of Station Mode:**

- Access the timer from any device on the same network
- Use mDNS hostname (`darkroom.local`) if supported
- Internet access enables over-the-air firmware updates
- Multiple devices can access the interface simultaneously

### Reverting to Access Point Mode

| Method | How |
|--------|-----|
| **From the UI** | Press **Force Hotspot Mode** in the CONTROLLER tab |
| **Clear credentials** | Press **Clear WiFi Credentials** in the CONTROLLER tab |

### Network Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't find DarkroomTimer network | Device not booted or boot error | Ensure power is connected; wait 5+ seconds |
| Connected but page won't load | Wrong IP or mDNS not supported | Use `http://192.168.4.1` directly |
| Lost access after WiFi config | Device switched to station mode | Connect your phone/tablet to the same WiFi network the Darkroom Timer joined |
| Can't access after connecting to home network | IP address changed | Check your router's connected device list for the Darkroom Timer's new IP |

---

## Over-the-Air Updates

The Darkroom Timer supports over-the-air (OTA) firmware updates.

### Checking for Updates

1. **Ensure internet access** — the Darkroom Timer must be connected to your home/studio WiFi network (Station Mode). Updates cannot be checked in Access Point mode.
2. Go to **CONTROLLER** → Updates section
3. Press **Check for Updates**
4. If a newer version is available, update details and download options are displayed

### Installing Updates

1. Press the install button for the available update
2. A progress bar shows download status for each file
3. When all files download successfully, the browser automatically reloads to load the new interface

Updates can include new features, bug fixes, and improvements to both the web interface and the server.

### Version Information

The current firmware version is displayed in the application interface and can be checked at any time from the CONTROLLER tab.

---

## Data Management — Export, Import & Backup

### What Gets Saved Locally

All application data is stored in the browser's localStorage. Important implications:

- Data is **per-browser, per-device** — different devices maintain independent configurations
- Data survives page reloads, browser restarts, and device reboots
- Data is **lost** if you clear browser data, clear site data, or use incognito/private browsing mode

### Automatic Persistence

The following data categories are saved automatically as you work:

| Data Category | Description |
|---------------|-------------|
| Settings | All system preferences (audio, countdown, timers, display) |
| Timer Profiles | Saved chemistry timer configurations |
| Test Strip Profiles | Saved test strip configurations |
| Split-Grade Presets | Saved split-grade settings |
| Chemical Mix Presets | Saved dilution recipes |
| Capacity Tracker Data | Developer usage counters and configuration |
| Shelf-Life Entries | Chemical expiration tracking data |
| Custom Filter Banks | 3 groups × 12 slots of custom filter factors |
| Light Meter Calibrations | Per-paper calibration constants |
| Color Scheme | Selected visual theme |
| Exposure Sessions (Temp) | Recent session data (max 6) |
| Exposure Sessions (Perm) | Permanently saved session data |
| UI State | Collapsible section positions, current profiles |

### Export All Data

Found in **SETTINGS** → Data Management → **Export All Data**.

Creates a JSON file containing all data categories listed above. The file is downloaded to your device with a timestamp in the filename.

### Import All Data

Found in **SETTINGS** → Data Management → **Import All Data**.

1. Select a previously exported JSON file
2. The system validates the file format and version
3. For duplicate profiles or presets, you are prompted to choose: **Overwrite** existing or **Skip** duplicates
4. All data categories are merged into the current application

### Backup Strategy

| Trigger | Action |
|---------|--------|
| After significant configuration changes | Export immediately |
| After a successful printing session | Export to capture new profiles and logs |
| Monthly (even if nothing changed) | Routine backup |
| Before firmware updates | Precautionary export |
| When setting up a new device | Export from old → transfer file → import on new |

**Storage recommendations:**

- Cloud storage (Google Drive, iCloud, Dropbox)
- Email it to yourself as an attachment
- Local backup drive
- Keep copies in at least 2 separate locations

### Reset All Settings

Found in **SETTINGS** → Data Management → **Reset All Settings**.

This permanently erases:

- All settings (returns to defaults)
- All profiles (timer, test strip, split-grade)
- All presets (chemical mixes)
- All tracking data (capacity, shelf-life)
- All calibrations (light meter)
- All filter banks
- All session logs

**Warning:** This action cannot be undone. Always export your data before resetting.

---

## Audio Feedback Reference

### Audio Engine

The application generates tones directly in the browser — no audio files are needed. Sounds work on any device with a web browser and speakers.

**Browser Requirement:** Most browsers require at least one user interaction (tap, click, or button press) before audio can play. If you don't hear any sounds on first use, tap any button once to initialize the audio system and try again.

### Audio Events

| Sound | Pattern | When It Plays |
|-------|---------|---------------|
| **Countdown** | Single beep per second | During pre-exposure countdown (follows selected pattern) |
| **Countdown Urgent** | Higher-pitch beep | Last 3 seconds of countdown (with visual flash effect) |
| **Countdown Final** | Distinct tone | Final second before exposure begins |
| **Countdown Complete** | Completion burst | Countdown reaches zero; exposure starts |
| **Exposure Warning** | Single warning beep | 3 seconds before exposure completes |
| **Exposure Complete** | Double beep | Exposure timer finished |
| **Timer Warning** | Single warning beep | 10 seconds before a chemistry timer completes |
| **Timer Complete** | Distinct completion tone | Chemistry timer finished (followed by auto-chain advance) |
| **Success** | Positive confirmation | Profile saved, data exported, settings applied |
| **Action** | Click feedback | Button press acknowledged |
| **Pause** | Pause tone | Timer paused |
| **Error** | Warning tone | Operation failed or invalid input |
| **Relay On/Off** | Toggle tone | Relay state changed via manual control |
| **Relay Trigger** | Trigger tone | Relay activated/deactivated by a timer |
| **Stable Reading** | Confirmation beep | Virtual Proof cell measurement stabilized |

### Configurable Audio Settings Summary

| Setting | Location | What It Controls |
|---------|----------|-----------------|
| Countdown Beep (master) | SETTINGS → Global | All countdown audio on/off |
| Countdown Pattern | SETTINGS → Global | When during countdown beeps play |
| 3-Second Warning | SETTINGS → Exposure | Exposure ending warning |
| Exposure End Beep | SETTINGS → Exposure | Exposure completion confirmation |
| 10-Second Warning | SETTINGS → Timer | Chemistry timer ending warning |
| Timer End Beep | SETTINGS → Timer | Chemistry timer completion confirmation |
| Virtual Proof Beep | SETTINGS → Metering | Stable reading audio confirmation |

---

## Troubleshooting

### Connection Issues

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| Can't find DarkroomTimer WiFi | Device not powered or boot failed | Check USB power; wait 5+ seconds |
| Page won't load at 192.168.4.1 | Not connected to DarkroomTimer network | Verify WiFi connection on your device |
| Page loads slowly or partially | Large interface file loading | Wait for the full load to complete; avoid refreshing mid-load |
| "Test Connection" fails | Server not running | Power-cycle the Darkroom Timer |
| Intermittent drops | WiFi interference or distance | Move closer to the device; reduce obstacles |
| Relays don't respond | Communication or power issue | Test connection from CONTROLLER; power-cycle if needed |

### Audio Issues

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| No audio at all | Browser audio not initialized | Tap any button once to initialize the audio system |
| No audio on iOS | iOS audio restrictions | Ensure the device is not in Silent Mode; tap a button first |
| Countdown beeps missing | Countdown beep setting disabled | SETTINGS → Global → enable Countdown Beep |
| Warning beeps missing | Warning beep setting disabled | SETTINGS → Exposure or Timer → enable Warning Beep |
| Audio quality poor | Browser limitation | Try a different browser (Chrome/Safari recommended) |

### Timer and Exposure Issues

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| Exposure starts but enlarger doesn't turn on | Auto-trigger disabled | CONTROLLER or SETTINGS → enable Auto-Trigger Enlarger |
| Enlarger stays on after exposure | Communication interrupted | Manually toggle relay OFF in CONTROLLER; check connection |
| Timer chain doesn't auto-advance | Not using Start All | Use **Start All** to initiate the auto-chain (not individual Start) |
| Photo Wash timer skipped | Timer disabled | Enable the Photo Wash timer in TIMER tab |
| Factorial development not calculating | No baseline set | Complete Phase 1 calibration by pressing Mark Baseline first |

### Light Meter Issues

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| No readings / sensor not found | Sensor not connected or detected | Verify the light meter accessory is properly attached |
| Readings very high or very low | Wrong gain setting | Set gain to Auto, or manually select an appropriate level |
| Inconsistent readings | Integration time too short | Increase integration time to 400–600 ms |
| Exposure time doesn't match expectations | Calibration incorrect | Recalibrate using the paper-specific calibration workflow |
| Contrast analyzer gives odd results | Highlight/shadow swapped | Ensure highlight = brightest area, shadow = darkest area |

### Temperature Issues

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| Temperature reads as disconnected | Sensor not attached | Verify the temperature sensor is properly connected |
| Temperature inaccurate | Sensor not in solution | Ensure the sensor probe is submerged in the liquid being measured |
| Heater cycles rapidly on/off | Normal near-target behavior | The ±0.5°C hysteresis is intentional; slight cycling is expected |
| Heater won't activate | Temperature control disabled | Enable temperature control toggle in CONTROLLER tab |

### Data Issues

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| All settings/profiles disappeared | Browser data cleared | Import from a backup file; avoid clearing browser data for this site |
| Settings don't persist after closing browser | Incognito/private browsing | Use a standard (non-private) browser window |
| Import fails with error | Incompatible file format | Ensure the file was exported from this application |
| Different settings on different devices | Expected behavior | localStorage is per-browser/device; use Export/Import to synchronize |

---

## Appendix A — F-Stop Reference Tables

### Understanding F-Stops in Printing

Each full f-stop doubles (or halves) the amount of light reaching the paper. Fractional stops provide finer control:

| Increment | Multiplier | Light Change |
|-----------|-----------|--------------|
| +1/6 stop | ×1.122 | +12.2% more light |
| +1/4 stop | ×1.189 | +18.9% more light |
| +1/3 stop | ×1.260 | +26.0% more light |
| +1/2 stop | ×1.414 | +41.4% more light |
| +1 stop | ×2.000 | +100% more light |
| +2 stops | ×4.000 | +300% more light |
| −1/6 stop | ×0.891 | −10.9% less light |
| −1/4 stop | ×0.841 | −15.9% less light |
| −1/3 stop | ×0.794 | −20.6% less light |
| −1/2 stop | ×0.707 | −29.3% less light |
| −1 stop | ×0.500 | −50.0% less light |
| −2 stops | ×0.250 | −75.0% less light |

### 1/3 Stop Reference Table (10-Second Base)

| Stop | Time (s) | Multiplier | Perceptual Change |
|------|----------|-----------|-------------------|
| −2.00 | 2.50 | 0.250× | 4× less light than base |
| −1.67 | 3.15 | 0.315× | |
| −1.33 | 3.97 | 0.397× | |
| −1.00 | 5.00 | 0.500× | 2× less light than base |
| −0.67 | 6.30 | 0.630× | |
| −0.33 | 7.94 | 0.794× | |
| **0.00** | **10.00** | **1.000×** | **Base exposure** |
| +0.33 | 12.60 | 1.260× | |
| +0.67 | 15.87 | 1.587× | |
| +1.00 | 20.00 | 2.000× | 2× more light than base |
| +1.33 | 25.20 | 2.520× | |
| +1.67 | 31.75 | 3.175× | |
| +2.00 | 40.00 | 4.000× | 4× more light than base |

### General Formula

```
Adjusted Time = Base Time × 2^(Stop Adjustment)
```

Where:

```
Stop Adjustment = Number of Fractional Increments × (1 ÷ Denominator)
```

**Example:** With 1/3 stop increments and +2 clicks on the stop slider:
- Stop Adjustment = 2 × (1/3) = +0.667 stops
- Multiplier = 2^0.667 = 1.587
- If base = 10s → Adjusted = 15.87s

---

## Appendix B — Paper & Filter Database

### Supported Papers

The application includes a comprehensive paper database with manufacturer-measured filter factors (ISO R values) for the following papers:

**Ilford Papers:**

| Paper | Base | Type |
|-------|------|------|
| Multigrade RC Deluxe | Resin-Coated | Variable-contrast, glossy/pearl |
| Multigrade FB Classic | Fibre-Based | Variable-contrast, classic tone |
| Multigrade FB Warmtone | Fibre-Based | Variable-contrast, warm tone |
| Multigrade Art 300 | Art Paper | Variable-contrast, textured |
| Multigrade RC Portfolio | Resin-Coated | Variable-contrast, fine art |
| Multigrade RC Cooltone | Resin-Coated | Variable-contrast, cool tone |
| Multigrade FB Cooltone | Fibre-Based | Variable-contrast, cool tone |

**FOMA Papers:**

| Paper | Base | Type |
|-------|------|------|
| Fomaspeed C311 | Resin-Coated | Glossy |
| Fomaspeed C312 | Resin-Coated | Matte |
| Fomaspeed N111 | Resin-Coated | Normal gradation |
| Fomaspeed N112 | Resin-Coated | Normal gradation, matte |

### Filter Naming Conventions

| Brand | System | Progression (Soft → Hard) |
|-------|--------|--------------------------|
| **Ilford** | Multigrade | Grade 00, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5 |
| **FOMA** | Color Filter | 2×Yellow, Yellow, (None), Magenta 1, 2×Magenta 1, Magenta 2, 2×Magenta 2 |

**Equivalence Guide:**

| Ilford Grade | Approximate FOMA Equivalent | Contrast |
|-------------|---------------------------|----------|
| Grade 00 | 2×Yellow | Very soft (lowest contrast) |
| Grade 0–1 | Yellow | Soft |
| Grade 2 | (None / no filter) | Normal |
| Grade 3 | Magenta 1 | Moderate contrast |
| Grade 4 | 2×Magenta 1 / Magenta 2 | High contrast |
| Grade 5 | 2×Magenta 2 | Very hard (highest contrast) |

Each paper has manufacturer-measured ISO R values and corresponding filter factors for every available grade. These values are used by:

- The **Enlarger & Contrast Calculator** for exposure compensation when changing grades
- The **Split-Grade Calculator** for computing soft/hard exposure times
- The **Light Meter** for applying filter factors to metered readings
- The **Heiland Algorithm** for optimal split-grade filter pair selection

---

**End of Manual**

*Darkroom Timer — Version 1.0.0*  
*For the latest updates, check the CONTROLLER tab → Updates section.*
