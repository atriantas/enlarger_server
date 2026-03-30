# Cyanowood Darkroom Timer — User Manual

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
21. [Appendix C — UI Element Reference (Screenshot Key)](#appendix-c--ui-element-reference-screenshot-key)

---

## Introduction

### About Cyanowood Darkroom Timer

Cyanowood Darkroom Timer is a professional-grade darkroom exposure and workflow management system. It combines precision timing, f-stop exposure calculation, light metering, split-grade printing, chemical tracking, and relay control into a single integrated platform.

The system creates its own WiFi network and hosts a web interface. You connect to it from any device with a web browser — phone, tablet, or laptop — and control your entire darkroom from a single screen.

### Design Principles

**Precision** — All timing uses drift-corrected millisecond-accurate timers. F-stop calculations maintain full photographic precision throughout every operation.

**Safety** — Relays default to OFF on startup. Automatic safelight control eliminates fogging risk during exposures.

**Integration** — Test strip results flow directly into exposure calculations. Split-grade measurements feed into timers. Chemistry tracking connects to your printing sessions. Every feature is designed to work together.

**Workflow** — The interface follows the natural order of darkroom work: metering → testing → calculating → exposing → processing → logging.

### Quick Start

1. Power on the Cyanowood Darkroom Timer
2. Connect your device to the **DarkroomTimer** WiFi network (password: **darkroom123**)
3. Open a browser and navigate to **http://192.168.4.1** (or **http://darkroom.local** if mDNS is supported)
4. The EXPOSURE & CALCULATOR tab opens by default — you're ready to work

---

## Getting Started

### First-Time Setup

**Step 1 — Power On**

Connect the Cyanowood Darkroom Timer to a USB power source. The system boots in approximately 3–5 seconds.

**Step 2 — Connect to WiFi**

The Cyanowood Darkroom Timer creates a WiFi access point automatically:

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

- Color scheme (Darkroom / Light / Night)
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

### Header & Footer

The page header displays **CYANOWOOD TIMER & TOOLS**. The footer shows the application name and current firmware version (e.g., "CYANOWOOD DARKROOM TIMER v1.0.0").

### Tab Bar & Menu

The application is organized into 9 tabs, accessible from a collapsible dropdown menu at the top of the screen. The menu button shows a hamburger icon (☰), the label "Menu", and the name of the currently active tab.

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

### Server Sync Indicator

A sync status indicator appears in the navigation bar beside the menu button. It consists of a colored dot and a text label showing the current sync state between the browser and the Pico server:

| Status | Dot Color | Meaning |
|--------|-----------|---------|
| **ok** | Green | All data synchronized to server |
| **saving** | Orange | Save in progress |
| **pending** | Orange | Changes queued for sync |
| **error** | Red | Sync failed — data preserved locally |
| **offline** | Grey | Server not reachable |

The application stores all settings and profiles in both the browser's localStorage and on the Pico server (via the `/app-data` endpoint). When the server is reachable, data syncs automatically so your settings persist across different devices and browser sessions. If the server is offline, data is preserved locally and will sync when connectivity is restored.

### Color Schemes

Three color schemes are available, selectable from SETTINGS:

| Scheme | Description | Best For |
|--------|-------------|----------|
| **Darkroom** | Dark background with red accents | Working under safelight conditions; preserves night vision |
| **Light** | Light background with warm grey-yellow tones | Daytime setup, planning, or brightly-lit environments |
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

The Exposure Meter mode measures light from the enlarger and calculates an exposure time for the selected paper.

**Paper & Filter Setup (shared across all metering modes):**

| Control | Options | Description |
|---------|---------|-------------|
| **Paper Brand** | Ilford / FOMA | Toggle buttons to select the filter naming system and ISO R data. Synchronized globally across all tabs |
| **Paper Type** | Brand-specific list | Selects the specific paper for calibration lookup |
| **Calibration Display** | Read-only | Shows the current paper name and its calibration constant (lux·s). Auto-saved per paper type |

**Sensor Configuration (in the collapsible SENSOR INFORMATION section):**

| Control | Options | Description |
|---------|---------|-------------|
| **Sensor Type** | Read-only display | Shows the detected sensor model (e.g., TSL2591X) |
| **Connection** | Read-only display | Shows the connection type (e.g., I²C) |
| **Current Gain** | Read-only display | Shows the active gain setting |
| **Integration** | Read-only display | Shows the active integration time |
| **Gain Select** | Auto (recommended), Low (1×), Medium (25×), High (428×), Maximum (9876×) | Sensitivity level. **Auto** adjusts dynamically |
| **Integration Select** | 100ms (fastest), 200ms, 300ms (balanced), 400ms, 500ms, 600ms (most sensitive) | How long the sensor collects light per reading |
| **Apply Sensor Settings** | Button | Sends the selected gain and integration time to the sensor |
| **Refresh Status** | Button | Reloads the sensor readouts |

**Taking a Reading:**

| Control | Description |
|---------|-------------|
| **Averaging Samples** | Slider (1–10) — number of readings averaged per measurement |
| **Sensor Status** | Display — shows whether the sensor is connected and ready |
| **Measure Lux** | Large button — takes a single averaged measurement |
| **Lux Reading** | Display — raw lux value from the sensor |
| **Variance** | Display — measurement variance across samples |
| **Calculated Exposure Time** | Large display — computed exposure time for the selected paper |
| **Filter Grade** | Dropdown (None, Grade 00–5) — applies a filter factor to the reading |
| **Send to EXPOSURE** | Button — transfers the calculated time to the EXPOSURE tab |

**Calculated Exposure:**

```
Exposure Time = Calibration Constant ÷ Lux × Filter Factor
```

The calibration constant is set per paper during calibration (see below).

### Paper-Specific Calibration

Because different papers have different sensitivities, the light meter supports per-paper calibration. The calibration section is a collapsible panel at the bottom of the METERING tab.

**Calibration Procedure:**

1. Select your **Paper Brand** (Ilford or FOMA) and **Paper Type**
2. Make a properly exposed test print using the EXPOSURE or TEST STRIP tab
3. Note the exposure time that produced the correct result

**Two calibration methods are available:**

| Method | Controls | Description |
|--------|----------|-------------|
| **Manual Entry** | Number input + **Save Calibration** button | Enter a known calibration constant directly (lux·s) |
| **Quick Calibration Calculator** | Measured Lux input + Correct Time input + **Calculate & Apply** button | Enter the measured lux and known-good time; the system computes and applies the constant automatically |

Once calibrated, all subsequent metering with this paper type will produce accurate exposure recommendations. Calibrations are auto-saved per paper type.

### Contrast Analyzer

Measures the contrast range of your projected image and recommends an appropriate contrast grade.

**How to Use:**

1. Set the **Averaging Samples** slider (1–10) for desired measurement accuracy
2. Place the sensor under the **brightest highlight area** of the projected image
3. Press **Measure Highlight** — the lux value is stored and displayed
4. Move the sensor to the **deepest shadow area** that should hold detail
5. Press **Measure Shadow** — the lux value is stored and displayed
6. Press **Analyze Contrast** to compute results

**Results Display:**

| Field | Description |
|-------|-------------|
| **ΔEV** | Contrast range in stops (large display) — higher = more contrast |
| **Recommended Grade** | The contrast filter grade that best maps the scene's range to the paper |
| **Match Quality** | How well the recommended grade fits the measured contrast |
| **Analysis Reasoning** | Multi-line explanation of the grade selection logic |
| **Midpoint Time** | Suggested exposure time based on the geometric mean of highlight and shadow |
| **Midpoint Lux** | The midpoint lux value used in the calculation |

**Action Buttons:**

| Button | Action |
|--------|--------|
| **Analyze Contrast** | Computes grade recommendation from highlight/shadow readings |
| **Send Suggested Time to EXPOSURE** | Transfers the midpoint exposure time to the EXPOSURE tab |
| **Clear Readings** | Resets highlight and shadow measurements |

**Interpreting ΔEV:**

| ΔEV Range | Scene Contrast | Recommended Action |
|-----------|----------------|-------------------|
| < 1.5 | Very flat (low contrast) | Use a hard filter (Grade 4–5) to add contrast |
| 1.5–2.5 | Low contrast | Grade 3–4 |
| 2.5–3.5 | Normal contrast | Grade 2–3 (neutral filtration) |
| 3.5–4.5 | High contrast | Grade 1–2 (soft filtration) |
| > 4.5 | Very contrasty | Use a soft filter (Grade 00–1) or consider split-grade printing |

### Split-Grade Analyzer (Heiland Method)

An advanced analysis mode that goes beyond single-grade recommendations. Based on the Heiland densitometry approach, it calculates optimal **two-exposure** (soft + hard) printing parameters with absolute exposure times.

**How It Works:**

After taking highlight and shadow readings:

1. The system computes ΔEV from the lux ratio
2. Using the selected paper's filter data, it selects the optimal soft and hard filter pair
3. It calculates the exposure time for each filter to produce correct highlight density (via the soft exposure) and correct shadow density (via the hard exposure)
4. Results include specific filter names, times, percentages, and paper characteristics

**Results Display:**

| Field | Description |
|-------|-------------|
| **ΔEV** | Contrast range in stops (large display) |
| **Match Quality** | How well the selected filter pair matches the measured contrast |
| **Match Note** | Additional detail about the quality of the match |
| **Analysis Reasoning** | Multi-line explanation of the filter selection logic |

**Paper Characteristics (unique to Split-Grade mode):**

| Field | Description |
|-------|-------------|
| **Printable EV** | The exposure range the paper can reproduce |
| **Gamma (Tone Curve)** | The paper's contrast response curve |
| **Contrast Index** | Numerical contrast index for the paper |
| **Density Range** | Paper density range from Dmin to Dmax |

**Exposure Time Results (displayed in two color-coded boxes):**

| Field | Description |
|-------|-------------|
| **Soft Exposure** | Yellow-tinted box showing the soft filter name, exposure time, and percentage of total |
| **Hard Exposure** | Purple-tinted box showing the hard filter name, exposure time, and percentage of total |
| **Total Exposure Time** | Combined soft + hard time (large display) |

**Action Buttons:**

| Button | Action |
|--------|--------|
| **Calculate Split-Grade** | Computes optimal filter pair and times from highlight/shadow readings |
| **Send Both to EXPOSURE** | Transfers both soft and hard times with filter names to the EXPOSURE tab |
| **Clear Readings** | Resets highlight and shadow measurements |

### Virtual Proof

The Virtual Proof system provides a grid-based sequential scan to rebuild a grayscale preview of your projected image **before making an exposure**, acting like a zone-system spot meter for enlarging.

**How It Works:**

1. Configure the grid size (width × height, up to 50×50 cells)
2. Measure cells one by one — each reading is placed in the next grid position
3. Optionally set a **Zone V Reference** to anchor the tonal scale
4. The system builds a grayscale preview showing predicted print tones
5. A histogram displays the tone distribution across all measured cells

**Grid Configuration:**

| Control | Description |
|---------|-------------|
| **Grid Width** | Number input (1–50) — columns in the grid |
| **Grid Height** | Number input (1–50) — rows in the grid |
| **Apply Grid** | Button — creates/resets the grid to the specified dimensions |
| **Averaging Samples** | Slider (1–10) — readings averaged per cell measurement |
| **Preview Filter Grade** | Dropdown — applies a filter grade to the preview computation |

**Measurement Controls:**

| Control | Description |
|---------|-------------|
| **Measure Next Cell** | Takes a reading and places it in the next empty grid cell |
| **Set Zone V Reference** | Establishes the current cell as the midtone reference point |
| **Recompute Preview** | Recalculates all cell tones (after changing filter grade or reference) |
| **Clear Grid** | Resets all cell measurements |

**Scan Progress Display:**

| Field | Description |
|-------|-------------|
| **Progress** | Shows cells measured vs total (e.g., "12/600") |
| **Status** | Current scan state (Idle, Scanning, Complete) |

**Last Sample Info (updated after each measurement):**

| Field | Description |
|-------|-------------|
| **Lux** | Raw lux value of the last measured cell |
| **Zone** | Predicted zone (0–X) for the cell |
| **ISO R** | ISO R factor applied |
| **EV Range** | Exposure value position relative to reference |
| **Density** | Predicted print density |
| **Exposure** | Calculated exposure for this cell |
| **Clipping** | Whether the cell is clipping to pure white or black |

**Virtual Proof Grid:**

The grid displays a grayscale representation of the measured cells. A legend shows the dark-to-light scale. Below the grid, a **histogram** canvas charts the tone distribution across all measured cells.

**Stability Detection:**

The Virtual Proof uses configurable stability detection to ensure accurate readings. When enabled, the system waits for multiple consecutive readings within a tolerance window before accepting a measurement. An audible beep confirms when a stable reading is captured. Configure tolerance, required stable reads, and maximum wait time in SETTINGS → Metering Settings.

**Practical Use:**

- Map the tonal range of your projected image before committing paper
- Identify areas that will block up (too dark) or blow out (too light)
- Decide whether to burn, dodge, or change grade before the first exposure
- Verify that split-grade filter choices will produce the expected tonal separation
- Use the histogram to evaluate overall tonal distribution

---

## TEST STRIP Tab — F-Stop Test Strip Generator

The TEST STRIP tab automates the creation of f-stop-based test strips, replacing the traditional method of adding equal time increments.

### Why F-Stop Test Strips?

Traditional test strips add the same number of seconds to each step (e.g., 5, 10, 15, 20, 25 seconds). This produces **unequal perceptible differences** between steps — the jump from 5s to 10s is massive (a full stop) while 20s to 25s is barely noticeable (less than 1/3 stop).

F-stop test strips use **geometric** (multiplicative) increments. Each step differs from the next by the same fraction of a stop, producing **visually uniform** steps that are far easier to evaluate.

### Configuration

| Control | Options | Description |
|---------|---------|-------------|
| **Base Time Slider** | Configurable range (default 1–50s) | The starting exposure time for the first step |
| **Stop Denominator** | 1, 1/2, 1/3, 1/4, 1/6 | Stop fraction denominator. 1/3 stop is the default and recommended for most work |
| **Increment** | Slider (1–9 increments) with visual ruler | Number of fractional increments per step. Combined with the denominator, this determines step size (e.g., 1 increment at 1/3 = ⅓ stop per step) |
| **Number of Steps** | 3–12 | Total steps in the test strip |
| **Method** | Cumulative / Incremental | How the test strip is exposed |
| **Auto Advance** | ON / OFF toggle | Automatically advance to the next step after a configurable delay |
| **Transfer Destination** | EXPOSURE / SPLIT GRADE | Segmented control — where the selected step's time is sent when tapped |

### Methods Explained

**Cumulative (Recommended):**

Each step adds exposure to the entire sheet. The paper is uncovered one section at a time during the sequence.

- Step 1: Expose entire sheet for *t₁* seconds
- Step 2: Cover the first section; expose remaining sheet for *t₂ − t₁* additional seconds
- Step 3: Cover the next section; expose remaining for *t₃ − t₂* additional seconds
- Continue until all steps are complete

This is the traditional enlarging test-strip technique adapted to f-stop spacing.

**Incremental:**

Each step is an independent, separate exposure of the stated duration. This is useful when testing individual exposure times on separate pieces of paper.

### Step Preview

### Test Strip Layout (Visual Preview)

Before running the strip, a **2D grid preview** displays all steps visually. Each cell shows the step number and can be toggled between time display and density-shading display using the **Show Times** checkbox.

**Sequence Information Panel:**

| Field | Description |
|-------|-------------|
| **Sequence Info** | Summary (e.g., "6 steps × ⅓ stop") |
| **Time Range** | Full range (e.g., "10.00s to 31.75s") |

**Instructions Panel:** Displays method-specific instructions (different for Cumulative vs Incremental). Also shows auto-advance status when enabled.

**Transfer Destination:** Tap any step in the preview to send its exposure time to the selected destination tab (EXPOSURE or SPLIT GRADE).

### Running the Test Strip

The timer section shows three columns during execution: the current step number (e.g., "1/6"), a large central timer display, and the step's target time.

A **progress bar** spans the bottom showing overall progress with start and end time labels.

| Button | Action |
|--------|--------|
| **Start Test Strip** | Begins the automated test strip sequence. A pre-exposure countdown runs first (configurable in SETTINGS). |
| **Stop** | Suspends the current exposure |
| **Reset** | Resets the test strip timer to the beginning |

**Notes Input:** A text field for annotations (e.g., "Portrait - find base exposure") that gets saved with the session log.

**Step Information (4-column grid):**

| Field | Description |
|-------|-------------|
| **Step Size** | Current step size in stops |
| **Current Stop** | Current stop offset |
| **Time Multiplier** | Current step's time multiplier |
| **Total Time** | Total cumulative time for the entire sequence |

**Auto-Advance** (configurable in SETTINGS): When enabled, each step automatically advances after a configurable delay (default: 1 second pause between steps). This provides hands-free operation — you only need to cover the next section of paper during each pause.

### Profiles

Test strip configurations can be saved and loaded via the collapsible **TEST STRIP PROFILES** section:

| Action | Description |
|--------|-------------|
| **Save Current as Profile** | Saves base time, increment, step count, and method with a custom name (max 20 characters) |
| **Load** | Restores a saved test strip configuration (via list item button) |
| **Delete** | Removes a specific profile (via list item button) |
| **Clear All** | Removes all saved test strip profiles |

### Test Strip Tips

- **Start with 1/3-stop increments, 6–7 steps**: This covers about 2 stops of range, usually enough to bracket the correct exposure.
- **Center the strip on your estimate**: If you think 10 seconds is about right, set the base time to about 6 seconds for a 7-step strip. The correct exposure will likely fall in the middle.
- **Evaluate under a white light**: Switch to the White Light relay in CONTROLLER to inspect your test strip under consistent illumination.
- **Select your best step**: Tap it in the preview to transfer its time directly to the EXPOSURE or SPLIT GRADE tab.

---

## SPLIT GRADE Tab — Split-Grade Exposure Calculator

Split-grade printing uses two separate exposures — one with a soft (low-contrast) filter and one with a hard (high-contrast) filter — to independently control highlight and shadow density. This provides more control than a single-grade approach and is especially effective with contrasty negatives.

### Controls

| Control | Options | Description |
|---------|---------|-------------|
| **Neutral Time Slider** | Configurable range (0.4–50s) | The base exposure time assuming a Grade 2 (neutral) filter |
| **Paper Brand** | Ilford / FOMA | Toggle buttons — selects the filter naming system and ISO R data. Synchronized globally — changing brand here updates all other tabs |
| **Paper Type** | Brand-specific list | Selects the specific paper for filter factor lookup |
| **Soft Filter** | 7 grade buttons (00, 0, 1, 2, 3, 4, 5) | Segmented control — the low-contrast filter for highlight control |
| **Hard Filter** | 7 grade buttons (00, 0, 1, 2, 3, 4, 5) | Segmented control — the high-contrast filter for shadow control |
| **Shadow Time Allocation** | 0–100% (step 5%) | Slider that controls the balance between soft and hard exposures. 50% = equal weight; lower values shift time toward highlights (soft), higher values toward shadows (hard) |

### How Split-Grade Times Are Calculated

The neutral time is split between soft and hard exposures based on the Shadow Time Allocation percentage, then each half is multiplied by the paper-specific ISO R filter factor:

```
Soft Base = Neutral Time × (100 − Shadow%) ÷ 100
Hard Base = Neutral Time × Shadow% ÷ 100
Soft Time = Soft Base × Soft Filter ISO R Factor
Hard Time = Hard Base × Hard Filter ISO R Factor
```

The ISO R factors come from the paper database and are manufacturer-measured values specific to each paper and filter combination. These factors compensate for the different light absorption of each filter, ensuring that the soft and hard exposures contribute the correct amount of density.

### Results Display

The results panel shows:

| Field | Description |
|-------|-------------|
| **Base Times (Before Filters)** | The soft and hard base times before filter factors are applied |
| **Highlights (Soft + Factor)** | The soft filter name and its calculated exposure time including the filter factor |
| **Shadows (Hard + Factor)** | The hard filter name and its calculated exposure time including the filter factor |
| **Total Exposure** | Combined soft + hard time |
| **Split Ratio** | The ratio of soft to hard time (e.g., "60% / 40%") |
| **Effective Contrast Grade** | The approximate single-grade equivalent of the current split-grade combination (e.g., "~Grade 2.5") |

### Transfer Options

| Button | Action |
|--------|--------|
| **Send to EXPOSURE** | Transfers both soft and hard filter names and times to the EXPOSURE tab's split-grade panel |

### Split-Grade Presets

Split-grade configurations can be saved and loaded via the collapsible **SPLIT-GRADE PRESETS** section:

| Action | Description |
|--------|-------------|
| **Save Current as Preset** | Saves neutral time, filters, allocation, and paper type with a custom name (max 20 characters) |
| **Load** | Restores a saved preset (via list item button) |
| **Delete** | Removes a specific preset (via list item button) |
| **Clear All** | Removes all saved split-grade presets |

### Split-Grade Tips

- **Start at 50% Shadow Time Allocation** and adjust from there. The slider shifts the balance between soft and hard exposures.
- **Use the METERING tab's Split-Grade Analyzer** if you have a light meter — it will calculate the optimal soft/hard filter selection and times automatically based on actual scene measurements.
- **Low-contrast negatives** benefit from a harder-biased split (higher shadow allocation).
- **High-contrast negatives** benefit from a softer-biased split (lower shadow allocation, or the Heiland algorithm's two-exposure approach).

---

## EXPOSURE & CALCULATOR Tab — Exposure Timer & Adjustments

The EXPOSURE & CALCULATOR tab is the primary exposure control interface. It combines a precision incremental exposure timer, f-stop exposure compensation, split-grade display, and an enlarger/contrast calculator into one unified panel.

### Split-Grade Times Display

When a split-grade recipe is sent from the SPLIT GRADE or METERING tab, a panel appears at the top of the tab showing:

| Field | Description |
|-------|-------------|
| **Neutral Time** | The base neutral time used for the split calculation |
| **Base Times (Burn Split)** | The time split before filter factors are applied |
| **Total Exposure** | Combined soft + hard time |
| **Highlights** | Button showing the soft filter time — tap to load as the current exposure |
| **Shadows** | Button showing the hard filter time — tap to load as the current exposure |
| **Clear Split Data** | Button to dismiss the split-grade panel |

This panel allows you to execute each split-grade exposure by tapping the Highlights or Shadows button to set the exposure time, then running the timer for each.

### Exposure Timer

**Base Time Slider:** Sets the exposure time. The slider range is configurable in SETTINGS (default: 0.4–50 seconds).

**Stop Denominator:** Segmented control with 5 options (1, 1/2, 1/3, 1/4, 1/6) — selects the f-stop fraction denominator. A value of "1" gives full-stop increments.

**Stop Adjustment Slider:** Adjusts the exposure in fractional f-stop increments. The slider has a dynamic visual ruler showing stop markings. The range is ±6 stops at the selected denomination.

**Selected Exposure Display:** Shows the final exposure time after applying the stop adjustment, along with the stop offset description (e.g., "BASE (0.0 stops)"):

```
Final Time = Base Time × 2^(Stop Adjustment)
```

### Incremental Exposure Timer

The timer section is designed for incremental (additive) printing workflows — each exposure adds to the cumulative total from previous exposures in the session.

**Timer Status:** Shows the current state (e.g., "READY FOR EXPOSURE", "EXPOSING", "PAUSED").

**Timer Display:** Large central display showing remaining time during countdown.

**Notes Input:** Text field for session annotations (e.g., "Added 1 stop - perfect").

**Timer Control Buttons:**

| Button | Action |
|--------|--------|
| **Start Exposure** | Begins the pre-exposure countdown, then runs the exposure timer |
| **Stop** | Pauses/stops the current exposure |
| **Reset** | Resets the timer to the selected exposure time |
| **Repeat Last** | Repeats the previous exposure with the same time (available after first exposure) |

**Exposure Information (4-box grid):**

| Field | Description |
|-------|-------------|
| **Selected Stop** | The current stop adjustment value |
| **Previous Total** | Cumulative exposure time from all previous exposures |
| **Current Total** | Running total including the current exposure |
| **This Exposure** | Time for the current exposure only |

### Transfer to TIMER Tab

A full-width button at the bottom of the exposure section: **Transfer to TIMER Tab →**. This sends the current exposure data to the TIMER tab and switches to it, enabling a seamless transition from exposure to chemistry processing.

### Countdown & Exposure Sequence

When you press **Start Exposure**:

1. A pre-exposure **countdown** begins (default: 5 seconds, configurable in SETTINGS). This gives you time to position the paper, remove the safe filter, or prepare.
2. During the last 3 seconds, urgent beeps and a visual flash alert you.
3. At zero, the exposure begins. If **Auto-Trigger Enlarger** is enabled, the enlarger relay activates automatically.
4. If **Auto Safelight Control** is enabled, the safelight turns off during the exposure and restores afterward.
5. The timer counts down, showing remaining time.
6. A **3-second warning beep** (configurable) sounds before completion.
7. At zero, an **end beep** (configurable) confirms the exposure is finished, and the enlarger relay deactivates.

### Enlarger & Contrast Calculator

A comprehensive tool for recalculating exposure times when changing enlarger height, lens aperture, paper size, or contrast filter grade. Each adjustment section is collapsible.

**Original Time:** Displays the original exposure time. Press **Use Current Exposure Time** to copy the current exposure time as the starting point.

**Head Height Adjustment (collapsible):**

Two side-by-side controls for Original and New height, each with:
- Coarse slider (10–60 cm, step 1)
- Fine slider (±0.5 cm, step 1)

**F-Stop Adjustment (collapsible):**

Two dropdown selects for Original and New f-stop: f/2.8, f/4, f/5.6, f/8, f/11, f/16, f/22, f/32.

**Paper Size Adjustment (collapsible):**

Two dropdown selects for Original and New paper size:
- Presets: 3.5×5", 4×5", 5×7", 8×10", 11×14", 16×20"
- Custom option with number input (0.001–1 m²) and Set button

**Contrast Filter Adjustment (collapsible):**

- Paper brand toggle (Ilford / FOMA) — synchronized globally
- Paper type selector — same paper variants as METERING and SPLIT GRADE tabs
- Displays the **ISO R** value and **Contrast Factor** for the selected combination

**Calculation Formula:**

```
Adjusted Time = Original Time
                × (New Height ÷ Original Height)²
                × (New F-Stop ÷ Original F-Stop)²
                × (√New Paper Area ÷ √Original Paper Area)²
                × Filter Factor
```

**Combined Factors Display (5-column grid):** Shows each individual factor as a multiplier:

| Factor | Description |
|--------|-------------|
| **Height Factor** | (New Height ÷ Original Height)² |
| **F-Stop Factor** | (Original F-Stop ÷ New F-Stop)² |
| **Paper Factor** | (New Paper Area ÷ Original Paper Area) |
| **Contrast Factor** | ISO R filter factor from paper database |
| **Custom Factor** | From the Custom Filter Bank (if selected) |

Below the factor grid: **Combined Factor** (product of all factors) and **New Adjusted Time** (Original Time × Combined Factor) displayed prominently.

### Custom Filter Banks (collapsible)

The Custom Filter Bank Manager provides 3 groups (A, B, C) with slots for storing custom filter factors.

**Use Cases:**

- **Group A:** Your standard variable-contrast paper grades
- **Group B:** Graded papers or alternative brands
- **Group C:** Experimental or specialty filters

Each slot has a label and a numeric filter factor. These factors feed into the Enlarger & Contrast Calculator's combined factor calculation, allowing you to layer a custom multiplier on top of the paper-specific ISO R factor.

---

## TIMER Tab — Chemistry Processing

The TIMER tab manages four independent chemistry timers that can run sequentially in an automated chain.

### Timer Grid

Four timers are displayed in a 2×2 grid:

| Timer | Default Duration | Purpose |
|-------|-----------------|---------|
| **Developer** | 60 seconds (1:00) | Controls development time — the most critical chemistry step |
| **Stop Bath** | 30 seconds (0:30) | Neutralizes developer; prevents carryover |
| **Fixer** | 300 seconds (5:00) | Removes unexposed silver; essential for print permanence |
| **Photo Wash** | 60 seconds (1:00) | Final rinse; removes fixer residue |

Default durations are configurable in SETTINGS.

### Individual Timer Controls

Each timer has:

- **Timer Name:** Label (e.g., "Developer")
- **Time Display:** Shows remaining time in MM:SS format during countdown
- **Elapsed Time:** Small display showing elapsed time below the main display
- **−1s / +1s Buttons:** Tap to adjust by 1 second
- **Start / Pause:** Begins or pauses the countdown (button text toggles)
- **Reset:** Returns to the default duration (enabled after timer starts)

### Auto-Start Chain

When the auto-start chain is invoked, starting the timer sequence triggers an automated progression:

1. **Countdown** (if configured) → **Developer** starts
2. Developer completes → **Stop Bath** automatically starts
3. Stop Bath completes → **Fixer** automatically starts
4. Fixer completes → **Photo Wash** automatically starts
5. Photo Wash completes → **Chain complete**

**Global Controls:**

| Button | Action |
|--------|--------|
| **Start All** | Initiates the countdown and begins the Developer timer. The chain auto-advances through all timers. |
| **Reset All** | Resets all four timers to their default durations |

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

Timer configurations can be saved and loaded via the collapsible **TIMER PROFILES** section:

| Action | Description |
|--------|-------------|
| **Save Current as Profile** | Saves all four timer durations plus factorial multiplier with a custom name (max 20 characters) |
| **Load** | Restores a saved timer configuration (via list item button) |
| **Delete** | Removes a specific profile (via list item button) |
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

The CHEMICAL tab provides three tools for managing darkroom chemistry, each in a collapsible section: a developer capacity tracker, a shelf-life tracker, and a chemical mix calculator.

### Developer Capacity Tracker (collapsible)

Tracks how many prints your developer can process before exhaustion. Takes into account the developer's concentrate capacity, dilution ratio, tray volume, and paper size.

**Controls:**

| Control | Range | Description |
|---------|-------|-------------|
| **Bottle Spec** | Slider, 0.5–30 m²/L concentrate | Developer capacity per the manufacturer's specification (in m² per liter of concentrate) |
| **Dilution** | Toggle buttons: 1+4, 1+9, 1+14, 1+19, 1+29, 1+39 + Custom | The working dilution ratio. Custom allows entering arbitrary stock + water parts |
| **Working Capacity** | Read-only display | Calculated working capacity in m²/L after dilution |
| **Tray Volume** | Slider, 100–5000 ml (step 100) | Amount of working developer in your tray |
| **Paper Size** | Toggle buttons: 3.5×5", 4×5", 5×7", 8×10", 11×14", 16×20" + Custom | The paper size you're printing (shows area in m²) |

**Calculated Display:**

| Field | Description |
|-------|-------------|
| **Max Prints This Batch** | Large display — how many prints the current tray can process |
| **Remaining** | Prints remaining with area |

**Progress Bar:** Visual indicator that fills as the developer is consumed, with 0 and max labels.

**Print Counter Buttons:**

| Button | Action |
|--------|--------|
| **+1 Print** | Add one print to the count |
| **+5 Prints** | Add five prints (for batch counting) |
| **Reset** | Clear the print count (do this when mixing fresh developer) |

**Status Display (4-column grid):**

| Field | Description |
|-------|-------------|
| **Prints Done** | Number of prints processed in this batch |
| **Area Used** | Total paper area processed in m² |
| **% Used** | Percentage of developer capacity consumed |
| **Status** | Color-coded condition indicator (Fresh, OK, Low, Replace) |

### Shelf-Life Tracker (collapsible)

Monitors the expiration of your darkroom chemicals so you never accidentally use expired solutions.

**Adding a Chemical:**

| Control | Description |
|---------|-------------|
| **Chemical Type** | Dropdown: Developer, Stop Bath, Fixer, Hypo Clear, Photo Wash, or Custom |
| **Custom Name** | Text input (visible only when "Custom" is selected, e.g., "Selenium Toner") |
| **Shelf Life (days)** | Number input (1–365, default 30) |
| **Date Mixed** | Date picker — the date the chemical was mixed or opened |
| **Add Chemical** | Button — adds the chemical to the tracking list |

**Active Chemicals List:**

Each tracked chemical displays:

- Chemical name and type
- Date mixed
- Days remaining until expiration
- Color-coded status indicator

**Status Colors:**

| Days Remaining | Visual | Meaning |
|----------------|--------|---------|
| > 3 days | Green background | Fresh — no action needed |
| 1–3 days | Orange background | Expires soon — plan replacement |
| ≤ 0 days | Red background | **EXPIRED — Do not use** |

**Management Button:**

| Button | Action |
|--------|--------|
| **Clear Expired** | Removes all expired entries in one action |

### Chemical Mix Calculator (collapsible)

Calculates stock and water volumes for any dilution ratio.

**Controls:**

| Control | Range | Description |
|---------|-------|-------------|
| **Total Volume** | Slider, 100–5000 ml (step 50) | The total amount of working solution you need |
| **Dilution Ratio** | Toggle buttons: 1+9, 1+14, 1+19, 1+24, 1+29, 1+39 | Quick-select preset dilutions |
| **Custom Ratio** | Two number inputs (Stock parts + Water parts, 1–100) | For non-standard dilutions |

**Mixing Instructions (results panel):**

| Field | Description |
|-------|-------------|
| **Stock Volume** | Large display — amount of stock concentrate required |
| **Water Volume** | Large display — amount of water required |
| **Instruction** | "Add stock to water, not water to stock" |

**Calculation:**

```
Stock Volume = Total Volume × Stock Parts ÷ (Stock Parts + Water Parts)
Water Volume = Total Volume × Water Parts ÷ (Stock Parts + Water Parts)
```

### Chemical Mix Presets (collapsible)

Save frequently used chemistry mixes for one-tap recall:

| Action | Description |
|--------|-------------|
| **Save Current as Preset** | Saves current volume and dilution ratio with a custom name (max 20 characters) |
| **Load** | Restores a saved mix configuration (via list item button) |
| **Delete** | Removes a specific preset (via list item button) |
| **Clear All** | Removes all saved chemical presets |

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

Four relays are available, each with a text input for the custom name and a toggle button showing the current state (OFF/ON):

| Relay | GPIO Pin | Default Label | Function |
|-------|----------|---------------|----------|
| **Relay 1** | GP14 | Enlarger | Controls the enlarger lamp power |
| **Relay 2** | GP15 | Safelight | Controls the safelight |
| **Relay 3** | GP16 | Heater | Controls a heating element (for temperature-controlled processing) |
| **Relay 4** | GP17 | White Light | Controls a white inspection light |

**Relay names are customizable** — edit the text input next to each relay to rename them.

**Bulk Controls:**

- **All ON:** Activates all four relays simultaneously
- **All OFF:** Deactivates all four relays simultaneously — use as an emergency stop

**Safety Note:** Manually turning off a relay will stop any active timer or exposure associated with that relay. This provides an immediate override for any operation in progress.

### Temperature Control

> **Requires:** Temperature sensor (optional DS18B20 accessory on GP18)

The temperature control system monitors your processing environment and can automatically maintain a target temperature using the heater relay (GP16).

**Controls:**

| Element | Description |
|---------|-------------|
| **Enable/Disable Toggle** | Toggle switch to activate or deactivate temperature monitoring and heating control |
| **Current Temperature** | Large display (1.8em) showing live reading from the sensor |
| **Temperature Status** | Text label showing state (e.g., "Disabled", "Heating", "At Target") |
| **Target Temperature** | Number input (15–50°C, step 0.5, default 20.0) |
| **Set Target** | Button to apply the target temperature |
| **Heating (GP16)** | Relay status display showing ON/OFF |
| **Dead Zone** | Display showing hysteresis value (±0.5°C) |

**Temperature Display Colors:**

| Condition | Color | Meaning |
|-----------|-------|---------|
| Heating active | Blue | Temperature is below target; heater is running |
| At target (±0.5°C) | Green | Temperature is within range |
| Close to target | Orange | Temperature is approaching the target |

**Hysteresis Control:** The system uses a ±0.5°C dead zone to prevent rapid on/off cycling of the heater. The heater turns on when the temperature drops 0.5°C below the target and turns off when it reaches 0.5°C above the target.

**History Chart:** A 15-minute temperature history graph (canvas element) shows temperature stability over time, updated every 15 seconds. A data point counter shows the number of readings collected.

**Sensor Disconnection Alert:** If the temperature sensor is disconnected, a warning box appears: "⚠️ Sensor Disconnected - Relay OFF" and the heater relay is automatically turned off for safety.

**Use Case:** Maintaining consistent developer temperature (typically 20°C / 68°F) is critical for repeatable results. The temperature control system can heat a water bath or developer tray to the target temperature and hold it there throughout your printing session.

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
| **Color Scheme** | Darkroom / Light / Night | Sets the visual theme for the entire application |

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

Under the "Virtual Proof Stability" heading:

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Stability Detection** | Off | Toggle | Enable/disable stability detection for Virtual Proof cell measurements |
| **Beep on Stable** | Off | Toggle | Play audible confirmation when a stable reading is captured |
| **Tolerance %** | 2.5% | 0.5–10% (step 0.1) | Percentage variation threshold (smaller = stricter stability requirement) |
| **Min Stable Reads** | 2 | 1–5 | Number of consecutive stable readings required before accepting |
| **Max Wait (ms)** | 900 ms | 300–3000 (step 50) | Maximum time to wait for stability; accepts current value if exceeded |
| **Min Delta Lux** | 0.2 lux | 0.05–5 (step 0.05) | Minimum absolute lux change to register as a genuinely new reading |

### Test Strip Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Auto Advance** | Off | Toggle | Automatically advance test strip steps after the configured delay |
| **Auto Advance Delay** | 1s | 0–30s (step 1) | Time between auto-advance steps (increase for more evaluation time) |
| **Test Base Time Min** | 1s | 0.5–10s (step 0.5) | Lower limit for the test strip base time slider |
| **Test Base Time Max** | 50s | 10–300s (step 1) | Upper limit for the test strip base time slider |

### Exposure Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Base Time Min** | 0.4s | 0.1–10s (step 0.1) | Lower limit for the exposure base time slider |
| **Base Time Max** | 50s | 10–300s (step 1) | Upper limit for the exposure base time slider |
| **3-Second Warning Beep** | On | Toggle | Audio alert 3 seconds before an exposure completes |
| **End Beep** | On | Toggle | Audio confirmation when an exposure completes |

**Tip:** Setting the base time min/max to your typical working range (e.g., 5–30 seconds) makes the slider more sensitive and easier to adjust precisely.

### Timer Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Default Dev Time** | 60s (1:00) | 5–600s (step 5) | Default developer timer duration |
| **Default Stop Time** | 30s (0:30) | 5–300s (step 5) | Default stop bath timer duration |
| **Default Fix Time** | 60s (1:00) | 5–600s (step 5) | Default fixer timer duration |
| **Default Flo Time** | 30s (0:30) | 5–300s (step 5) | Default photo wash timer duration |
| **10-Second Warning Beep** | On | Toggle | Audio alert 10 seconds before a chemistry timer completes |
| **End Beep** | On | Toggle | Audio confirmation when a chemistry timer completes |

### Controller Settings

This collapsible section contains all hardware-related settings: relay automation, server connection, WiFi networking, and firmware updates.

#### Auto – Manual Enlarger Control

| Setting | Default | Description |
|---------|---------|-------------|
| **Auto-trigger Enlarger** | On | When enabled, starting any timer automatically activates the enlarger relay |
| **Auto Safelight Control** | On | When enabled, the safelight automatically turns off during exposures and restores afterward |

**Note:** Auto-trigger controls the enlarger relay during timers. Auto Safelight automatically manages the safelight relay when the enlarger is active.

#### Controller Manager

| Element | Description |
|---------|-------------|
| **Server IP** | Auto-detected from the page URL (read-only) |
| **Server Port** | Auto-detected from URL, typically 80 (read-only) |
| **Test Connection** | Sends a health check request to verify communication. Shows status below the button |
| **Test Timer Relay** | Enter a duration (0.1–60s, default 5s) and trigger the enlarger relay for a test exposure |

#### WiFi Configuration

**Help text:** "Connect to a WiFi router for mDNS access (darkroom.local)"

| Element | Description |
|---------|-------------|
| **WiFi SSID** | Text input for your network name |
| **WiFi Password** | Password input for your network credentials |
| **Connect to WiFi** | Attempts to connect to the entered SSID/password. Credentials are saved to the device |
| **Force Hotspot Mode** | Disconnects from any WiFi network and reactivates the built-in access point |
| **Clear WiFi Credentials** | Removes saved WiFi credentials from the device |
| **WiFi Status** | Shows current connection mode and IP address (default: "AP Mode (192.168.4.1)") |

**Note:** After connecting to WiFi, access the device via `darkroom.local`.

#### Updates

**Help text:** "Check for new versions from GitHub and update automatically"

| Element | Description |
|---------|-------------|
| **Current Version** | Displays the installed firmware version |
| **Latest Version** | Displays the newest available version (or "Unknown" before checking) |
| **Check for Updates** | Checks GitHub for new releases. Requires internet access (Station Mode) |
| **Update Status** | Shows "Ready", download progress, or error messages |
| **Progress Bar** | Appears during download — shows percentage completion |

**Note:** The Pico will restart automatically after a successful update.

#### Auto Safelight Control — Detailed Behavior

When Auto Safelight Control is enabled:

1. An exposure starts (from EXPOSURE, TEST STRIP, or TIMER tabs)
2. The system checks the current safelight relay state
3. If the safelight is ON, its state is remembered
4. The safelight relay is turned OFF
5. The enlarger relay activates and the exposure runs
6. After the exposure completes, a 0.5-second buffer is added
7. The safelight relay is restored to its previous state

This eliminates the risk of safelight fogging during exposure — a common cause of ruined prints.

### Save All Settings

A single **Save All Settings** button (primary/accent style) persists all current settings to localStorage. A confirmation message appears below the button after saving.

### Profile & Settings Sharing

| Button | Description |
|--------|-------------|
| **Export All Data** | Creates a downloadable JSON backup file containing Timer Profiles, Chemical Presets, Capacity Tracker, and Shelf-Life Data |
| **Import All Data** | Loads previously exported JSON data back into the application. Accepts `.json` files only |

### Reset

| Element | Description |
|---------|-------------|
| **Reset All Settings** | Red danger button. Returns **all** settings to factory defaults and clears **all** saved data including profiles, presets, calibrations, chemical tracking, and logs. **This action cannot be undone.** |

**Warning text:** "This will reset all settings to defaults and clear all data"

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

On first startup (or when no WiFi credentials are saved), the Cyanowood Darkroom Timer creates its own WiFi network:

| Parameter | Value |
|-----------|-------|
| SSID | DarkroomTimer |
| Password | darkroom123 |
| IP Address | 192.168.4.1 |
| mDNS | darkroom.local |

Connect your device to this network and navigate to `http://192.168.4.1`. The mDNS hostname `darkroom.local` may also work depending on your device's mDNS support.

### Station Mode (Connecting to Your Network)

To connect the Cyanowood Darkroom Timer to your existing WiFi:

1. Go to **SETTINGS** → Controller Settings → WiFi Configuration
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
| **From the UI** | Press **Force Hotspot Mode** in SETTINGS → Controller Settings → WiFi Configuration |
| **Clear credentials** | Press **Clear WiFi Credentials** in SETTINGS → Controller Settings → WiFi Configuration |

### Network Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't find DarkroomTimer network | Device not booted or boot error | Ensure power is connected; wait 5+ seconds |
| Connected but page won't load | Wrong IP or mDNS not supported | Use `http://192.168.4.1` directly |
| Lost access after WiFi config | Device switched to station mode | Connect your phone/tablet to the same WiFi network the device joined |
| Can't access after connecting to home network | IP address changed | Check your router's connected device list for the device's new IP |

---

## Over-the-Air Updates

The Cyanowood Darkroom Timer supports over-the-air (OTA) firmware updates.

### Checking for Updates

1. **Ensure internet access** — the device must be connected to your home/studio WiFi network (Station Mode). Updates cannot be checked in Access Point mode.
2. Go to **SETTINGS** → Controller Settings → Updates
3. Press **Check for Updates**
4. If a newer version is available, update details and download options are displayed

### Installing Updates

1. Press the install button for the available update
2. A progress bar shows download status for each file
3. When all files download successfully, the browser automatically reloads to load the new interface

Updates can include new features, bug fixes, and improvements to both the web interface and the server.

### Version Information

The current firmware version is displayed in the application footer and in SETTINGS → Controller Settings → Updates.

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
| "Test Connection" fails | Server not running | Power-cycle the device |
| Intermittent drops | WiFi interference or distance | Move closer to the device; reduce obstacles |
| Relays don't respond | Communication or power issue | Test connection from SETTINGS → Controller Settings; power-cycle if needed |

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
| Exposure starts but enlarger doesn't turn on | Auto-trigger disabled | SETTINGS → Controller Settings → enable Auto-trigger Enlarger |
| Enlarger stays on after exposure | Communication interrupted | Manually toggle relay OFF in CONTROLLER; check connection |
| Timer chain doesn't auto-advance | Not using Start All | Use **Start All** to initiate the auto-chain (not individual Start) |
| Photo Wash timer skipped | Timer set to 0 or chain not started | Set a duration > 0 for Photo Wash in TIMER tab; use **Start All** for the full chain |
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
| MULTIGRADE RC DELUXE (NEW) | Resin-Coated | Variable-contrast, current production |
| MULTIGRADE RC PORTFOLIO (NEW) | Resin-Coated | Variable-contrast, current production |
| Multigrade IV RC Portfolio (Discontinued) | Resin-Coated | Variable-contrast, legacy reference data |
| Multigrade FB Classic | Fibre-Based | Variable-contrast, classic tone |
| Multigrade RC Cooltone | Resin-Coated | Variable-contrast, cool tone |
| Multigrade FB Warmtone | Fibre-Based | Variable-contrast, warm tone |
| Multigrade FB Cooltone | Fibre-Based | Variable-contrast, cool tone |

**FOMA Papers:**

| Paper | Base | Type |
|-------|------|------|
| FOMASPEED VARIANT | Resin-Coated | Variable-contrast |
| FOMABROM VARIANT | Fibre-Based | Variable-contrast |
| FOMAPASTEL MG (Special FB Colored Base) | Fibre-Based | Variable-contrast, colored base |
| FOMATONE MG Classic (Warm Tone) | Fibre-Based | Variable-contrast, warm tone |

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

## Appendix C — UI Element Reference (Screenshot Key)

This appendix provides a numbered reference for every visible UI element, organized by tab. Use these numbers to annotate screenshots with corresponding labels.

### Global Elements (Header, Navigation, Footer)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | App title | Text | "CYANOWOOD TIMER & TOOLS" header banner |
| 2 | Sync indicator dot | Status icon | Colored circle — green (OK), orange (saving), red (error), gray (offline) |
| 3 | Sync status label | Text | Shows sync state ("Synced", "Saving…", "Offline", etc.) |
| 4 | Menu button | Button | Hamburger icon + active tab name — opens tab dropdown |
| 5 | Active tab name | Text | Displays current tab name inside menu button |
| 6 | Tab dropdown menu | Menu | Lists all 9 tabs: METERING, TEST STRIP, SPLIT GRADE, EXPOSURE & CALCULATOR, TIMER, CHEMICAL, CONTROLLER, LOGS, SETTINGS |
| 7 | Footer | Text | "CYANOWOOD DARKROOM TIMER v1.0.0" |

---

### EXPOSURE & CALCULATOR Tab

#### Split-Grade Times Display (visible when split-grade data is active)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Split-Grade display panel | Container | Shows split-grade exposure data |
| 2 | Neutral time label | Text | "NEUTRAL TIME" |
| 3 | Neutral time value | Readout | Neutral exposure time |
| 4 | Base times label | Text | "BASE TIMES (Burn Split)" |
| 5 | Base times value | Readout | Burn time for shadows |
| 6 | Total exposure label | Text | "TOTAL EXPOSURE" |
| 7 | Total exposure value | Readout | Total of both exposures |
| 8 | Highlights button | Button | "HIGHLIGHTS" — applies highlight time to base |
| 9 | Shadows button | Button | "SHADOWS" — applies shadow time to base |
| 10 | Clear split data button | Button (danger) | Clears all split-grade data |
| 11 | Applied message | Text | "Click to apply time to BASE TIME • Use STOP ADJUST for dodge/burn" |

#### Base Time & Stop Controls

| # | Element | Type | Description |
|---|---------|------|-------------|
| 12 | Base time label | Text | "BASE TIME" |
| 13 | Base time value | Readout | Current base time (e.g., "10.0s") |
| 14 | Base time slider | Range | 0.4–50s, step 0.1 — adjusts base exposure time |
| 15 | Stop increment label | Text | "EXPOSURE STOP INCREMENT" |
| 16 | 1 stop button | Segmented | Selects full-stop increments |
| 17 | 1/2 stop button | Segmented | Selects half-stop increments |
| 18 | 1/3 stop button | Segmented (active) | Selects third-stop increments |
| 19 | 1/4 stop button | Segmented | Selects quarter-stop increments |
| 20 | 1/6 stop button | Segmented | Selects sixth-stop increments |
| 21 | Stop adjust label | Text | "STOP ADJUST" |
| 22 | Stop adjust value | Readout | Current offset (e.g., "0.0 stops") |
| 23 | Stop adjust slider | Range | −6 to +6, step 1 — dodge/burn stop adjustment |
| 24 | Stop ruler | Labels | Incremental stop values beneath slider |

#### Selected Exposure Display

| # | Element | Type | Description |
|---|---------|------|-------------|
| 25 | Selected exposure box | Container | Calculated exposure result |
| 26 | Selected exposure label | Text | "SELECTED EXPOSURE" |
| 27 | Selected exposure value | Readout (large) | Calculated time in seconds |
| 28 | Stop offset description | Text | Shows base offset (e.g., "BASE (0.0 stops)") |

#### Incremental Exposure Timer

| # | Element | Type | Description |
|---|---------|------|-------------|
| 29 | Timer status | Text | "READY FOR EXPOSURE" (updates during run) |
| 30 | Timer display | Readout (2.8rem) | Countdown in MM:SS or S.SS format |
| 31 | Notes label | Text | "Notes for this exposure" |
| 32 | Notes input | Text input | Accepts exposure notes |
| 33 | Start Exposure button | Button | Begins exposure countdown |
| 34 | Stop button | Button | Halts running timer (disabled until started) |
| 35 | Reset button | Button | Resets timer to zero |
| 36 | Repeat Last button | Button | Repeats previous exposure settings |
| 37 | Selected stop box | Readout | Current stop offset value |
| 38 | Previous total box | Readout | Cumulative time from prior exposures |
| 39 | Current total box | Readout | Total of all exposures including current |
| 40 | This exposure box | Readout | Time for current exposure only |
| 41 | Transfer to TIMER button | Button (primary) | "Transfer to TIMER Tab →" |

#### Enlarger & Contrast Calculator

| # | Element | Type | Description |
|---|---------|------|-------------|
| 42 | Calculator title | Text | "ENLARGER & CONTRAST CALCULATOR" |
| 43 | Original time box | Container | Reference time display |
| 44 | Original time label | Text | "Original Time (s)" |
| 45 | Original time value | Readout | Reference exposure time |
| 46 | Use Current button | Button | "Use Current Exposure Time" |

##### Head Height Adjustment (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 47 | Section header | Collapsible | "Head Height Adjustment" |
| 48 | Expand arrow | Icon | Expand/collapse indicator |
| 49 | Original height box | Container | Coarse + fine sliders |
| 50 | Original height label | Text | "Original Height (cm)" |
| 51 | Original height value | Readout | Height in cm |
| 52 | Coarse label | Text | "Coarse adjustment" |
| 53 | Coarse slider | Range | 10–60 cm, step 1 |
| 54 | Fine label | Text | "Fine adjustment (±0.5cm)" |
| 55 | Fine slider | Range | −5 to +5, step 1 |
| 56 | New height box | Container | New height sliders |
| 57 | New height label | Text | "New Height (cm)" |
| 58 | New height value | Readout | New height |
| 59 | New coarse label | Text | "Coarse adjustment" |
| 60 | New coarse slider | Range | 10–60 cm, step 1 |
| 61 | New fine label | Text | "Fine adjustment (±0.5cm)" |
| 62 | New fine slider | Range | −5 to +5, step 1 |

##### F-Stop Adjustment (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 63 | Section header | Collapsible | "F-Stop Adjustment" |
| 64 | Expand arrow | Icon | Expand/collapse |
| 65 | Original F-stop label | Text | "Original F-Stop" |
| 66 | Original F-stop select | Dropdown | f/2.8 to f/32 |
| 67 | New F-stop label | Text | "New F-Stop" |
| 68 | New F-stop select | Dropdown | f/2.8 to f/32 |

##### Paper Size Adjustment (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 69 | Section header | Collapsible | "Paper Size Adjustment" |
| 70 | Expand arrow | Icon | Expand/collapse |
| 71 | Original paper label | Text | "Original Paper Size" |
| 72 | Original paper select | Dropdown | 3.5×5" to 16×20" + Custom |
| 73 | Original custom container | Container | Appears for custom size |
| 74 | Original custom input | Number | Custom area in m² |
| 75 | Original custom Set button | Button | Applies custom area |
| 76 | New paper label | Text | "New Paper Size" |
| 77 | New paper select | Dropdown | 3.5×5" to 16×20" + Custom |
| 78 | New custom container | Container | Appears for custom size |
| 79 | New custom input | Number | Custom area in m² |
| 80 | New custom Set button | Button | Applies new custom area |

##### Contrast Filter Adjustment (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 81 | Section header | Collapsible | "Contrast Filter Adjustment" |
| 82 | Expand arrow | Icon | Expand/collapse |
| 83 | Paper brand label | Text | "PAPER BRAND" |
| 84 | Ilford button | Toggle (active) | Selects Ilford papers |
| 85 | FOMA button | Toggle | Selects FOMA papers |
| 86 | Paper type label | Text | "Paper Type" |
| 87 | Ilford paper select | Dropdown | 7 Ilford paper variants |
| 88 | FOMA paper select | Dropdown | 4 FOMA paper variants |
| 89 | ISO R label | Text | "ISO R" |
| 90 | ISO R value | Readout | Sensitivity rating |
| 91 | Contrast factor label | Text | "Contrast Factor" |
| 92 | Contrast factor value | Readout | Filter multiplier (e.g., "1.0×") |

##### Custom Factor Bank (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 93 | Section header | Collapsible | "Custom Factor Bank" |
| 94 | Expand arrow | Icon | Expand/collapse |
| 95 | Group select | Dropdown | Group A / B / C |
| 96 | Group name input | Text input | Custom label for group |
| 97 | Filter rows | Container | Input rows for each filter slot |

##### Factors & Adjusted Time

| # | Element | Type | Description |
|---|---------|------|-------------|
| 98 | Factors title | Text | "Factors & Time" |
| 99 | Height factor | Readout | Height multiplier (e.g., "1.00×") |
| 100 | F-stop factor | Readout | Aperture multiplier |
| 101 | Paper size factor | Readout | Paper area multiplier |
| 102 | Contrast factor | Readout | Filter factor |
| 103 | Custom factor | Readout | Custom bank multiplier |
| 104 | Combined factor | Readout (large) | Product of all factors |
| 105 | New adjusted time label | Text | "New Adjusted Time (s)" |
| 106 | New adjusted time value | Readout (large) | Final calculated time |
| 107 | Apply Adjusted Time button | Button | "Apply Adjusted Time as Base Time" |

---

### SPLIT GRADE Tab

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Neutral time label | Text | "NEUTRAL TIME" |
| 2 | Neutral time value | Readout | Current neutral exposure (e.g., "10.0s") |
| 3 | Neutral time slider | Range | 0.4–50s, step 0.1 |
| 4 | Paper brand label | Text | "PAPER BRAND" |
| 5 | Ilford button | Toggle (active) | Selects Ilford paper database |
| 6 | FOMA button | Toggle | Selects FOMA paper database |
| 7 | FOMA paper section | Container | Appears when FOMA selected |
| 8 | FOMA paper label | Text | "FOMA PAPER TYPE" |
| 9 | FOMA paper select | Dropdown | 4 FOMA paper variants |
| 10 | Ilford paper section | Container | Appears when Ilford selected |
| 11 | Ilford paper label | Text | "ILFORD PAPER TYPE" |
| 12 | Ilford paper select | Dropdown | 7 Ilford paper variants |
| 13 | Soft filter label | Text | "SOFT FILTER (Highlights)" |
| 14–20 | Soft filter buttons (00–5) | Segmented | 7 grade buttons for soft filter |
| 21 | Hard filter label | Text | "HARD FILTER (Shadows)" |
| 22–28 | Hard filter buttons (00–5) | Segmented | 7 grade buttons for hard filter |
| 29 | Shadow allocation label | Text | "SHADOW TIME ALLOCATION" |
| 30 | Shadow allocation value | Readout | Percentage (e.g., "50%") |
| 31 | Burn percent slider | Range | 0–100%, step 5 |
| 32 | Results box | Container | All split-grade calculations |
| 33 | Base times label | Text | "BASE TIMES (Before Filters)" |
| 34 | Base times value | Readout | Time before filter adjustment |
| 35 | Highlights label | Text | "HIGHLIGHTS (Soft + Factor)" |
| 36 | Highlights value | Readout (large) | Soft exposure time |
| 37 | Shadows label | Text | "SHADOWS (Hard + Factor)" |
| 38 | Shadows value | Readout (large) | Hard exposure time |
| 39 | Total exposure label | Text | "TOTAL EXPOSURE" |
| 40 | Total exposure value | Readout (large) | Sum of soft + hard |
| 41 | Split ratio label | Text | "SPLIT RATIO" |
| 42 | Split ratio value | Readout | Ratio between soft and hard |
| 43 | Contrast grade label | Text | "EFFECTIVE CONTRAST GRADE" |
| 44 | Contrast grade value | Readout | Computed grade equivalent |
| 45 | Send to EXPOSURE button | Button (primary) | Transfers times to EXPOSURE tab |
| 46 | Presets header | Collapsible | "SPLIT-GRADE PRESETS" |
| 47 | Expand arrow | Icon | Expand/collapse |
| 48 | Preset name input | Text input | Max 20 chars |
| 49 | Save preset button | Button | "Save Current as Preset" |
| 50 | Presets list | List | Saved split-grade presets |
| 51 | Clear All button | Button (danger) | Removes all presets |

---

### TEST STRIP Tab

#### Configuration Section

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Base time label | Text | "BASE TIME" |
| 2 | Base time value | Readout | (e.g., "10.0s") |
| 3 | Base time slider | Range | 1–50s, step 0.5 |
| 4 | Increment label | Text | "EXPOSURE STOP INCREMENT" |
| 5 | 1 stop button | Segmented | Full-stop increments |
| 6 | 1/2 stop button | Segmented | Half-stop |
| 7 | 1/3 stop button | Segmented (active) | Third-stop |
| 8 | 1/4 stop button | Segmented | Quarter-stop |
| 9 | 1/6 stop button | Segmented | Sixth-stop |
| 10 | Increment slider label | Text | "INCREMENT (in stops)" |
| 11 | Increment slider value | Readout | (e.g., "⅓ stop") |
| 12 | Increment slider | Range | 1–9 increments, step 1 |
| 13 | Increment ruler | Labels | Visual ruler beneath slider |
| 14 | Steps label | Text | "NUMBER OF STEPS" |
| 15 | Steps value | Readout | (e.g., "6") |
| 16 | Steps slider | Range | 3–12, step 1 |
| 17 | Method label | Text | "METHOD" |
| 18 | Method value | Readout | (e.g., "Cumulative") |
| 19 | Cumulative button | Toggle (active) | Cumulative method |
| 20 | Incremental button | Toggle | Incremental method |
| 21 | Auto advance label | Text | "AUTO ADVANCE" |
| 22 | Auto advance value | Readout | (e.g., "OFF") |
| 23 | Auto advance switch | Toggle | Enables auto-progression |
| 24 | Auto advance note | Text | "Pause after each step" / "Auto-advance enabled" |

#### Sequence Info & Instructions

| # | Element | Type | Description |
|---|---------|------|-------------|
| 25 | Sequence info box | Container | Test configuration summary |
| 26 | Sequence label | Text | "TEST STRIP SEQUENCE" |
| 27 | Sequence value | Readout | (e.g., "6 steps × ⅓ stop") |
| 28 | Time range | Text | Min/max exposure times |
| 29 | Instructions title | Text | "INSTRUCTIONS" |
| 30 | Cumulative instructions | Text | Method-specific instructions |
| 31 | Incremental instructions | Text | Method-specific instructions |
| 32 | Auto advance status | Text | "Current: Manual Advance" / auto |

#### Preview & Transfer

| # | Element | Type | Description |
|---|---------|------|-------------|
| 33 | Preview title | Text | "TEST STRIP LAYOUT" |
| 34 | Preview container | Grid | Visual test strip representation |
| 35 | Step elements (×12 max) | Colored boxes | Each step with time/f-stop info |
| 36 | Active step highlight | Visual | Current step highlighted |
| 37 | Show times toggle | Checkbox | Toggles time/f-stop display |
| 38 | Show times label | Text | "Show Times" |
| 39 | Transfer instruction | Text | "Click test steps to apply time to:" |
| 40 | Transfer label | Text | "TRANSFER DESTINATION" |
| 41 | → EXPOSURE button | Segmented | Sends to EXPOSURE tab |
| 42 | → SPLIT GRADE button | Segmented | Sends to SPLIT GRADE tab |

#### Timer & Controls

| # | Element | Type | Description |
|---|---------|------|-------------|
| 43 | Timer status | Text | "READY FOR TEST STRIP" |
| 44 | Current step label | Text | "Current Step" |
| 45 | Current step value | Readout | (e.g., "1/6") |
| 46 | Timer display | Readout (2.8rem) | Countdown timer |
| 47 | Time label | Text | "Time" |
| 48 | Time value | Readout | Current step time |
| 49 | Progress bar container | Bar | Visual progress |
| 50 | Progress fill | Bar (animated) | Fills during exposure |
| 51 | Progress label start | Text | Min time |
| 52 | Progress label mid | Text | Mid time |
| 53 | Progress label end | Text | Max time |
| 54 | Start button | Button | Begins test strip exposure |
| 55 | Stop button | Button | Halts timer (disabled until started) |
| 56 | Reset button | Button | Resets to ready state |
| 57 | Notes label | Text | "Notes for this test strip" |
| 58 | Notes input | Text input | Test strip notes |
| 59 | Step size box | Readout | Step increment value |
| 60 | Current stop box | Readout | Current stop offset |
| 61 | Time multiplier box | Readout | Multiplier value |
| 62 | Total time box | Readout | Total sequence time |

#### Profiles (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 63 | Profiles header | Collapsible | "TEST STRIP PROFILES" |
| 64 | Expand arrow | Icon | Expand/collapse |
| 65 | Profile name input | Text input | Max 20 chars |
| 66 | Save button | Button | "Save Current as Profile" |
| 67 | Profiles list | List | Saved test strip profiles |
| 68 | Clear All button | Button (danger) | Removes all profiles |

---

### TIMER Tab

#### Timer Grid (2×2)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Developer box | Container | Top-left timer cell |
| 2 | Developer title | Text | "Developer" |
| 3 | Developer time | Readout (1.6rem) | MM:SS countdown |
| 4 | Developer elapsed | Text (tiny) | Elapsed time since start |
| 5 | Developer −1s button | Button | Decrements 1 second |
| 6 | Developer +1s button | Button | Increments 1 second |
| 7 | Developer Start button | Button | Starts developer timer |
| 8 | Developer Reset button | Button | Resets timer (disabled until used) |
| 9 | Stop Bath box | Container | Top-right timer cell |
| 10 | Stop Bath title | Text | "Stop Bath" |
| 11 | Stop Bath time | Readout | MM:SS countdown |
| 12 | Stop Bath elapsed | Text (tiny) | Elapsed time |
| 13 | Stop Bath −1s button | Button | Decrements 1 second |
| 14 | Stop Bath +1s button | Button | Increments 1 second |
| 15 | Stop Bath Start button | Button | Starts stop bath timer |
| 16 | Stop Bath Reset button | Button | Resets timer |
| 17 | Fixer box | Container | Bottom-left timer cell |
| 18 | Fixer title | Text | "Fixer" |
| 19 | Fixer time | Readout | MM:SS countdown |
| 20 | Fixer elapsed | Text (tiny) | Elapsed time |
| 21 | Fixer −1s button | Button | Decrements 1 second |
| 22 | Fixer +1s button | Button | Increments 1 second |
| 23 | Fixer Start button | Button | Starts fixer timer |
| 24 | Fixer Reset button | Button | Resets timer |
| 25 | Photo Wash box | Container | Bottom-right timer cell |
| 26 | Photo Wash title | Text | "Photo Wash" |
| 27 | Photo Wash time | Readout | MM:SS countdown |
| 28 | Photo Wash elapsed | Text (tiny) | Elapsed time |
| 29 | Photo Wash −1s button | Button | Decrements 1 second |
| 30 | Photo Wash +1s button | Button | Increments 1 second |
| 31 | Photo Wash Start button | Button | Starts wash timer |
| 32 | Photo Wash Reset button | Button | Resets timer |

#### Global Timer Controls

| # | Element | Type | Description |
|---|---------|------|-------------|
| 33 | Start All button | Button | Begins auto-chain (Dev → Stop → Fix → Wash) |
| 34 | Reset All button | Button | Resets all four timers |

#### Factorial Development (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 35 | Section header | Collapsible | "FACTORIAL DEVELOPMENT" |
| 36 | Expand arrow | Icon | Expand/collapse |
| 37 | Current multiplier label | Text | "CURRENT MULTIPLIER" |
| 38 | Multiplier value | Readout | Multiplier result (or "Not Set") |
| 39 | Status text | Text | "Set Dev time and start first print" |
| 40 | Mark Baseline button | Button | "MARK BASELINE" — records first black point |
| 41 | Black Point button | Button | "BLACK POINT" — records subsequent readings |
| 42 | Reset Multiplier button | Button | Clears factorial data |
| 43 | Instructions | Text | Multi-line workflow guide |

#### Timer Profiles (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 44 | Profiles header | Collapsible | "TIMER PROFILES" |
| 45 | Expand arrow | Icon | Expand/collapse |
| 46 | Profile name input | Text input | Max 20 chars |
| 47 | Save button | Button | "Save Current as Profile" |
| 48 | Profiles list | List | Saved timer profiles |
| 49 | Clear All button | Button (danger) | Removes all profiles |

---

### CHEMICAL Tab

#### Developer Capacity Tracker (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Section header | Collapsible | "DEVELOPER CAPACITY TRACKER" |
| 2 | Expand arrow | Icon | Expand/collapse |
| 3 | Bottle spec label | Text | "BOTTLE SPEC (m²/L concentrate)" |
| 4 | Bottle spec value | Readout | (e.g., "5.0") |
| 5 | Bottle spec slider | Range | 0.5–30, step 0.5 |
| 6 | Dilution label | Text | "DILUTION" |
| 7 | Dilution value | Readout | (e.g., "1+9") |
| 8 | 1+4 button | Toggle | Dilution preset |
| 9 | 1+9 button | Toggle (active) | Default dilution |
| 10 | 1+14 button | Toggle | Dilution preset |
| 11 | 1+19 button | Toggle | Dilution preset |
| 12 | 1+29 button | Toggle | Dilution preset |
| 13 | 1+39 button | Toggle | Dilution preset |
| 14 | Custom stock input | Number | Custom stock parts (1–99) |
| 15 | Custom water input | Number | Custom water parts (1–99) |
| 16 | Working capacity label | Text | "WORKING CAPACITY" |
| 17 | Working capacity value | Readout (large) | (e.g., "0.50 m²/L") |
| 18 | Tray volume label | Text | "TRAY VOLUME (ml)" |
| 19 | Tray volume value | Readout | (e.g., "1000") |
| 20 | Tray volume slider | Range | 100–5000, step 100 |
| 21 | Paper 3.5×5" button | Toggle | Paper size |
| 22 | Paper 4×5" button | Toggle (active) | Default paper size |
| 23 | Paper 5×7" button | Toggle | Paper size |
| 24 | Paper 8×10" button | Toggle | Paper size |
| 25 | Paper 11×14" button | Toggle | Paper size |
| 26 | Paper 16×20" button | Toggle | Paper size |
| 27 | Custom area input | Number | Custom area in m² |
| 28 | Use Custom button | Toggle | Applies custom area |
| 29 | Max prints label | Text | "MAX PRINTS THIS BATCH" |
| 30 | Max prints value | Readout (large) | Calculated maximum prints |
| 31 | Remaining text | Text | "X prints remaining (Y m²)" |
| 32 | Progress bar | Bar | Capacity usage visualization |
| 33 | Progress labels | Text | "0", mid, max values |
| 34 | +1 Print button | Button | Increments print counter |
| 35 | +5 Prints button | Button | Adds 5 to counter |
| 36 | Reset button | Button | Clears usage counter |
| 37 | Prints done box | Readout | Number processed |
| 38 | Area used box | Readout | Total area exposed |
| 39 | Percent used box | Readout | Usage percentage |
| 40 | Status box | Readout | "Fresh" / "Caution" / "Depleted" |

#### Shelf Life Tracker (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 41 | Section header | Collapsible | "SHELF LIFE TRACKER" |
| 42 | Expand arrow | Icon | Expand/collapse |
| 43 | Chemical type label | Text | "Chemical" |
| 44 | Chemical type select | Dropdown | Developer, Stop Bath, Fixer, Hypo Clear, Photo Wash, Custom |
| 45 | Custom name label | Text | "Custom Name" (hidden unless Custom selected) |
| 46 | Custom name input | Text input | Custom chemical name |
| 47 | Shelf life days label | Text | "Shelf Life (days)" |
| 48 | Shelf life days input | Number | 1–365, default 30 |
| 49 | Date mixed label | Text | "Date Mixed/Opened" |
| 50 | Date input | Date picker | Calendar date selection |
| 51 | Add Chemical button | Button | Saves entry |
| 52 | Active chemicals title | Text | "ACTIVE CHEMICALS" |
| 53 | Chemical list | List | Saved chemicals with status colors |
| 54 | Clear Expired button | Button | Removes expired items |
| 55 | Help text | Text | "Red items expired, orange expire in 3 days" |

#### Chemical Mix Calculator (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 56 | Section header | Collapsible | "CHEMICAL MIX CALCULATOR" |
| 57 | Expand arrow | Icon | Expand/collapse |
| 58 | Total volume label | Text | "TOTAL VOLUME" |
| 59 | Total volume value | Readout | (e.g., "1000ml") |
| 60 | Total volume slider | Range | 100–5000, step 50 |
| 61 | Dilution ratio title | Text | "DILUTION RATIO" |
| 62 | 1+9 button | Toggle (active) | "1+9 (1:10)" |
| 63 | 1+14 button | Toggle | "1+14 (1:15)" |
| 64 | 1+19 button | Toggle | "1+19 (1:20)" |
| 65 | 1+24 button | Toggle | "1+24 (1:25)" |
| 66 | 1+29 button | Toggle | "1+29 (1:30)" |
| 67 | 1+39 button | Toggle | "1+39 (1:40)" |
| 68 | Custom ratio title | Text | "OR CUSTOM RATIO" |
| 69 | Custom stock input | Number | Stock concentrate parts |
| 70 | Custom water input | Number | Water parts |
| 71 | Mixing instructions panel | Container | Results display |
| 72 | Stock volume label | Text | "STOCK SOLUTION" |
| 73 | Stock volume value | Readout | (e.g., "100ml") |
| 74 | Water label | Text | "WATER" |
| 75 | Water volume value | Readout | (e.g., "900ml") |
| 76 | Mixing note | Text | "Add stock to water, not water to stock" |

#### Chemical Mix Presets (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 77 | Section header | Collapsible | "CHEMICAL MIX PRESETS" |
| 78 | Expand arrow | Icon | Expand/collapse |
| 79 | Preset name input | Text input | Max 20 chars |
| 80 | Save button | Button | "Save Current as Preset" |
| 81 | Presets list | List | Saved chemical mix presets |
| 82 | Clear All button | Button (danger) | Removes all presets |

---

### CONTROLLER Tab

#### Relay Control

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Section title | Text | "Relay Control (Manual)" |
| 2 | Relay 1 label | Text | "Relay 1 (GP14)" |
| 3 | Relay 1 name input | Text input | Custom name (default "Enlarger") |
| 4 | Relay 1 state label | Text | "State" |
| 5 | Relay 1 toggle | Button | ON/OFF toggle (default OFF) |
| 6 | Relay 2 label | Text | "Relay 2 (GP15)" |
| 7 | Relay 2 name input | Text input | Custom name (default "Safelight") |
| 8 | Relay 2 state label | Text | "State" |
| 9 | Relay 2 toggle | Button | ON/OFF toggle |
| 10 | Relay 3 label | Text | "Relay 3 (GP16)" |
| 11 | Relay 3 name input | Text input | Custom name (default "Heater") |
| 12 | Relay 3 state label | Text | "State" |
| 13 | Relay 3 toggle | Button | ON/OFF toggle |
| 14 | Relay 4 label | Text | "Relay 4 (GP17)" |
| 15 | Relay 4 name input | Text input | Custom name (default "White Light") |
| 16 | Relay 4 state label | Text | "State" |
| 17 | Relay 4 toggle | Button | ON/OFF toggle |
| 18 | All ON button | Button | Turns on all relays |
| 19 | All OFF button | Button | Turns off all relays |

#### Temperature Control

| # | Element | Type | Description |
|---|---------|------|-------------|
| 20 | Section title | Text | "Temperature Control" |
| 21 | Enable label | Text | "Enable Temperature Control" |
| 22 | Enable toggle | Checkbox | Enables/disables temperature management |
| 23 | Current temp label | Text | "Current Temperature" |
| 24 | Current temp display | Readout (1.8em) | Temperature in °C |
| 25 | Temperature status | Text | "Disabled" / "Active" / "Heating" etc. |
| 26 | Target temp label | Text | "Target (°C)" |
| 27 | Target temp input | Number | 15–50, step 0.5 |
| 28 | Set Target button | Button (primary) | "Set Target" applies temperature |
| 29 | Heating status label | Text | "Heating (GP16)" |
| 30 | Heating status value | Readout | ON/OFF state |
| 31 | Dead zone label | Text | "Dead Zone" |
| 32 | Dead zone value | Readout | (e.g., "±0.5°C") |
| 33 | History label | Text | "Temperature History (15 min)" |
| 34 | Temperature chart | Canvas | 15-minute temperature history graph |
| 35 | Data points text | Text | "0 readings" — number of data points collected |
| 36 | Sensor disconnect warning | Alert box | "⚠️ Sensor Disconnected - Relay OFF" (hidden normally) |

---

### LOGS Tab

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Section title | Text | "LOGS" |
| 2 | Instruction text | Text | "Automatically tracks your printing sessions…" |
| 3 | Statistics label | Text | "SESSION STATISTICS" |
| 4 | Statistics display | Readout | Session count and summary |
| 5 | Temporary sessions title | Text | "TEMPORARY SESSIONS (Auto-saved)" |
| 6 | Temporary sessions list | List | Lists temporary sessions (max 6) |
| 7 | Temporary placeholder | Text | "No temporary sessions yet" |
| 8 | Permanent sessions title | Text | "PERMANENT SESSIONS" |
| 9 | Permanent sessions list | List | Lists permanently saved sessions |
| 10 | Permanent placeholder | Text | "No permanent sessions saved" |
| 11 | Export CSV button | Button | Downloads CSV file |
| 12 | Export JSON button | Button | Downloads JSON file |
| 13 | Import JSON button | Button | Uploads JSON session data |
| 14 | Clear All Logs button | Button (danger) | Removes all sessions |

---

### METERING Tab

#### Mode Selection

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Meter mode label | Text | "METER MODE" |
| 2 | Mode value | Readout | Current mode name |
| 3 | Exposure button | Segmented (active) | "Exposure" mode |
| 4 | Contrast button | Segmented | "Contrast" mode |
| 5 | Split button | Segmented | "Split-Grade" mode |
| 6 | Proof button | Segmented | "Virtual Proof" mode |

#### Paper & Filter Setup (collapsible, expanded by default)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 7 | Section header | Collapsible | "PAPER & FILTER SETUP" |
| 8 | Expand arrow | Icon | Expand/collapse |
| 9 | Paper brand label | Text | "PAPER BRAND" |
| 10 | Ilford button | Toggle (active) | Selects Ilford papers |
| 11 | FOMA button | Toggle | Selects FOMA papers |
| 12 | Ilford paper select | Dropdown | Ilford paper types |
| 13 | FOMA paper select | Dropdown | FOMA paper types (hidden by default) |
| 14 | Current paper label | Text | "CALIBRATION FOR CURRENT PAPER" |
| 15 | Paper name | Text (colored) | Selected paper name |
| 16 | Calibration value | Readout | Calibration constant (e.g., "1000 lux·s") |
| 17 | Calibration note | Text (tiny) | "Auto-saved per paper type" |

#### Exposure Meter Mode

| # | Element | Type | Description |
|---|---------|------|-------------|
| 18 | Mode title | Text | "EXPOSURE METER" |
| 19 | Instruction | Text | "Place sensor on baseboard under enlarger light" |
| 20 | Sensor status label | Text | "SENSOR STATUS" |
| 21 | Sensor status value | Readout | Connection state |
| 22 | Averaging label | Text | "AVERAGING SAMPLES" |
| 23 | Averaging value | Readout | (e.g., "5") |
| 24 | Averaging slider | Range | 1–10, step 1 |
| 25 | Measure Lux button | Button | "MEASURE LUX" |
| 26 | Lux reading label | Text | "LUX READING" |
| 27 | Lux reading value | Readout | Measured lux |
| 28 | Variance label | Text | "VARIANCE" |
| 29 | Variance value | Readout | Standard deviation |
| 30 | Exposure time label | Text | "CALCULATED EXPOSURE TIME" |
| 31 | Exposure time display | Readout (2.5rem) | Final exposure time |
| 32 | Filter grade label | Text | "FILTER GRADE (optional)" |
| 33 | Filter grade select | Dropdown | None, 00–5 |
| 34 | Send to EXPOSURE button | Button (primary) | "→ Send to EXPOSURE" |

#### Contrast Analyzer Mode (hidden by default)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 35 | Mode title | Text | "CONTRAST ANALYZER" |
| 36 | Instruction | Text | "Measure highlight and shadow areas…" |
| 37 | Averaging label | Text | "AVERAGING SAMPLES" |
| 38 | Averaging value | Readout | Sample count |
| 39 | Averaging slider | Range | 1–10, step 1 |
| 40 | Highlight label | Text | "HIGHLIGHT (brightest area)" |
| 41 | Highlight lux value | Readout | Measured lux |
| 42 | Measure Highlight button | Button | Captures highlight reading |
| 43 | Shadow label | Text | "SHADOW (darkest area)" |
| 44 | Shadow lux value | Readout | Measured lux |
| 45 | Measure Shadow button | Button | Captures shadow reading |
| 46 | Delta EV label | Text | "CONTRAST RANGE (ΔEV)" |
| 47 | Delta EV display | Readout (2.5rem) | Contrast range |
| 48 | Delta EV note | Text | "Higher ΔEV = higher contrast negative" |
| 49 | Recommended grade label | Text | "RECOMMENDED GRADE" |
| 50 | Recommended grade value | Readout (1.8rem) | Computed grade |
| 51 | Match quality label | Text | "MATCH QUALITY" |
| 52 | Match quality value | Readout | Quality assessment |
| 53 | Analysis reasoning label | Text (accent) | "ANALYSIS REASONING" |
| 54 | Analysis reasoning text | Text (multi-line) | Explanation |
| 55 | Suggested time label | Text | "SUGGESTED EXPOSURE TIME" |
| 56 | Midpoint time label | Text | "Midpoint Time:" |
| 57 | Midpoint time value | Readout (bold) | Calculated base time |
| 58 | Midpoint lux label | Text | "Midpoint Lux:" |
| 59 | Midpoint lux value | Readout (bold) | Light level at midpoint |
| 60 | Exposure note | Text (italic) | Additional notes |
| 61 | Analyze Contrast button | Button | Runs calculation |
| 62 | Send to EXPOSURE button | Button | "Send Suggested Time to EXPOSURE" |
| 63 | Clear Readings button | Button | Resets measurements |

#### Split-Grade Analyzer Mode (hidden by default)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 64 | Mode title | Text | "SPLIT-GRADE ANALYZER" |
| 65 | Instruction | Text | "Calculate absolute exposure times for split-grade printing" |
| 66 | Averaging label | Text | "AVERAGING SAMPLES" |
| 67 | Averaging value | Readout | Sample count |
| 68 | Averaging slider | Range | 1–10, step 1 |
| 69 | Highlight label | Text | "HIGHLIGHT AREA" |
| 70 | Highlight lux value | Readout | Measured lux |
| 71 | Measure Highlight button | Button | Captures highlight |
| 72 | Shadow label | Text | "SHADOW AREA" |
| 73 | Shadow lux value | Readout | Measured lux |
| 74 | Measure Shadow button | Button | Captures shadow |
| 75 | Delta EV label | Text | "CONTRAST RANGE (ΔEV)" |
| 76 | Delta EV display | Readout (2rem) | Contrast range |
| 77 | Match quality display | Text | "Match Quality: --" |
| 78 | Match note | Text | Notes about quality |
| 79 | Printable EV label | Text | "Printable EV:" |
| 80 | Printable EV value | Readout (bold) | Paper EV range |
| 81 | Gamma label | Text | "Gamma (Tone Curve):" |
| 82 | Gamma value | Readout (bold) | Paper gamma |
| 83 | Contrast index label | Text | "Contrast Index:" |
| 84 | Contrast index value | Readout (bold) | Contrast index |
| 85 | Density range label | Text | "Density Range:" |
| 86 | Density range value | Readout | "-- (Dmin-Dmax)" |
| 87 | Analysis reasoning label | Text (accent) | "ANALYSIS REASONING" |
| 88 | Analysis reasoning text | Text (multi-line) | Explanation |
| 89 | Soft exposure label | Text (colored) | "SOFT EXPOSURE" |
| 90 | Soft time display | Readout (1.8rem) | Soft exposure time |
| 91 | Soft filter name | Readout | Filter grade |
| 92 | Soft percent | Readout | Percentage of total |
| 93 | Hard exposure label | Text (colored) | "HARD EXPOSURE" |
| 94 | Hard time display | Readout (1.8rem) | Hard exposure time |
| 95 | Hard filter name | Readout | Filter grade |
| 96 | Hard percent | Readout | Percentage of total |
| 97 | Send Both to EXPOSURE button | Button | "→ Send Both to EXPOSURE" |
| 98 | Total exposure label | Text | "TOTAL EXPOSURE TIME" |
| 99 | Total exposure display | Readout (2.2rem) | Total time |
| 100 | How-to label | Text (accent) | "HOW TO USE" |
| 101 | How-to instructions | Text (multi-line) | Step-by-step workflow |
| 102 | Calculate Split-Grade button | Button | Runs split-grade calculation |
| 103 | Clear Readings button | Button | Resets measurements |

#### Virtual Proof Mode (hidden by default)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 104 | Mode title | Text | "VIRTUAL PROOF" |
| 105 | Instruction | Text | "Sequential scan to rebuild grayscale preview" |
| 106 | Grid size label | Text | "GRID SIZE" |
| 107 | Grid total value | Readout | Total cells |
| 108 | Width input | Number | 1–50, step 1, default 30 |
| 109 | Height input | Number | 1–50, step 1, default 20 |
| 110 | Apply Grid button | Button | Creates/resizes grid |
| 111 | Averaging label | Text | "AVERAGING SAMPLES" |
| 112 | Averaging value | Readout | Sample count |
| 113 | Averaging slider | Range | 1–10, step 1 |
| 114 | Filter label | Text | "PREVIEW FILTER GRADE" |
| 115 | Filter select | Dropdown | Grade for preview |
| 116 | Scan progress label | Text | "SCAN PROGRESS" |
| 117 | Scan progress value | Readout | "0/600" etc. |
| 118 | Scan status | Text | "Idle" / "Scanning" |
| 119 | Measure Next Cell button | Button | Captures next cell |
| 120 | Set Zone V Reference button | Button | Sets Zone V baseline |
| 121 | Recompute Preview button | Button | Recalculates grid view |
| 122 | Clear Grid button | Button | Resets all cells |
| 123 | Last sample label | Text | "LAST SAMPLE" |
| 124 | Last lux | Text | "Lux: --" |
| 125 | Last zone | Text | "Zone: --" |
| 126 | Last ISO R | Text | "ISO R: --" |
| 127 | Last EV range | Text | "EV Range: --" |
| 128 | Last density | Text | "Density: --" |
| 129 | Last exposure | Text | "Exposure: --" |
| 130 | Last clipping | Text | "Clipping: --" |
| 131 | Virtual proof label | Text | "VIRTUAL PROOF" |
| 132 | Proof grid | Grid | Matrix of proof cells |
| 133 | Proof cells | Colored boxes | Individual cell elements (up to 2500) |
| 134 | Legend | Labels | "Dark → Light" grayscale legend |
| 135 | Histogram label | Text | "HISTOGRAM" |
| 136 | Histogram canvas | Canvas | Histogram visualization |

#### Calibration (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 137 | Section header | Collapsible | "CALIBRATION" |
| 138 | Expand arrow | Icon | Expand/collapse |
| 139 | Procedure title | Text | "CALIBRATION PROCEDURE" |
| 140 | Instructions | Text (6-line) | Step-by-step calibration guide |
| 141 | Constant label | Text | "CALIBRATION CONSTANT (lux·s)" |
| 142 | Constant input | Number | 1–100000, step 1, default 1000 |
| 143 | Quick calc title | Text | "QUICK CALIBRATION CALCULATOR" |
| 144 | Measured lux label | Text | "Measured Lux" |
| 145 | Measured lux input | Number | Light measurement entry |
| 146 | Correct time label | Text | "Correct Time (s)" |
| 147 | Correct time input | Number | Known correct time |
| 148 | Calculate & Apply button | Button | Computes and applies calibration |
| 149 | Save Calibration button | Button (primary) | Saves calibration |

#### Sensor Information (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 150 | Section header | Collapsible | "SENSOR INFORMATION" |
| 151 | Expand arrow | Icon | Expand/collapse |
| 152 | Sensor type label | Text | "SENSOR TYPE" |
| 153 | Sensor type value | Readout | "TSL2591X" |
| 154 | Connection label | Text | "CONNECTION" |
| 155 | Connection value | Readout | "I²C" |
| 156 | Current gain label | Text | "CURRENT GAIN" |
| 157 | Gain value | Readout | (e.g., "MED (25×)") |
| 158 | Integration label | Text | "INTEGRATION" |
| 159 | Integration value | Readout | (e.g., "300ms") |
| 160 | Gain control label | Text | "SENSOR GAIN" |
| 161 | Gain select | Dropdown | Auto, Low 1×, Med 25×, High 428×, Max 9876× |
| 162 | Integration time label | Text | "INTEGRATION TIME" |
| 163 | Integration select | Dropdown | 100ms to 600ms options |
| 164 | Apply Sensor Settings button | Button | Applies gain/integration |
| 165 | Refresh Status button | Button | Refreshes sensor info |

---

### SETTINGS Tab

#### Display Settings

| # | Element | Type | Description |
|---|---------|------|-------------|
| 1 | Toggle Fullscreen button | Button (primary) | Enters/exits fullscreen mode |
| 2 | Color scheme title | Text | "Color Scheme" |
| 3 | Darkroom button | Toggle (active) | "Darkroom (Default)" red/black theme |
| 4 | Light button | Toggle | "Light" bright theme |
| 5 | Night button | Toggle | "Night" neutral dark theme |

#### Global Settings (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 6 | Section header | Collapsible | "GLOBAL SETTINGS" |
| 7 | Expand arrow | Icon | Expand/collapse |
| 8 | Base time label | Text | "Default Base Time (s)" |
| 9 | Base time input | Number | 1–50, step 0.5, default 10 |
| 10 | Stop increment label | Text | "Default Stop Increment" |
| 11 | Stop increment select | Dropdown | 1, 1/2, 1/3, 1/4, 1/6 (default 1/3) |
| 12 | Countdown delay label | Text | "Countdown Delay (s)" |
| 13 | Countdown delay input | Number | 0–30, step 1, default 5 |
| 14 | Countdown beep label | Text | "Countdown Beep" |
| 15 | Countdown beep toggle | Checkbox (checked) | Enables countdown audio |
| 16 | Beep pattern label | Text | "Beep Pattern" |
| 17 | Beep pattern select | Dropdown | every-second, last3, last5, none |
| 18 | Test Beep button | Button | Plays sample sound |

#### Metering Settings (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 19 | Section header | Collapsible | "METERING SETTINGS" |
| 20 | Expand arrow | Icon | Expand/collapse |
| 21 | Proof stability title | Text | "Virtual Proof Stability" |
| 22 | Stability detection label | Text | "Stability Detection" |
| 23 | Stability detection toggle | Checkbox | Enables stability algorithm |
| 24 | Beep on stable label | Text | "Beep On Stable" |
| 25 | Beep on stable toggle | Checkbox | Audio on stable reading |
| 26 | Tolerance label | Text | "Tolerance (%)" |
| 27 | Tolerance input | Number | 0.5–10, step 0.1, default 2.5 |
| 28 | Min stable reads label | Text | "Min Stable Reads" |
| 29 | Min stable reads input | Number | 1–5, default 2 |
| 30 | Max wait label | Text | "Max Wait (ms)" |
| 31 | Max wait input | Number | 300–3000, step 50, default 900 |
| 32 | Min delta label | Text | "Min Delta (lux)" |
| 33 | Min delta input | Number | 0.05–5, step 0.05, default 0.2 |

#### Test Strip Settings (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 34 | Section header | Collapsible | "TEST STRIP SETTINGS" |
| 35 | Expand arrow | Icon | Expand/collapse |
| 36 | Auto advance label | Text | "Auto Advance" |
| 37 | Auto advance toggle | Checkbox | Enables auto-progression |
| 38 | Advance delay label | Text | "Auto Advance Delay (s)" |
| 39 | Advance delay input | Number | 0–30, step 1, default 1 |
| 40 | Base time min label | Text | "Test Base Time Min (s)" |
| 41 | Base time min input | Number | 0.5–10, step 0.5, default 1 |
| 42 | Base time max label | Text | "Test Base Time Max (s)" |
| 43 | Base time max input | Number | 10–300, step 1, default 50 |

#### Exposure Settings (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 44 | Section header | Collapsible | "EXPOSURE SETTINGS" |
| 45 | Expand arrow | Icon | Expand/collapse |
| 46 | Base time min label | Text | "Base Time Min (s)" |
| 47 | Base time min input | Number | 0.1–10, step 0.1, default 0.4 |
| 48 | Base time max label | Text | "Base Time Max (s)" |
| 49 | Base time max input | Number | 10–300, step 1, default 50 |
| 50 | Warning beep label | Text | "Exposure 3s Beep" |
| 51 | Warning beep toggle | Checkbox (checked) | Beep at 3 seconds remaining |
| 52 | End beep label | Text | "Exposure End Beep" |
| 53 | End beep toggle | Checkbox (checked) | Beep on completion |

#### Timer Settings (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 54 | Section header | Collapsible | "TIMER SETTINGS" |
| 55 | Expand arrow | Icon | Expand/collapse |
| 56 | Dev time label | Text | "Default Developer (s)" |
| 57 | Dev time input | Number | 5–600, step 5, default 60 |
| 58 | Stop time label | Text | "Default Stop Bath (s)" |
| 59 | Stop time input | Number | 5–300, step 5, default 30 |
| 60 | Fix time label | Text | "Default Fixer (s)" |
| 61 | Fix time input | Number | 5–600, step 5, default 60 |
| 62 | Flo time label | Text | "Default Photo Wash (s)" |
| 63 | Flo time input | Number | 5–300, step 5, default 30 |
| 64 | Timer warning label | Text | "Timer 10s Beep" |
| 65 | Timer warning toggle | Checkbox (checked) | Beep at 10 seconds remaining |
| 66 | Timer end label | Text | "Timer End Beep" |
| 67 | Timer end toggle | Checkbox (checked) | Beep on completion |

#### Controller Settings (collapsible)

| # | Element | Type | Description |
|---|---------|------|-------------|
| 68 | Section header | Collapsible | "CONTROLLER SETTINGS" |
| 69 | Expand arrow | Icon | Expand/collapse |
| 70 | Auto control subtitle | Text | "Auto - Manual Enlarger Control" |
| 71 | Auto-trigger label | Text | "Auto-trigger Enlarger" |
| 72 | Auto-trigger toggle | Checkbox (checked) | Enlarger relay during timers |
| 73 | Auto safelight label | Text | "Auto Safelight Control" |
| 74 | Auto safelight toggle | Checkbox (checked) | Safelight off during exposure |
| 75 | Auto control note | Text | Help text about behavior |
| 76 | Manager subtitle | Text | "Controller Manager" |
| 77 | Server IP label | Text | "Server IP (auto-detected)" |
| 78 | Server IP input | Text (readonly) | Auto-detected address |
| 79 | Server port label | Text | "Server Port" |
| 80 | Server port input | Number (readonly) | Default 80 |
| 81 | Test Connection label | Text | "Test Connection" |
| 82 | Test button | Button | Validates server connection |
| 83 | Status label | Text | "Status" |
| 84 | Status display | Text | "Not connected" etc. |
| 85 | Test Timer label | Text | "Test Timer Relay" |
| 86 | Timer seconds input | Number | 0.1–60, step 0.1, default 5 |
| 87 | Timer test button | Button | Triggers relay for set duration |
| 88 | WiFi subtitle | Text | "WiFi Configuration" |
| 89 | WiFi help text | Text | "Connect to WiFi router for mDNS…" |
| 90 | SSID label | Text | "WiFi SSID" |
| 91 | SSID input | Text input | Network name |
| 92 | Password label | Text | "WiFi Password" |
| 93 | Password input | Password | Network password |
| 94 | Connect to WiFi button | Button (primary) | Connects to network |
| 95 | WiFi status label | Text | "WiFi Status" |
| 96 | WiFi status display | Text | "AP Mode (192.168.4.1)" |
| 97 | Force Hotspot button | Button | Reactivates access point |
| 98 | Clear WiFi button | Button | Removes saved credentials |
| 99 | WiFi note | Text | "After connecting, access via darkroom.local" |
| 100 | Updates subtitle | Text | "Updates" |
| 101 | Updates help text | Text | "Check for new versions from GitHub…" |
| 102 | Current version label | Text | "Current Version" |
| 103 | Current version display | Text | Installed version |
| 104 | Latest version label | Text | "Latest Version" |
| 105 | Latest version display | Text | "Unknown" / version number |
| 106 | Check for Updates button | Button (primary) | Checks GitHub |
| 107 | Update status | Text | "Ready" etc. |
| 108 | Progress bar | Bar | Download progress (hidden by default) |
| 109 | Progress percentage | Text | "0%" etc. |
| 110 | Updates note | Text | "Pico will restart after update" |

#### Save, Sharing & Reset

| # | Element | Type | Description |
|---|---------|------|-------------|
| 111 | Save All Settings button | Button (primary) | Persists all configuration |
| 112 | Save feedback | Text | Confirmation message |
| 113 | Sharing title | Text | "Profile & Settings Sharing" |
| 114 | Export All Data button | Button | Downloads JSON backup |
| 115 | Import All Data button | Button | Uploads JSON data |
| 116 | Sharing note | Text | "Exports Timer Profiles, Chemical Presets…" |
| 117 | Reset title | Text | "Reset" |
| 118 | Reset All Settings button | Button (danger) | Clears everything — cannot be undone |
| 119 | Reset warning | Text | "This will reset all settings to defaults…" |

---

**End of Manual**

*Cyanowood Darkroom Timer — Version 1.0.0*  
*For the latest updates, check SETTINGS → Controller Settings → Updates.*
