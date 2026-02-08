# Split-Grade Analyzer Research Summary

## Executive Summary

The current split-grade analyzer in the METER tab produces unrealistic exposure times that don't match darkroom experience. This research investigates the Heiland Splitgrade Controller methodology to develop an improved algorithm that better aligns with sensitometric principles and practical printing results.

## 1. Current System Analysis

### 1.1 Implementation Overview

- **Location**: `lib/light_sensor.py`, `DarkroomLightMeter` class
- **Algorithm**: Simple additive model with fixed extreme filters
- **Input**: Highlight and shadow lux readings
- **Output**: Soft/hard exposure times

### 1.2 Identified Issues

1. **Unrealistic Exposure Times**: Especially for high/low contrast negatives
2. **Fixed Filter Selection**: Always uses Grade 00 and 5 (extremes)
3. **Oversimplified Model**: Ignores paper characteristic curve
4. **Linear Assumption**: Assumes paper response linear with exposure
5. **No Optimization**: No attempt to optimize tonal placement

## 2. Heiland Splitgrade Controller Research

### 2.1 Key Principles (Hypothesized)

1. **Sensitometric Foundation**: Based on paper D-logE curves
2. **Dynamic Filter Selection**: Chooses optimal filter pair based on contrast
3. **Exposure Optimization**: Minimizes density error for highlights/shadows
4. **Paper Characterization**: Requires calibration data

### 2.2 Mathematical Model

- **Paper Response**: `D = f(log E)` where f() is characteristic curve
- **Filter Effect**: Each grade has specific paper γ (contrast)
- **Optimization**: Minimize `|D_target - D_achieved|²` for highlights/shadows
- **Constraint**: Total exposure within paper latitude

## 3. Algorithm Comparison

### 3.1 Current Algorithm

```
E_soft = (C / L_highlight) × F_00
E_hard = (C / L_shadow) × F_5
E_total = E_soft + E_hard
```

### 3.2 Heiland Approach (Estimated)

```
1. Calculate required contrast: ΔD_negative
2. Choose filters g_soft, g_hard to match paper γ
3. Solve optimization: min |D_target - (γ_soft×logE_soft + γ_hard×logE_hard)|²
4. Apply constraints: E_soft + E_hard ≤ E_max
```

### 3.3 Key Differences

| Aspect                 | Current         | Heiland                     |
| ---------------------- | --------------- | --------------------------- |
| **Mathematical Basis** | Linear exposure | Log-linear density          |
| **Filter Selection**   | Fixed (00, 5)   | Dynamic based on contrast   |
| **Optimization**       | None            | Density error minimization  |
| **Paper Model**        | Ignored         | Characteristic curve        |
| **Calibration**        | Single constant | Full paper characterization |

## 4. Test Case Analysis

### 4.1 High Contrast Negative (ΔEV = 4.0)

- **Current**: E_soft = 16.0s, E_hard = 0.25s (unbalanced)
- **Expected**: More balanced exposures (e.g., 12s + 2s)

### 4.2 Low Contrast Negative (ΔEV = 1.0)

- **Current**: Still uses extreme filters unnecessarily
- **Expected**: Closer filters or single-filter recommendation

## 5. Proposed Improvements

### 5.1 Phase 1: Dynamic Filter Selection

- Replace fixed filters (00, 5) with contrast-based selection
- Implement filter selection table based on ΔEV
- Add intermediate filter options

### 5.2 Phase 2: Sensitometric Enhancement

- Incorporate paper γ values
- Use density-space additivity instead of exposure-space
- Add paper calibration interface

### 5.3 Phase 3: Optimization Algorithm

- Implement simplified optimization
- Add highlight/shadow density targets
- Include paper latitude constraints

## 6. Implementation Considerations

### 6.1 Resource Constraints (Pico 2 W)

- Limited memory and processing power
- Need for efficient algorithms
- Pre-computed tables where possible

### 6.2 User Experience

- Maintain simple calibration process
- Clear feedback on calculations
- Option to override automatic selections

### 6.3 Backward Compatibility

- Support existing calibration data
- Fallback to current algorithm if needed
- Gradual migration path

## 7. Research Gaps

### 7.1 Heiland-Specific Information Needed

1. Actual algorithm documentation
2. Filter selection logic details
3. Paper database structure
4. Calibration procedures

### 7.2 Sensitometric Data Needed

1. Paper γ values for common papers
2. Characteristic curve parameters
3. Filter grade effects on paper response
4. Additivity principles for split-grade

## 8. Next Steps

### 8.1 Immediate Actions

1. **Research**: Find Heiland technical documentation
2. **Prototype**: Implement dynamic filter selection
3. **Testing**: Compare algorithms with test cases

### 8.2 Medium-Term Goals

1. **Algorithm Development**: Create improved calculation model
2. **UI Enhancement**: Update METER tab interface
3. **Calibration System**: Add paper characterization

### 8.3 Long-Term Vision

1. **Full Optimization**: Implement Heiland-like algorithm
2. **Paper Database**: Store multiple paper profiles
3. **Advanced Features**: Local contrast control, burn/dodge guidance

## 9. Recommendations

### 9.1 Short-Term Fix

Implement dynamic filter selection based on ΔEV:

- Low contrast (ΔEV < 1.5): Use closer filters (e.g., 1 and 3)
- Moderate contrast (1.5 ≤ ΔEV ≤ 3.0): Use standard split (00 and 5)
- High contrast (ΔEV > 3.0): Consider alternative approaches

### 9.2 Medium-Term Solution

Develop simplified sensitometric model:

- Use paper γ values from literature
- Implement density-space calculation
- Add basic optimization

### 9.3 Long-Term Solution

Research and implement Heiland-equivalent algorithm:

- Full paper characterization
- Advanced optimization
- Professional-grade results

## 10. Conclusion

The current split-grade analyzer has fundamental limitations due to its oversimplified mathematical model. By researching the Heiland Splitgrade Controller approach and incorporating sensitometric principles, we can develop a significantly improved tool that produces more realistic and practical exposure times for split-grade printing.

**Priority Recommendation**: Start with Phase 1 (dynamic filter selection) as it provides immediate improvement with minimal complexity, while continuing research on the full Heiland methodology for future enhancements.
