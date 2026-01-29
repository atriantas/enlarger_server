# Improved Split-Grade Calculation Algorithm Design

## 1. Design Goals

### 1.1 Primary Objectives

1. **More Realistic Exposure Times**: Match darkroom experience
2. **Dynamic Filter Selection**: Choose optimal filter pair based on contrast
3. **Sensitometric Foundation**: Incorporate paper response characteristics
4. **Practical Implementation**: Feasible on Pico 2 W with limited resources

### 1.2 Constraints

- Must work within Pico 2 W memory/processing limits
- Maintain backward compatibility with existing calibration
- Simple enough for users to understand and trust
- Gradual improvement path (phased implementation)

## 2. Algorithm Architecture

### 2.1 Three-Tier Approach

#### Tier 1: Dynamic Filter Selection (Immediate)

- Replace fixed filters (00, 5) with contrast-based selection
- Simple rule-based system
- Minimal computational overhead

#### Tier 2: Enhanced Calculation (Medium-term)

- Incorporate paper γ values
- Density-space additivity
- Basic optimization

#### Tier 3: Full Optimization (Long-term)

- Complete Heiland-like algorithm
- Advanced sensitometric modeling
- Requires more research and resources

## 3. Tier 1: Dynamic Filter Selection Algorithm

### 3.1 Input Parameters

```
highlight_lux: Lux reading at highlight area
shadow_lux: Lux reading at shadow area
calibration: Calibration constant (lux·seconds)
filter_system: 'ilford', 'foma_fomaspeed', 'foma_fomatone'
paper_type: Optional paper identifier for advanced features
```

### 3.2 Core Algorithm

#### Step 1: Calculate Contrast (ΔEV)

```
ΔEV = abs(log₂(shadow_lux / highlight_lux))
```

#### Step 2: Select Filter Pair Based on ΔEV

```
For Ilford system:
  if ΔEV < 1.0:        # Very low contrast
    soft_filter = '1'  (Grade 1)
    hard_filter = '3'  (Grade 3)
  elif ΔEV < 2.0:      # Low contrast
    soft_filter = '0'  (Grade 0)
    hard_filter = '4'  (Grade 4)
  elif ΔEV < 3.0:      # Moderate contrast
    soft_filter = '00' (Grade 00)
    hard_filter = '5'  (Grade 5)
  else:                # High contrast
    soft_filter = '00' (Grade 00)
    hard_filter = '5'  (Grade 5)
    # Apply contrast reduction factor
```

#### Step 3: Calculate Base Exposure Times

```
base_highlight = calibration / highlight_lux
base_shadow = calibration / shadow_lux
```

#### Step 4: Apply Filter Factors

```
soft_time = base_highlight × factor_soft
hard_time = base_shadow × factor_hard
```

#### Step 5: Apply Contrast-Dependent Adjustments

**High Contrast Adjustment (ΔEV > 3.0)**:

```
# Reduce extreme imbalance
if ΔEV > 3.0:
  ratio = hard_time / soft_time
  if ratio < 0.1:  # Hard exposure too small
    hard_time = soft_time × 0.1  # Minimum 10% ratio
```

**Low Contrast Adjustment (ΔEV < 1.5)**:

```
# Consider single-filter printing
if ΔEV < 1.5:
  single_grade = recommend_single_filter(ΔEV)
  if single_grade is not None:
    # Offer single-filter alternative
    single_time = calculate_single_exposure(ΔEV, highlight_lux, shadow_lux)
```

### 3.3 Filter Selection Tables

#### Ilford Multigrade

```
ΔEV Range   | Soft Filter | Hard Filter | Notes
------------|-------------|-------------|------
< 1.0       | 1           | 3           | Very low contrast
1.0 - 1.5   | 0           | 4           | Low contrast
1.5 - 2.5   | 00          | 5           | Normal contrast
2.5 - 3.5   | 00          | 5           | High contrast
> 3.5       | 00          | 5*          | Very high contrast (*adjusted)
```

#### FOMA FOMASPEED

```
ΔEV Range   | Soft Filter | Hard Filter
------------|-------------|-------------
< 1.0       | Y           | M1
1.0 - 1.5   | 2xY         | 2xM1
1.5 - 2.5   | 2xY         | 2xM2
2.5 - 3.5   | 2xY         | 2xM2
> 3.5       | 2xY         | 2xM2*
```

### 3.4 Single-Filter Recommendation

For very low contrast negatives (ΔEV < 1.0), consider single-filter printing:

```
def recommend_single_filter(ΔEV):
  if ΔEV < 0.5:
    return '2'  # Normal grade
  elif ΔEV < 1.0:
    return '1'  # Slightly soft
  else:
    return None  # Use split-grade
```

## 4. Tier 2: Enhanced Calculation Algorithm

### 4.1 Paper γ Values

Store paper contrast (γ) for each filter grade:

```
ILFORD_γ_VALUES = {
  '00': 0.4,   # Very soft
  '0':  0.5,   # Soft
  '1':  0.6,   # Medium-soft
  '2':  0.7,   # Normal
  '3':  0.9,   # Medium-hard
  '4':  1.1,   # Hard
  '5':  1.3,   # Very hard
}
```

### 4.2 Density-Space Calculation

#### Step 1: Convert to Log Exposure

```
logE_highlight = log10(calibration / highlight_lux)
logE_shadow = log10(calibration / shadow_lux)
```

#### Step 2: Calculate Effective γ

```
γ_effective = (γ_soft × w_soft) + (γ_hard × w_hard)
where w_soft, w_hard are exposure weights
```

#### Step 3: Calculate Density Range

```
ΔD_negative = γ_effective × (logE_shadow - logE_highlight)
```

#### Step 4: Adjust Exposures for Target Densities

```
# Target densities (adjustable)
D_highlight_target = 0.1  # Just above paper base
D_shadow_target = 1.8     # Near maximum black

# Solve for exposures (simplified)
soft_time = 10**((D_highlight_target / γ_soft) + logE_highlight)
hard_time = 10**(((D_shadow_target - D_highlight_target) / γ_hard) + logE_shadow)
```

### 4.3 Optimization (Simplified)

```
# Minimize density error
def calculate_optimal_exposures(highlight_lux, shadow_lux, γ_soft, γ_hard):
  # Grid search over possible exposure ratios
  best_error = float('inf')
  best_soft = best_hard = 0

  for ratio in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    soft_time = base_highlight × ratio
    hard_time = base_shadow × (1 - ratio)

    D_highlight = γ_soft × log10(soft_time) + γ_hard × log10(hard_time)
    D_shadow = D_highlight + ΔD_negative

    error = abs(D_highlight - 0.1) + abs(D_shadow - 1.8)

    if error < best_error:
      best_error = error
      best_soft, best_hard = soft_time, hard_time

  return best_soft, best_hard, best_error
```

## 5. Implementation Plan

### 5.1 Phase 1A: Dynamic Filter Selection

**Files to modify**:

- `lib/light_sensor.py`: `calculate_split_grade_enhanced()` method
- `index.html`: METER tab UI updates

**Changes**:

1. Replace fixed filter selection with ΔEV-based selection
2. Add filter selection logic tables
3. Update UI to show selected filters

### 5.2 Phase 1B: Contrast Adjustments

**Changes**:

1. Add high-contrast adjustment factor
2. Implement single-filter recommendation
3. Add user override options

### 5.3 Phase 2A: Paper γ Integration

**Changes**:

1. Add paper γ data structures
2. Implement density-space calculation
3. Add paper type selection

### 5.4 Phase 2B: Basic Optimization

**Changes**:

1. Implement simplified optimization
2. Add target density parameters
3. Improve exposure balance

### 5.5 Phase 3: Advanced Features

**Changes**:

1. Full Heiland-like algorithm (after research)
2. Paper calibration system
3. Advanced user controls

## 6. Testing Strategy

### 6.1 Test Cases

```
Test 1: Very low contrast (ΔEV = 0.5)
  Expected: Single-filter or close filters (1 and 3)

Test 2: Normal contrast (ΔEV = 2.0)
  Expected: Standard split-grade (00 and 5)

Test 3: High contrast (ΔEV = 4.0)
  Expected: Adjusted exposures, more balanced

Test 4: Extreme contrast (ΔEV = 5.0)
  Expected: Significant adjustments, possible warning
```

### 6.2 Validation Methods

1. **Mathematical Consistency**: Verify algorithm produces reasonable values
2. **Sensitometric Plausibility**: Check against paper response curves
3. **User Testing**: Compare with darkroom experience
4. **A/B Testing**: Compare with current algorithm

## 7. User Interface Updates

### 7.1 METER Tab Enhancements

```
Current: "Split-Grade Analyzer"
Proposed: "Advanced Split-Grade Calculator"

New elements:
1. Contrast display: "ΔEV: 2.3 (Moderate)"
2. Filter selection: "Soft: Grade 00, Hard: Grade 5"
3. Adjustment indicators: "High contrast adjustment applied"
4. Alternative suggestions: "Consider single filter: Grade 2"
5. Override controls: "Manual filter selection"
```

### 7.2 Calibration Interface

```
New section: "Paper Settings"
- Paper type selection (Ilford MG IV, FOMA, etc.)
- Custom γ values (advanced)
- Save paper profiles
```

## 8. Migration Path

### 8.1 Backward Compatibility

- Maintain existing `calculate_split_grade()` method
- New algorithm in `calculate_split_grade_enhanced_v2()`
- Gradual migration in UI

### 8.2 Configuration Options

```
Settings option: "Split-Grade Algorithm"
- Legacy (current)
- Enhanced v1 (dynamic filters)
- Enhanced v2 (with γ)
- Advanced (full optimization)
```

## 9. Conclusion

This improved algorithm addresses the key issue of unrealistic exposure times by:

1. **Dynamic Filter Selection**: Choosing appropriate filters based on contrast
2. **Contrast Adjustments**: Balancing exposures for extreme cases
3. **Sensitometric Foundation**: Incorporating paper response characteristics
4. **Practical Implementation**: Feasible on resource-constrained hardware

**Recommended First Step**: Implement Phase 1A (dynamic filter selection) as it provides immediate improvement with minimal risk and complexity.
