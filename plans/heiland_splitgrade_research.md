# Heiland Splitgrade Controller Research

## Current System Analysis

### Current Split-Grade Implementation (from light_sensor.py)

The current system uses the following algorithm:

1. **ΔEV Calculation**: `ΔEV = abs(log₂(shadow_lux / highlight_lux))`
2. **Base Exposure Time**: `base_time = calibration_constant / lux`
3. **Filter Factors**: Predefined factors for Ilford/Foma filters
4. **Split-Grade Calculation**:
   - Soft filter: Always Grade 00 (Ilford) or 2xY (Foma)
   - Hard filter: Always Grade 5 (Ilford) or 2xM2 (Foma)
   - Soft time: `(calibration / highlight_lux) × soft_factor`
   - Hard time: `(calibration / shadow_lux) × hard_factor`
   - Total time: `soft_time + hard_time`

### Potential Issues Identified:

1. **Fixed Filter Selection**: Always uses extremes (00 and 5) regardless of contrast
2. **Simple Additive Model**: Assumes exposures are purely additive
3. **No Sensitometric Curve Consideration**: Doesn't account for paper D-logE curve
4. **No Highlight/Shadow Compression**: Linear calculation may not match paper response

## Heiland Splitgrade Controller Research

### Overview

The Heiland Splitgrade Controller is a professional darkroom exposure computer that uses advanced sensitometric principles for split-grade printing. Key features:

1. **Dual-Channel Measurement**: Measures highlight and shadow densities
2. **Paper Curve Analysis**: Incorporates paper's characteristic curve
3. **Dynamic Filter Selection**: Chooses optimal filter pair based on contrast
4. **Exposure Optimization**: Calculates exposures for optimal tonal separation

### Key Principles (Based on Available Documentation):

1. **Sensitometric Basis**:
   - Uses paper's D-logE (density vs log exposure) curve
   - Accounts for toe, straight-line, and shoulder regions
   - Considers paper ISO R (exposure latitude)

2. **Filter Selection Algorithm**:
   - Not fixed to extremes (00 and 5)
   - Selects filters based on required contrast compression/expansion
   - May use intermediate grades for better tonal control

3. **Exposure Calculation**:
   - Not simple additive model
   - Conserves highlight and shadow detail
   - May use proportional or weighted exposures

4. **Calibration Approach**:
   - Requires paper calibration for accurate results
   - Stores paper-specific sensitometric data
   - Accounts for developer effects

### Mathematical Model Hypotheses:

Based on sensitometric principles, Heiland likely uses:

1. **Paper Characteristic Curve Modeling**:

   ```
   D = f(log E) where f is the paper's response function
   ```

2. **Contrast Matching**:

   ```
   Required contrast = ΔD_negative / Paper_γ
   Where Paper_γ varies with filter grade
   ```

3. **Exposure Optimization**:

   ```
   Minimize: |D_target - D_achieved| for highlights and shadows
   Subject to: Total exposure = E_soft + E_hard
   ```

4. **Filter Grade Selection**:
   ```
   Choose grades that minimize contrast mismatch
   While maintaining printable density range
   ```

## Comparison: Current vs. Heiland Approach

| Aspect                | Current Implementation | Heiland (Hypothesized)       |
| --------------------- | ---------------------- | ---------------------------- |
| **Filter Selection**  | Fixed (00 and 5)       | Dynamic based on contrast    |
| **Exposure Model**    | Simple additive        | Sensitometric optimization   |
| **Paper Curve**       | Ignored                | Incorporated via calibration |
| **Contrast Handling** | Linear ΔEV calculation | Paper γ consideration        |
| **Calibration**       | Single constant        | Full paper characterization  |

## Research Questions for Further Investigation:

1. **Heiland's Exact Algorithm**: How does it actually calculate exposures?
2. **Filter Selection Logic**: What criteria determine soft/hard filter grades?
3. **Paper Database**: Does it store paper-specific sensitometric data?
4. **Mathematical Model**: What optimization function does it use?
5. **User Experience**: How do professionals use it in practice?

## Next Steps:

1. Search for Heiland technical documentation
2. Analyze user manuals and forum discussions
3. Contact Heiland users for practical insights
4. Develop test scenarios to compare approaches
5. Create improved algorithm based on findings

## References Needed:

- Heiland Splitgrade Controller user manual
- Technical papers on sensitometric split-grade printing
- Photographic science literature on paper characteristic curves
- User experiences and calibration procedures
