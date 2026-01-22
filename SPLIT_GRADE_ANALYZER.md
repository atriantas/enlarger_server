# Split-Grade Analyzer - Detailed Technical Documentation

## Overview

The Split-Grade Analyzer is a sophisticated darkroom printing tool that implements the Ilford split-grade technique. This method separates contrast control into two distinct exposures: one for highlights (soft filter) and one for shadows (hard filter), allowing precise contrast manipulation without changing overall exposure density.

## Architecture Philosophy

The tool follows **Option A** design philosophy:
- **Exposure time** comes from Exposure Meter / Test Strip (neutralTime)
- **Contrast Analyzer** provides ΔEV which drives the recommended split
- **Filter factors** are normalized to prevent total exposure drift
- **User can override** the recommended split manually

## Core Class: SplitGradeCalculator

### Class Structure

```javascript
class SplitGradeCalculator {
  // Static configuration tables
  static DELTA_EV_TO_SPLIT = [...];
  static REFERENCE_FACTOR = 1.0;
  static FILTER_FACTORS = {...};
  
  // Instance properties
  neutralTime: number;        // Base exposure time from test strip (seconds)
  paperBrand: string;         // 'Ilford', 'Kodak', 'FOMA', 'Custom'
  fomaPaperType: string;      // 'fomaspeed' or 'fomatonemg'
  softFilter: string;         // Soft filter number (e.g., '0', '4', '5')
  hardFilter: string;         // Hard filter number
  customFactors: Object;      // Custom filter factors for all 7 grades
  contrastSplit: number;      // Shadow emphasis percentage (0-100)
  recommendedSplit: number;   // ΔEV-derived split (null if no ΔEV)
  userOverride: boolean;      // True if user manually adjusted split
}
```

## Key Formulas and Calculations

### 1. ΔEV to Split Percentage Mapping

The tool uses a lookup table to convert measured scene contrast (ΔEV) to recommended split percentage:

```javascript
static DELTA_EV_TO_SPLIT = [
  { deltaEV: 3.0, split: 70 },  // Very low contrast → heavy hard emphasis
  { deltaEV: 4.0, split: 65 },  // Low contrast
  { deltaEV: 4.5, split: 60 },
  { deltaEV: 5.0, split: 55 },
  { deltaEV: 5.5, split: 50 },  // Normal contrast → balanced
  { deltaEV: 6.0, split: 45 },
  { deltaEV: 6.5, split: 40 },
  { deltaEV: 7.0, split: 35 },  // High contrast
  { deltaEV: 7.5, split: 30 },
  { deltaEV: 8.0, split: 25 },  // Very high contrast → heavy soft emphasis
];
```

**Logic:**
- Low contrast (ΔEV < 4) → More hard filter to increase contrast
- Normal contrast (ΔEV ~5-6) → Balanced 50/50 split
- High contrast (ΔEV > 7) → More soft filter to reduce contrast

**Interpolation Formula:**
```javascript
deltaEVToSplit(deltaEV) {
  // Clamp to table bounds
  if (deltaEV <= table[0].deltaEV) return table[0].split;
  if (deltaEV >= table[table.length - 1].deltaEV)
    return table[table.length - 1].split;

  // Linear interpolation between bracketing entries
  for (let i = 0; i < table.length - 1; i++) {
    if (deltaEV >= table[i].deltaEV && deltaEV <= table[i + 1].deltaEV) {
      const t = (deltaEV - table[i].deltaEV) / 
                (table[i + 1].deltaEV - table[i].deltaEV);
      return Math.round(
        table[i].split + t * (table[i + 1].split - table[i].split)
      );
    }
  }
  return 50; // Fallback to balanced
}
```

### 2. Filter Factor Database

Each paper brand has predefined filter factors (relative to Grade 2 baseline):

```javascript
static FILTER_FACTORS = {
  Ilford: { "00": 1.0, 0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.2, 5: 1.5 },
  Kodak:  { 0: 1.0, 1: 1.0, 2: 1.0, 3: 1.1, 4: 1.3, 5: 1.6 },
  FOMA:   { "00": 1.6, 0: 1.4, 1: 1.0, 2: 1.4, 3: 2.1, 4: 2.6, 5: 4.6 },
  FOMASPEED: { "00": 1.6, 0: 1.4, 1: 1.0, 2: 1.4, 3: 2.1, 4: 2.6, 5: 4.6 },
  FOMATONE: { "00": 2.0, 0: 1.5, 1: 1.0, 2: 1.5, 3: 1.8, 4: 2.0, 5: 3.0 },
};
```

**Example:** Grade 5 requires 1.5× more exposure than Grade 2 on Ilford paper.

### 3. Core Calculation Algorithm

The `calculate()` method implements the complete split-grade calculation with normalization:

```javascript
calculate() {
  // Step 1: Get filter factors
  let softFactor, hardFactor;
  
  if (this.paperBrand === "Custom") {
    softFactor = this.customFactors[this.softFilter] || 1.0;
    hardFactor = this.customFactors[this.hardFilter] || 1.0;
  } else if (this.paperBrand === "FOMA") {
    const fomaKey = this.fomaPaperType === "fomaspeed" ? "FOMASPEED" : "FOMATONE";
    softFactor = SplitGradeCalculator.FILTER_FACTORS[fomaKey][this.softFilter] || 1.0;
    hardFactor = SplitGradeCalculator.FILTER_FACTORS[fomaKey][this.hardFilter] || 1.0;
  } else {
    softFactor = SplitGradeCalculator.FILTER_FACTORS[this.paperBrand][this.softFilter] || 1.0;
    hardFactor = SplitGradeCalculator.FILTER_FACTORS[this.paperBrand][this.hardFilter] || 1.0;
  }

  // Step 2: Calculate base times based on contrastSplit percentage
  const highlightsBase = (this.neutralTime * (100 - this.contrastSplit)) / 100;
  const shadowsBase = this.neutralTime * (this.contrastSplit / 100);

  // Step 3: Apply filter factors (raw, before normalization)
  const rawSoftTime = highlightsBase * softFactor;
  const rawHardTime = shadowsBase * hardFactor;
  const rawTotal = rawSoftTime + rawHardTime;

  // Step 4: Calculate normalization scale
  // Target: neutralTime × referenceFactor (Grade 2 baseline)
  const targetTotal = this.neutralTime * SplitGradeCalculator.REFERENCE_FACTOR;
  const normalizationScale = rawTotal > 0 ? targetTotal / rawTotal : 1.0;

  // Step 5: Apply normalization to preserve total exposure
  const softTime = rawSoftTime * normalizationScale;
  const hardTime = rawHardTime * normalizationScale;
  const totalTime = softTime + hardTime; // Should be ≈ targetTotal

  return {
    highlightsBase,
    shadowsBase,
    softTime,
    hardTime,
    totalTime,
    softFactor,
    hardFactor,
    contrastSplit: this.contrastSplit,
    recommendedSplit: this.recommendedSplit,
    userOverride: this.userOverride,
    normalizationScale,
    rawTotal,
  };
}
```

### 4. Normalization Formula

**Purpose:** Prevent density drift when changing filters. The total exposure should remain constant regardless of filter combination.

**Formula:**
```
normalizationScale = targetTotal / rawTotal
where:
  targetTotal = neutralTime × REFERENCE_FACTOR (1.0)
  rawTotal = rawSoftTime + rawHardTime

softTime = rawSoftTime × normalizationScale
hardTime = rawHardTime × normalizationScale
```

**Example Calculation:**
```
neutralTime = 10.0s
contrastSplit = 50% (balanced)
softFilter = "00" (softFactor = 1.6)
hardFilter = "5" (hardFactor = 1.5)

highlightsBase = 10.0 × (100 - 50) / 100 = 5.0s
shadowsBase = 10.0 × 50 / 100 = 5.0s

rawSoftTime = 5.0 × 1.6 = 8.0s
rawHardTime = 5.0 × 1.5 = 7.5s
rawTotal = 8.0 + 7.5 = 15.5s

targetTotal = 10.0 × 1.0 = 10.0s
normalizationScale = 10.0 / 15.5 = 0.645

softTime = 8.0 × 0.645 = 5.16s
hardTime = 7.5 × 0.645 = 4.84s
totalTime = 5.16 + 4.84 = 10.0s ✓ (matches neutralTime)
```

## UI Components and Event Flow

### 1. Neutral Time Input

```javascript
// Slider: neutralTimeSlider (0.4s - 50s, step 0.1)
neutralSlider.addEventListener("input", (e) => {
  this.neutralTime = parseFloat(e.target.value);
  document.getElementById("neutralTimeValue").textContent = 
    `${this.neutralTime.toFixed(1)}s`;
  this.calculate();
});
```

### 2. Paper Brand Selection

```javascript
// Dropdown: splitPaperBrand
paperSelect.addEventListener("change", (e) => {
  this.paperBrand = e.target.value;
  this.updateBrandVisibility(); // Show/hide FOMA/Custom sections
  this.calculate();
});
```

**Brand-Specific UI:**
- **FOMA:** Shows paper type selector (FOMASPEED vs FOMATONE)
- **Custom:** Shows 7 grade factor inputs (00, 0, 1, 2, 3, 4, 5)
- **Ilford/Kodak:** Uses predefined factors

### 3. Filter Selection

```javascript
// Segmented controls: splitSoftFilter, splitHardFilter
container.addEventListener("click", (e) => {
  const btn = e.target.closest(".segmented-btn");
  if (!btn) return;

  // Remove active from all, add to clicked
  container.querySelectorAll(".segmented-btn").forEach((b) => 
    b.classList.remove("active")
  );
  btn.classList.add("active");

  // Update state
  const filter = btn.dataset.filter;
  if (type === "soft") {
    this.softFilter = filter;
  } else {
    this.hardFilter = filter;
  }

  this.calculate();
});
```

### 4. Contrast Split Slider

```javascript
// Slider: contrastSplitSlider (0-100%, step 5)
splitSlider.addEventListener("input", (e) => {
  this.contrastSplit = parseInt(e.target.value);
  this.userOverride = true; // User manually adjusted
  document.getElementById("contrastSplitValue").textContent = 
    `${this.contrastSplit}%`;
  this.updateSplitRecommendationDisplay();
  this.calculate();
});
```

### 5. Sync from Contrast Analyzer

```javascript
syncFromContrastAnalyzer() {
  const lightMeter = window.lightMeterManager;
  if (lightMeter && lightMeter.deltaEV !== null) {
    this.recommendedSplit = this.deltaEVToSplit(lightMeter.deltaEV);

    // If user hasn't overridden, apply the recommendation
    if (!this.userOverride) {
      this.contrastSplit = this.recommendedSplit;
      const slider = document.getElementById("contrastSplitSlider");
      if (slider) slider.value = this.contrastSplit;
      document.getElementById("contrastSplitValue").textContent = 
        `${this.contrastSplit}%`;
    }

    this.updateSplitRecommendationDisplay();
    this.calculate();
  } else {
    this.recommendedSplit = null;
    this.updateSplitRecommendationDisplay();
  }
}
```

## Integration with Other Components

### 1. Contrast Analyzer (LightMeterManager)

The Split-Grade Analyzer reads ΔEV from the Contrast Analyzer:

```javascript
// In LightMeterManager
calculateSplitGrade() {
  // ... measurement logic ...
  const deltaEV = Math.log2(highlightLux / shadowLux);
  
  // Store in instance for SplitGradeCalculator to read
  this.deltaEV = deltaEV;
}
```

### 2. CALC Tab Integration

When "Send to CALC" is clicked:

```javascript
sendToCalc() {
  const result = this.calculate();

  // Store in appState
  appState.calculator.splitGrade = {
    enabled: true,
    neutralTime: this.neutralTime,
    highlightsBase: result.highlightsBase,
    shadowsBase: result.shadowsBase,
    softTime: result.softTime,
    hardTime: result.hardTime,
    totalTime: result.totalTime,
    softFilter: this.softFilter,
    hardFilter: this.hardFilter,
    // ... other properties
  };

  // Update CALC tab display
  const display = document.getElementById("splitGradeDisplay");
  if (display) display.style.display = "block";
  // ... update individual displays ...

  // Log to exposure log
  if (window.exposureLogManager) {
    window.exposureLogManager.addSplitPhase({
      neutralTime: this.neutralTime,
      paperBrand: this.paperBrand,
      softFilter: this.softFilter,
      hardFilter: this.hardFilter,
      highlightsBase: result.highlightsBase,
      shadowsBase: result.shadowsBase,
      softTime: result.softTime,
      hardTime: result.hardTime,
      totalTime: result.totalTime,
      contrastSplit: this.contrastSplit,
      normalizationScale: result.normalizationScale,
    });
  }

  // Switch to CALC tab
  switchTab("calc");
}
```

### 3. Preset System

The tool supports saving/loading split-grade configurations:

```javascript
savePreset() {
  const preset = {
    name: name,
    neutralTime: this.neutralTime,
    paperBrand: this.paperBrand,
    fomaPaperType: this.fomaPaperType,
    softFilter: this.softFilter,
    hardFilter: this.hardFilter,
    contrastSplit: this.contrastSplit,
    customFactors: { ...this.customFactors },
    date: new Date().toISOString(),
  };

  // Save to localStorage via StorageManager
  StorageManager.saveSplitPresets(this.splitPresets);
}
```

## Example Workflows

### Workflow 1: Test Strip → Split-Grade → Print

1. **Create test strip** with neutral exposure (e.g., 10s)
2. **Measure ΔEV** using Contrast Analyzer (e.g., ΔEV = 4.5)
3. **Sync to Split-Grade** (recommended split = 60%)
4. **Select filters** (e.g., Soft: Grade 00, Hard: Grade 5)
5. **Calculate** → Get: 4.0s (soft) + 6.0s (hard) = 10.0s total
6. **Send to CALC** → Switch to CALC tab
7. **Start exposure** → Enlarger runs for calculated times

### Workflow 2: Manual Override

1. **Load neutral time** from test strip (e.g., 15.0s)
2. **Manually set contrast split** to 70% (more shadow emphasis)
3. **Select filters** (e.g., Soft: Grade 1, Hard: Grade 4)
4. **Calculate** → Get: 4.5s (soft) + 10.5s (hard) = 15.0s total
5. **Note:** Normalization ensures total remains 15.0s

### Workflow 3: Custom Paper Factors

1. **Select "Custom"** paper brand
2. **Enter filter factors** for all 7 grades (e.g., Grade 5 = 2.0×)
3. **Select filters** (e.g., Soft: Grade 2, Hard: Grade 5)
4. **Calculate** → Uses custom factors instead of predefined

## Key Features

### 1. Normalization
- **Prevents density drift** when changing filters
- **Maintains total exposure** at neutralTime × referenceFactor
- **Only redistributes contrast** between highlights and shadows

### 2. ΔEV-Driven Recommendations
- **Automatic split calculation** based on measured scene contrast
- **Linear interpolation** between table entries
- **User override** capability for manual adjustment

### 3. Paper Brand Support
- **Ilford Multigrade** (standard factors)
- **Kodak Polycontrast** (standard factors)
- **FOMA** (paper-specific: FOMASPEED vs FOMATONE)
- **Custom** (user-defined factors for all 7 grades)

### 4. Preset Management
- **Save** current configuration with custom name
- **Load** previously saved presets
- **Delete** individual presets or clear all
- **Persistent storage** via localStorage

### 5. Integration
- **Sync from Contrast Analyzer** (ΔEV → split percentage)
- **Send to CALC tab** (seamless workflow)
- **Exposure logging** (automatic session recording)

## Technical Notes

### Why Normalization is Critical

Without normalization, changing filters would change total exposure:
```
Without normalization:
Grade 00 + Grade 5 = 1.6× + 1.5× = 3.1× exposure
Result: Print becomes 3 stops denser!

With normalization:
Scale = 1.0 / 3.1 = 0.32
Adjusted: 1.6×0.32 + 1.5×0.32 = 1.0× exposure
Result: Print density stays constant ✓
```

### Filter Factor Interpretation

- **Factor = 1.0**: No change (Grade 2 baseline)
- **Factor > 1.0**: More exposure needed (denser filter)
- **Factor < 1.0**: Less exposure needed (clearer filter)

### Contrast Split Percentage

- **0%**: All exposure in highlights (soft filter only)
- **50%**: Balanced split (equal time for both filters)
- **100%**: All exposure in shadows (hard filter only)

### ΔEV Interpretation

- **ΔEV < 4**: Low contrast scene → More hard filter (70% split)
- **ΔEV = 5-6**: Normal contrast → Balanced (50% split)
- **ΔEV > 7**: High contrast scene → More soft filter (25% split)

## Code Examples

### Complete Calculation Example

```javascript
// Initialize calculator
const calculator = new SplitGradeCalculator();

// Set parameters
calculator.neutralTime = 12.0;      // Test strip result
calculator.paperBrand = "Ilford";
calculator.softFilter = "00";       // Soft filter for highlights
calculator.hardFilter = "5";        // Hard filter for shadows
calculator.contrastSplit = 60;      // 60% shadow emphasis

// Calculate
const result = calculator.calculate();

console.log(result);
// {
//   highlightsBase: 4.8,    // 12.0 × (100 - 60) / 100
//   shadowsBase: 7.2,       // 12.0 × 60 / 100
//   softTime: 4.8,          // highlightsBase × 1.0 (Grade 00 factor)
//   hardTime: 10.8,         // shadowsBase × 1.5 (Grade 5 factor)
//   totalTime: 15.6,        // rawTotal before normalization
//   softFactor: 1.0,
//   hardFactor: 1.5,
//   normalizationScale: 0.641,  // 12.0 / 15.6
//   rawTotal: 15.6
// }

// After normalization:
// softTime = 4.8 × 0.641 = 3.08s
// hardTime = 10.8 × 0.641 = 6.92s
// totalTime = 3.08 + 6.92 = 10.0s ✓ (matches neutralTime)
```

### ΔEV to Split Conversion

```javascript
// Low contrast scene (ΔEV = 3.5)
const split = calculator.deltaEVToSplit(3.5);
// Returns: 67% (interpolated between 70% at 3.0 and 65% at 4.0)

// Normal contrast scene (ΔEV = 5.5)
const split = calculator.deltaEVToSplit(5.5);
// Returns: 50% (exact match from table)

// High contrast scene (ΔEV = 7.2)
const split = calculator.deltaEVToSplit(7.2);
// Returns: 34% (interpolated between 35% at 7.0 and 30% at 7.5)
```

### Custom Filter Factors

```javascript
// Define custom factors for a specific paper
calculator.paperBrand = "Custom";
calculator.customFactors = {
  "00": 1.8,  // Very soft
  0: 1.4,
  1: 1.0,
  2: 1.0,     // Baseline
  3: 1.2,
  4: 1.6,
  5: 2.2,     // Very hard
};

// Now calculations use these custom factors
const result = calculator.calculate();
```

## Troubleshooting

### Issue: Total exposure doesn't match neutralTime

**Cause:** Normalization scale calculation error
**Solution:** Check that `targetTotal = neutralTime × REFERENCE_FACTOR` and `rawTotal > 0`

### Issue: Split recommendation not appearing

**Cause:** No ΔEV data from Contrast Analyzer
**Solution:** Measure highlight and shadow lux values first, then sync

### Issue: Filter factors seem wrong

**Cause:** Wrong paper brand selected
**Solution:** Verify paper brand matches actual paper, or use Custom mode with manual factors

### Issue: Presets not loading

**Cause:** localStorage corruption or version mismatch
**Solution:** Clear presets and recreate, or check browser console for errors

## References

- **Ilford Split-Grade Technique**: https://www.ilford.com/how-to/split-grade-printing/
- **Filter Factor Database**: Based on manufacturer specifications
- **ΔEV Mapping**: Empirical darkroom testing and calibration

## Version History

- **v1.0**: Initial implementation with Ilford, Kodak, FOMA support
- **v1.1**: Added custom filter factors and preset system
- **v1.2**: Enhanced ΔEV integration and normalization
- **v1.3**: UI improvements and accessibility enhancements

---

**Last Updated**: 2026-01-22  
**Author**: Darkroom Timer Development Team  
**License**: Open Source (MIT)
