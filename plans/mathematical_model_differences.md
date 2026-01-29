# Mathematical Model Differences: Current vs. Heiland Split-Grade

## 1. Current Mathematical Model

### 1.1 Core Equations

```
ΔEV = log₂(L_shadow / L_highlight)                    (1)
E_base_highlight = C / L_highlight                    (2)
E_base_shadow = C / L_shadow                          (3)
E_soft = E_base_highlight × F_soft                    (4)
E_hard = E_base_shadow × F_hard                       (5)
E_total = E_soft + E_hard                             (6)
```

Where:

- `L_highlight`, `L_shadow`: Lux readings
- `C`: Calibration constant (lux·seconds)
- `F_soft`, `F_hard`: Filter factors (e.g., 1.6 for 00, 0.4 for 5)
- `E_soft`, `E_hard`: Exposure times

### 1.2 Assumptions

1. **Linearity**: Paper response linear with exposure (ignores D-logE curve)
2. **Additivity**: Total density = density_soft + density_hard
3. **Independence**: Soft filter affects only highlights, hard only shadows
4. **Fixed Factors**: Filter factors constant regardless of contrast

### 1.3 Limitations

- No paper characteristic curve consideration
- Extreme filters always used
- No optimization for tonal placement
- Unrealistic for high/low contrast extremes

## 2. Heiland Mathematical Model (Reconstructed)

### 2.1 Sensitometric Foundation

#### Paper Characteristic Curve

```
D = f(log E)                                          (7)
```

Where `f()` is typically piecewise:

```
f(log E) =
  D_min                          for log E < log E_toe
  D_min + γ × (log E - log E_toe) for log E_toe ≤ log E ≤ log E_shoulder
  D_max                          for log E > log E_shoulder
```

#### Filter Grade Effect

Each filter grade `g` has:

- Paper γ_g (contrast)
- Effective speed factor S_g
- Printable density range ΔD_g

### 2.2 Contrast Matching

#### Negative Contrast

```
ΔD_negative = D_shadow - D_highlight                  (8)
ΔlogE_negative = log E_shadow - log E_highlight       (9)
```

#### Required Paper γ

```
γ_required = ΔD_negative / ΔlogE_available            (10)
```

Where `ΔlogE_available` is paper's printable log exposure range.

### 2.3 Filter Selection

#### Optimization Problem

Choose soft/hard filters (g_soft, g_hard) to:

```
Minimize: |γ_required - (w_soft × γ_soft + w_hard × γ_hard)|   (11)
Subject to: ΔD_soft + ΔD_hard ≥ ΔD_negative                    (12)
```

Where `w_soft`, `w_hard` are exposure weighting factors.

### 2.4 Exposure Calculation

#### Density Targets

```
D_highlight_target = D_min + δ_highlight              (13)
D_shadow_target = D_max - δ_shadow                    (14)
```

Where `δ_highlight`, `δ_shadow` are safety margins.

#### Exposure Optimization

Solve for `E_soft`, `E_hard`:

```
Minimize: J = |D_highlight_target - D_highlight_achieved|²
            + |D_shadow_target - D_shadow_achieved|²           (15)
Where:
  D_highlight_achieved = γ_soft × log E_soft + γ_hard × log E_hard
  D_shadow_achieved = γ_soft × log E_soft + γ_hard × log E_hard + ΔD_negative
```

#### Constraint

```
E_soft + E_hard ≤ E_max (paper maximum exposure)               (16)
```

## 3. Key Mathematical Differences

### 3.1 Linearity vs. Log-Linearity

| Aspect         | Current           | Heiland                 |
| -------------- | ----------------- | ----------------------- |
| **Response**   | Linear: D ∝ E     | Log-linear: D ∝ log E   |
| **Additivity** | In exposure space | In density space        |
| **Contrast**   | ΔEV (log ratio)   | ΔD (density difference) |

### 3.2 Filter Factor Application

```
Current: E_filtered = E_base × F_filter
Heiland: γ_effective = w_soft × γ_soft + w_hard × γ_hard
```

### 3.3 Optimization Approach

```
Current: No optimization, fixed formula
Heiland: Minimize density error with constraints
```

### 3.4 Contrast Handling

```
Current: Simple ΔEV, fixed filter response
Heiland: Match negative contrast to paper γ
```

## 4. Practical Examples

### Example 1: Moderate Contrast (ΔEV = 2.0)

**Current**:

```
L_highlight = 100, L_shadow = 400
E_soft = (1000/100) × 1.6 = 16.0s
E_hard = (1000/400) × 0.4 = 1.0s
Total = 17.0s
```

**Heiland (Estimated)**:

```
ΔD_negative ≈ 0.6 (assuming typical negative)
Choose filters: 1 (γ=0.6) and 4 (γ=1.2)
E_soft ≈ 8.0s, E_hard ≈ 4.0s (balanced)
Total ≈ 12.0s
```

### Example 2: High Contrast (ΔEV = 4.0)

**Current**:

```
L_highlight = 100, L_shadow = 1600
E_soft = 16.0s, E_hard = 0.25s
Total = 16.25s (hard exposure negligible)
```

**Heiland (Estimated)**:

```
ΔD_negative ≈ 1.2
Choose filters: 00 (γ=0.4) and 5 (γ=1.6)
E_soft ≈ 12.0s, E_hard ≈ 2.0s
Total ≈ 14.0s (more balanced)
```

## 5. Implementation Implications

### 5.1 Data Requirements

**Current**: Single calibration constant
**Heiland**: Paper characteristic curve parameters:

- `D_min`, `D_max`
- `γ_g` for each filter grade
- `log E_toe`, `log E_shoulder`
- Speed factors `S_g`

### 5.2 Computational Complexity

**Current**: Simple arithmetic (O(1))
**Heiland**: Optimization problem (may require iterative solver)

### 5.3 Calibration Process

**Current**: Measure one proper exposure
**Heiland**: Full paper characterization with test strips

### 5.4 User Interface

**Current**: Simple lux input
**Heiland**: May require paper selection, calibration data

## 6. Proposed Hybrid Approach

Given implementation constraints on Pico 2 W, consider:

### 6.1 Simplified Heiland Model

```
1. Use paper γ values from literature
2. Linear approximation of D-logE curve
3. Pre-computed filter selection table
4. Closed-form exposure calculation
```

### 6.2 Enhanced Current Model

```
1. Dynamic filter selection based on ΔEV
2. Paper γ consideration in exposure calculation
3. Additive model in density space
4. Calibration for paper type
```

### 6.3 Implementation Priority

1. **Phase 1**: Dynamic filter selection
2. **Phase 2**: Paper γ consideration
3. **Phase 3**: Density-space additivity
4. **Phase 4**: Full optimization (if resources allow)

## 7. Next Steps for Mathematical Development

1. **Research**: Find actual Heiland algorithm or similar systems
2. **Data Collection**: Gather paper γ values for common papers
3. **Prototype**: Implement simplified model
4. **Testing**: Compare with current algorithm using test cases
5. **Refinement**: Adjust based on practical results
