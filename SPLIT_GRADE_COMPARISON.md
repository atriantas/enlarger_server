# Split-Grade Analyzer - Current vs Required Implementation

## Executive Summary

The current implementation has a **fundamental architectural mismatch** with the requirements. The current system uses a **proportional split approach** based on ΔEV, while the requirements specify a **fixed filter pair approach** where each exposure is calculated independently using lux measurements.

---

## Critical Differences

### 1. Core Philosophy Mismatch

#### Current Implementation (Proportional Split)
```javascript
// Current: Uses neutralTime as base, splits it proportionally
const highlightsBase = (this.neutralTime * (100 - this.contrastSplit)) / 100;
const shadowsBase = this.neutralTime * (this.contrastSplit / 100);

// Then applies filter factors and normalizes
const rawSoftTime = highlightsBase * softFactor;
const rawHardTime = shadowsBase * hardFactor;
```

**Problem:** This assumes a single "neutral" exposure time that gets split. This doesn't match the split-grade philosophy where highlights and shadows are placed independently.

#### Required Implementation (Independent Exposures)
```javascript
// Required: Calculate each exposure independently
// Soft exposure (highlights) - uses highlight lux
softTime = highlightLux / calibrationConstant / softFilterFactor;

// Hard exposure (shadows) - uses shadow lux  
hardTime = shadowLux / calibrationConstant / hardFilterFactor;

// Total is the sum, not a split of a base time
totalTime = softTime + hardTime;
```

**Key Difference:** Each exposure is calculated from its own lux reading, not from a split of a base time.

---

### 2. Fixed Filter Pairs vs. Flexible Selection

#### Current Implementation
- **Allows any combination** of soft/hard filters
- **User selects** both filters independently
- **No fixed pairs** enforced

#### Required Implementation
- **Fixed pairs only** (per paper brand):
  - **Ilford:** Soft: Grade 00, Hard: Grade 5
  - **FOMA:** Soft: Y or 2×Y, Hard: M2 or 2×M2
- **Advanced users can override** defaults
- **Pairs are suggested, not dictated**

---

### 3. ΔEV Usage

#### Current Implementation
- **ΔEV drives the split percentage** (contrastSplit)
- **ΔEV → recommended split** (e.g., ΔEV 4.5 → 60% split)
- **Split affects time distribution**

#### Required Implementation
- **ΔEV is diagnostic only** (explains why a grade is suggested)
- **ΔEV does NOT calculate times**
- **Times come from lux measurements only**

---

### 4. Calibration Requirements

#### Current Implementation
- **Single calibration value** per paper (lux·seconds for mid-gray)
- **No highlight/shadow reference** calibration
- **Uses filter factors** to adjust exposure

#### Required Implementation (NEW)
- **Base calibration** (lux·seconds for mid-gray) - already exists
- **Highlight reference** (near paper white) - **MISSING**
- **Shadow reference** (near maximum black) - **MISSING**
- **Optional:** Separate calibration for soft-only and hard-only exposures

---

## Detailed Comparison Table

| Feature | Current Implementation | Required Implementation | Status |
|---------|----------------------|------------------------|--------|
| **Core Algorithm** | Proportional split from neutralTime | Independent lux-based calculations | ❌ Mismatch |
| **Filter Pairs** | Any combination allowed | Fixed pairs (Ilford: 00/5, FOMA: Y/M2) | ⚠️ Partial |
| **ΔEV Role** | Drives split percentage | Diagnostic only (explains grade choice) | ❌ Wrong usage |
| **Highlight Lux** | Used for ΔEV calculation | Used for soft exposure time | ⚠️ Partial |
| **Shadow Lux** | Used for ΔEV calculation | Used for hard exposure time | ⚠️ Partial |
| **Calibration** | Single mid-gray value | Mid-gray + highlight + shadow refs | ❌ Missing |
| **Normalization** | Applied to prevent density drift | Not needed (independent calculations) | ❌ Wrong approach |
| **UI Mode** | Split-Grade is a mode in METER tab | Split-Grade should be a toggle in METER | ⚠️ Partial |
| **Send to CALC** | Sends both times together | Sends soft/hard times separately | ⚠️ Partial |
| **Timer Behavior** | Single exposure | Soft → Pause → Hard exposure | ❌ Missing |

---

## Required Changes by Section

### 1. SplitGradeCalculator Class (index.html)

#### Current Issues:
1. **Uses neutralTime as base** - should use lux readings directly
2. **Implements normalization** - not needed for independent calculations
3. **ΔEV drives split** - ΔEV should be diagnostic only
4. **No fixed filter pairs** - should enforce Ilford/FOMA standards

#### Required Changes:
```javascript
class SplitGradeCalculator {
  // REMOVE: neutralTime property (not used in split-grade)
  // REMOVE: contrastSplit property (not used)
  // REMOVE: normalization logic
  
  // ADD: calibration constants for highlight and shadow
  static HIGHLIGHT_CALIBRATION = 1000; // lux·seconds (example)
  static SHADOW_CALIBRATION = 1000;    // lux·seconds (example)
  
  // ADD: fixed filter pairs
  static FIXED_PAIRS = {
    Ilford: { soft: "00", hard: "5" },
    FOMA_FOMASPEED: { soft: "2xY", hard: "2xM2" },
    FOMA_FOMATONE: { soft: "2xY", hard: "2xM2" },
  };
  
  // NEW calculate() method
  calculate(highlightLux, shadowLux) {
    // Get fixed filter pair
    const pair = this.getFixedFilterPair();
    
    // Get filter factors
    const softFactor = this.getFilterFactor(pair.soft);
    const hardFactor = this.getFilterFactor(pair.hard);
    
    // Calculate independent exposures
    const softTime = highlightLux / this.highlightCalibration / softFactor;
    const hardTime = shadowLux / this.shadowCalibration / hardFactor;
    
    // Calculate ΔEV for diagnostic purposes
    const deltaEV = Math.log2(highlightLux / shadowLux);
    
    return {
      softFilter: pair.soft,
      hardFilter: pair.hard,
      softTime: softTime,
      hardTime: hardTime,
      totalTime: softTime + hardTime,
      deltaEV: deltaEV,
      explanation: this.getExplanation(deltaEV, pair),
    };
  }
}
```

### 2. LightMeterManager Class (index.html)

#### Current Issues:
1. **Split-grade calculates times** - should only recommend proportions
2. **Uses server for calculation** - should use client-side calculation
3. **No calibration management** - needs highlight/shadow calibration

#### Required Changes:
```javascript
class LightMeterManager {
  // ADD: Calibration storage for highlight and shadow
  highlightCalibration = 1000; // lux·seconds
  shadowCalibration = 1000;    // lux·seconds
  
  // NEW: Split-Grade calculation method
  async calculateSplitGrade() {
    if (!this.highlightLux || !this.shadowLux) {
      this.showFeedback("Measure both highlight and shadow first", "error");
      return;
    }
    
    // Use SplitGradeCalculator (client-side)
    const calculator = new SplitGradeCalculator();
    calculator.highlightCalibration = this.highlightCalibration;
    calculator.shadowCalibration = this.shadowCalibration;
    calculator.paperBrand = this.paperBrand;
    calculator.fomaPaperType = this.fomaPaperType;
    
    const result = calculator.calculate(this.highlightLux, this.shadowLux);
    
    // Update UI with results
    this.updateSplitGradeDisplay(result);
    
    // Enable Send to CALC button
    document.getElementById("sendSplitToCalcBtn").disabled = false;
  }
  
  // NEW: Update split-grade display
  updateSplitGradeDisplay(result) {
    document.getElementById("splitDeltaEV").textContent = 
      result.deltaEV.toFixed(1) + " EV";
    
    document.getElementById("splitSoftFilter").textContent = 
      result.softFilter;
    
    document.getElementById("splitHardFilter").textContent = 
      result.hardFilter;
    
    document.getElementById("splitSoftTime").textContent = 
      result.softTime.toFixed(2) + "s";
    
    document.getElementById("splitHardTime").textContent = 
      result.hardTime.toFixed(2) + "s";
    
    document.getElementById("splitTotalTime").textContent = 
      result.totalTime.toFixed(2) + "s";
    
    // Show explanation
    this.showSplitGradeExplanation(result);
  }
  
  // NEW: Show why these grades were suggested
  showSplitGradeExplanation(result) {
    const explanation = result.explanation;
    // Display in UI: "ΔEV = 4.5 (low contrast) → More hard filter needed"
  }
}
```

### 3. METER Tab UI (index.html)

#### Current Issues:
1. **Split-Grade is a separate mode** - should be a toggle within Contrast mode
2. **No calibration controls** - needs highlight/shadow calibration inputs
3. **No explanation display** - needs to show why grades are suggested

#### Required Changes:
```html
<!-- CONTRAST ANALYSIS MODE (Single-Grade) -->
<div id="meterContrastMode" class="meter-mode-content">
  <!-- ADD: Contrast Mode Toggle -->
  <div class="control">
    <div class="control-label">
      <span>CONTRAST MODE</span>
    </div>
    <div class="segmented-control-container">
      <div class="segmented-control" id="contrastModeSeg">
        <button class="segmented-btn active" data-mode="single" aria-pressed="true">
          Single Grade
        </button>
        <button class="segmented-btn" data-mode="split" aria-pressed="false">
          Split Grade
        </button>
      </div>
    </div>
  </div>

  <!-- Single Grade Content (existing) -->
  <div id="singleGradeContent">
    <!-- ... existing single-grade UI ... -->
  </div>

  <!-- Split Grade Content (NEW) -->
  <div id="splitGradeContent" style="display: none">
    <!-- Fixed Filter Pair Display -->
    <div class="info-box">
      <div class="label-sm">FIXED FILTER PAIR</div>
      <div class="value-display" id="fixedPairDisplay">
        Soft: Grade 00 | Hard: Grade 5
      </div>
      <div class="label-sm" style="margin-top: 4px; font-size: 0.55rem">
        Based on Ilford split-grade standard
      </div>
    </div>

    <!-- Highlight Measurement -->
    <div class="info-box" style="margin-top: 10px">
      <div class="label-sm">HIGHLIGHT AREA (Paper White)</div>
      <div class="value-display" id="splitHighlightLux">-- lux</div>
      <button class="settings-btn" id="splitMeasureHighlightBtn">
        Measure Highlight
      </button>
    </div>

    <!-- Shadow Measurement -->
    <div class="info-box" style="margin-top: 10px">
      <div class="label-sm">SHADOW AREA (Maximum Black)</div>
      <div class="value-display" id="splitShadowLux">-- lux</div>
      <button class="settings-btn" id="splitMeasureShadowBtn">
        Measure Shadow
      </button>
    </div>

    <!-- Results -->
    <div class="info-box" style="margin-top: 15px">
      <div class="label-sm">CONTRAST RANGE (ΔEV)</div>
      <div class="timer-display" id="splitDeltaEV">--</div>
      <div class="label-sm" style="margin-top: 4px">
        Diagnostic: Explains grade choice
      </div>
    </div>

    <!-- Soft Exposure -->
    <div class="info-box" style="margin-top: 10px">
      <div class="label-sm">SOFT EXPOSURE (Highlights)</div>
      <div class="value-display" id="splitSoftFilter">--</div>
      <div class="value-display" id="splitSoftTime" style="font-size: 1.8rem">--</div>
      <div class="label-sm" style="margin-top: 4px">
        Uses highlight lux measurement
      </div>
    </div>

    <!-- Hard Exposure -->
    <div class="info-box" style="margin-top: 10px">
      <div class="label-sm">HARD EXPOSURE (Shadows)</div>
      <div class="value-display" id="splitHardFilter">--</div>
      <div class="value-display" id="splitHardTime" style="font-size: 1.8rem">--</div>
      <div class="label-sm" style="margin-top: 4px">
        Uses shadow lux measurement
      </div>
    </div>

    <!-- Total Time -->
    <div class="info-box" style="margin-top: 10px">
      <div class="label-sm">TOTAL EXPOSURE</div>
      <div class="timer-display" id="splitTotalTime">--</div>
    </div>

    <!-- Explanation -->
    <div class="info-box" style="margin-top: 15px">
      <div class="label-sm">WHY THESE GRADES?</div>
      <div class="label-sm" id="splitExplanation" style="text-align: center">
        -- 
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="settings-btn-group" style="margin-top: 15px">
      <button class="settings-btn" id="calculateSplitBtn" disabled>
        Calculate Split-Grade
      </button>
      <button class="settings-btn" id="clearSplitBtn">
        Clear Readings
      </button>
    </div>

    <!-- Send to CALC Tab -->
    <div class="settings-btn-group" style="margin-top: 10px">
      <button class="settings-btn primary" id="sendSplitToCalcBtn" disabled>
        Send to CALC Tab
      </button>
    </div>
  </div>
</div>

<!-- NEW: Calibration Section for Highlight/Shadow -->
<section class="collapsible" data-id="split-calibration">
  <button class="collapsible-header" aria-expanded="false">
    SPLIT-GRADE CALIBRATION
  </button>
  <div class="collapsible-content">
    <div class="incremental-timer">
      <div class="title-sm">Calibration Values</div>
      
      <div class="control">
        <div class="control-label">
          <span>HIGHLIGHT CALIBRATION (lux·s)</span>
          <span class="value-display" id="highlightCalibValue">1000</span>
        </div>
        <input type="range" min="100" max="5000" step="50" value="1000" 
               class="slider" id="highlightCalibSlider" />
        <div class="label-sm" style="margin-top: 4px; font-size: 0.55rem">
          For paper white / Zone VII-VIII
        </div>
      </div>

      <div class="control">
        <div class="control-label">
          <span>SHADOW CALIBRATION (lux·s)</span>
          <span class="value-display" id="shadowCalibValue">1000</span>
        </div>
        <input type="range" min="100" max="5000" step="50" value="1000" 
               class="slider" id="shadowCalibSlider" />
        <div class="label-sm" style="margin-top: 4px; font-size: 0.55rem">
          For maximum black / Zone 0
        </div>
      </div>

      <div class="info-box" style="margin-top: 10px">
        <div class="label-sm">CALIBRATION PROCEDURE</div>
        <div class="label-sm" style="text-align: left; font-size: 0.55rem">
          1. Make test strip for highlight (paper white)<br>
          2. Measure lux and note exposure time<br>
          3. Calculate: lux × time = calibration value<br>
          4. Repeat for shadow (maximum black)
        </div>
      </div>
    </div>
  </div>
</section>
```

### 4. CALC Tab Integration

#### Current Issues:
1. **Sends both times together** - should send soft/hard separately
2. **No pause between exposures** - needs soft → pause → hard sequence
3. **No explanation stored** - should log why grades were chosen

#### Required Changes:
```javascript
// In SplitGradeCalculator.sendToCalc()
sendToCalc() {
  const result = this.calculate(highlightLux, shadowLux);
  
  // Store in appState with explanation
  appState.calculator.splitGrade = {
    enabled: true,
    softFilter: result.softFilter,
    hardFilter: result.hardFilter,
    softTime: result.softTime,
    hardTime: result.hardTime,
    totalTime: result.totalTime,
    deltaEV: result.deltaEV,
    explanation: result.explanation,
    // Store lux values for reference
    highlightLux: highlightLux,
    shadowLux: shadowLux,
  };
  
  // Update CALC tab display
  const display = document.getElementById("splitGradeDisplay");
  if (display) display.style.display = "block";
  
  // Show explanation in CALC tab
  const explanationEl = document.getElementById("splitGradeExplanation");
  if (explanationEl) {
    explanationEl.textContent = result.explanation;
  }
  
  // Log to exposure log
  if (window.exposureLogManager) {
    window.exposureLogManager.addSplitPhase({
      softFilter: result.softFilter,
      hardFilter: result.hardFilter,
      softTime: result.softTime,
      hardTime: result.hardTime,
      totalTime: result.totalTime,
      deltaEV: result.deltaEV,
      highlightLux: highlightLux,
      shadowLux: shadowLux,
    });
  }
  
  // Switch to CALC tab
  switchTab("calc");
}
```

### 5. Timer Behavior (CALC Tab)

#### Current Issues:
1. **Single exposure timer** - needs two-phase timer
2. **No pause between exposures** - needs configurable pause

#### Required Changes:
```javascript
// In CALC tab timer logic
class IncrementalTimer {
  // ADD: Split-grade timer support
  startSplitGrade(softTime, hardTime, pauseBetween = 2.0) {
    this.softTime = softTime;
    this.hardTime = hardTime;
    this.pauseBetween = pauseBetween;
    this.currentPhase = "soft";
    
    // Start soft exposure
    this.start(softTime);
    
    // After soft completes, pause, then start hard
    this.onComplete = () => {
      if (this.currentPhase === "soft") {
        // Show pause message
        this.showPauseMessage(pauseBetween);
        
        // Wait for pause, then start hard
        setTimeout(() => {
          this.currentPhase = "hard";
          this.start(hardTime);
        }, pauseBetween * 1000);
      }
    };
  }
  
  showPauseMessage(seconds) {
    // Display: "Pause: X seconds before hard exposure"
    // Could trigger safelight off/on here
  }
}
```

---

## Implementation Plan

### Phase 1: Core Algorithm Changes (Priority: HIGH)

1. **Modify SplitGradeCalculator.calculate()**
   - Remove neutralTime dependency
   - Remove normalization logic
   - Implement independent lux-based calculations
   - Add fixed filter pair enforcement

2. **Update LightMeterManager.calculateSplitGrade()**
   - Use client-side calculation (not server)
   - Add calibration storage
   - Implement explanation generation

### Phase 2: UI Changes (Priority: HIGH)

1. **Update METER tab Contrast mode**
   - Add Single/Split toggle
   - Add calibration sliders
   - Add explanation display
   - Update button labels

2. **Update CALC tab**
   - Add split-grade explanation display
   - Update timer to support two-phase exposure

### Phase 3: Calibration System (Priority: MEDIUM)

1. **Add calibration management**
   - Highlight calibration (paper white)
   - Shadow calibration (maximum black)
   - Store in localStorage per paper type

2. **Add calibration procedure UI**
   - Step-by-step instructions
   - Auto-calculate from test strips

### Phase 4: Timer Behavior (Priority: MEDIUM)

1. **Implement two-phase timer**
   - Soft exposure → Pause → Hard exposure
   - Configurable pause duration
   - Safelight auto-off during pause

### Phase 5: Explanation System (Priority: LOW)

1. **Add ΔEV interpretation**
   - Low contrast: "More hard filter needed"
   - Normal contrast: "Balanced split"
   - High contrast: "More soft filter needed"

2. **Add grade justification**
   - "Grade 00 selected for highlights (paper white)"
   - "Grade 5 selected for shadows (maximum black)"

---

## Migration Strategy

### Current → Required Transition

1. **Keep existing SplitGradeCalculator** as legacy
2. **Create new SplitGradeAnalyzer** class with required logic
3. **Add feature flag** to switch between old/new behavior
4. **Gradual migration**:
   - Phase 1: Add new calculation alongside old
   - Phase 2: Update UI to use new calculation
   - Phase 3: Remove old calculation
   - Phase 4: Update documentation

### Backward Compatibility

- **Preserve existing presets** (convert format if needed)
- **Keep existing UI** as fallback
- **Add migration guide** for users

---

## Testing Requirements

### Unit Tests
1. **Fixed filter pair selection** (Ilford, FOMA)
2. **Lux-based time calculation** (highlight and shadow)
3. **ΔEV calculation** (log2(highlight/shadow))
4. **Explanation generation** (ΔEV interpretation)

### Integration Tests
1. **METER tab → CALC tab flow**
2. **Split-grade timer behavior** (soft → pause → hard)
3. **Calibration persistence** (localStorage)
4. **Paper brand switching**

### User Acceptance Tests
1. **Ilford split-grade procedure**
2. **FOMA split-grade procedure**
3. **Override defaults** (advanced users)
4. **Calibration workflow**

---

## Documentation Updates Needed

1. **SPLIT_GRADE_ANALYZER.md** - Update with new algorithm
2. **USER_MANUAL.md** - Add split-grade workflow
3. **README.md** - Update feature list
4. **API Documentation** - Update server endpoints if needed

---

## Summary of Changes

### Files to Modify
1. **index.html** (SplitGradeCalculator, LightMeterManager, UI)
2. **SPLIT_GRADE_ANALYZER.md** (documentation)
3. **USER_MANUAL.md** (user guide)

### Key Changes
1. **Algorithm**: Proportional split → Independent lux-based calculations
2. **Filters**: Flexible selection → Fixed pairs with override
3. **ΔEV**: Drives split → Diagnostic only
4. **Calibration**: Single value → Highlight + Shadow references
5. **UI**: Separate mode → Toggle within Contrast mode
6. **Timer**: Single exposure → Two-phase with pause

### Effort Estimate
- **Phase 1 (Core)**: 2-3 days
- **Phase 2 (UI)**: 1-2 days
- **Phase 3 (Calibration)**: 1 day
- **Phase 4 (Timer)**: 1 day
- **Phase 5 (Explanation)**: 1 day
- **Testing**: 2 days
- **Documentation**: 1 day

**Total: 9-11 days**

---

## Next Steps

1. **Review this document** with team
2. **Prioritize phases** based on user needs
3. **Create implementation tickets** for each phase
4. **Start with Phase 1** (core algorithm)
5. **Test thoroughly** before release
6. **Update documentation** as you go

---

**Document Version**: 1.0  
**Date**: 2026-01-23  
**Status**: Analysis Complete - Ready for Implementation
