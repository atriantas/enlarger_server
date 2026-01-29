# Split-Grade Algorithm Comparison: Current vs. Heiland Approach

## Current Algorithm Analysis

### Mathematical Model

```
1. ΔEV = log₂(shadow_lux / highlight_lux)
2. Base_time_highlight = calibration / highlight_lux
3. Base_time_shadow = calibration / shadow_lux
4. Soft_time = Base_time_highlight × soft_factor
5. Hard_time = Base_time_shadow × hard_factor
6. Total_time = Soft_time + Hard_time
```

### Assumptions:

1. **Linear Response**: Paper density is linear with exposure (ignores D-logE curve)
2. **Additive Exposures**: Total effect = sum of individual exposures
3. **Fixed Filters**: Always use extreme filters (00 and 5)
4. **Independent Effects**: Soft filter only affects highlights, hard only shadows

### Limitations:

1. **Unrealistic for High Contrast**: Extreme contrast negatives produce unrealistic times
2. **No Paper Curve**: Doesn't account for paper's non-linear response
3. **Fixed Filter Pair**: Doesn't adapt to contrast range
4. **No Highlight/Shadow Compression**: Can't handle beyond paper latitude

## Heiland Approach (Hypothesized)

### Sensitometric Foundation

Heiland likely uses paper characteristic curves:

```
D = f(log E)
where f() is the paper's response function with:
- Toe region (low exposures)
- Straight-line region (γ = contrast)
- Shoulder region (high exposures)
```

### Key Principles:

1. **Paper γ (Gamma) Variation**:
   - Each filter grade has different paper γ
   - Softer filters → lower γ → more exposure latitude
   - Harder filters → higher γ → less exposure latitude

2. **Contrast Matching**:

   ```
   Required paper γ = ΔD_negative / ΔlogE_available
   Choose filters that provide closest γ match
   ```

3. **Exposure Optimization**:

   ```
   Minimize: |D_highlight_target - D_highlight_achieved|² + |D_shadow_target - D_shadow_achieved|²
   Subject to: logE_total = log(E_soft + E_hard)
   ```

4. **Filter Selection**:
   - Not fixed to extremes
   - Based on contrast range and paper characteristics
   - May use intermediate grades for better control

## Mathematical Model Comparison

### Current Model (Simplistic):

```
E_soft = (C / L_highlight) × F_soft
E_hard = (C / L_shadow) × F_hard
E_total = E_soft + E_hard
```

### Heiland Model (Proposed):

```
Let:
  D_target_highlight = desired highlight density (e.g., 0.1 above paper base)
  D_target_shadow = desired shadow density (e.g., 1.8 above paper base)
  γ_soft = paper γ with soft filter
  γ_hard = paper γ with hard filter

Solve for E_soft, E_hard that minimize:
  J = |D_highlight_target - (γ_soft × logE_soft + γ_hard × logE_hard)|²
      + |D_shadow_target - (γ_soft × logE_soft + γ_hard × logE_hard)|²

With constraint: E_soft + E_hard ≤ E_max (paper maximum exposure)
```

## Practical Implications

### Test Case: High Contrast Negative (ΔEV = 4.0)

**Current Algorithm**:

- Highlight lux = 100, Shadow lux = 1600 (16× difference)
- Soft time = (1000/100) × 1.6 = 16.0s
- Hard time = (1000/1600) × 0.4 = 0.25s
- Total = 16.25s (mostly soft exposure)

**Problem**: Hard exposure is negligible, unlikely to affect shadows

**Heiland Approach (Expected)**:

- Would select less extreme filters (e.g., 0 and 4)
- Balance exposures more evenly
- Consider paper's ability to render extreme contrast

### Test Case: Low Contrast Negative (ΔEV = 1.0)

**Current Algorithm**:

- Highlight lux = 100, Shadow lux = 200 (2× difference)
- Soft time = (1000/100) × 1.6 = 16.0s
- Hard time = (1000/200) × 0.4 = 2.0s
- Total = 18.0s

**Problem**: Still uses extreme filters unnecessarily

**Heiland Approach (Expected)**:

- Might use closer filters (e.g., 1 and 3)
- Or recommend single-filter printing
- Optimize for tonal separation

## Algorithm Improvement Opportunities

### 1. Dynamic Filter Selection

```
Calculate required contrast compression:
  Required_compression = ΔEV_negative / Paper_latitude

Choose filters where:
  γ_soft provides highlight control
  γ_hard provides shadow control
  Combined γ covers required range
```

### 2. Sensitometric Exposure Calculation

```
Use paper D-logE curve to:
1. Convert lux readings to log exposure values
2. Apply filter γ adjustments
3. Solve for exposures that achieve target densities
4. Account for exposure additivity in density space
```

### 3. Calibration Enhancement

```
Store paper-specific:
- Base exposure constant
- Characteristic curve parameters (toe, γ, shoulder)
- Filter γ multipliers
- Maximum printable density range
```

## Implementation Strategy

### Phase 1: Research Validation

1. Find Heiland technical documentation
2. Interview Heiland users
3. Test current algorithm with real prints

### Phase 2: Algorithm Development

1. Implement paper curve modeling
2. Add dynamic filter selection
3. Create optimization solver

### Phase 3: Integration

1. Replace current split-grade calculator
2. Add paper calibration interface
3. Update METER tab UI

### Phase 4: Testing

1. Compare with current algorithm
2. Validate with test prints
3. Refine based on user feedback

## Next Steps

1. **Research Priority**: Find Heiland's actual algorithm
2. **Mathematical Development**: Create paper curve model
3. **Prototype Testing**: Implement and test improved algorithm
4. **User Interface**: Design calibration and calculation interface
