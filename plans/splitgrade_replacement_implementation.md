# Split-Grade Analyzer Replacement Implementation Plan

## Project Overview

**Goal**: Replace the current split-grade analyzer in the METER tab with an improved algorithm based on Heiland Splitgrade Controller principles and sensitometric foundations.

**Problem**: Current tool produces unrealistic exposure times that don't match darkroom experience.

**Solution**: Implement phased improvements starting with dynamic filter selection and progressing to full sensitometric optimization.

## 1. Implementation Strategy

### 1.1 Phased Approach

#### Phase 1: Dynamic Filter Selection (Weeks 1-2)

- Replace fixed filters (00, 5) with contrast-based selection
- Minimal risk, immediate improvement
- Backward compatible

#### Phase 2: Enhanced Calculation (Weeks 3-4)

- Incorporate paper γ values
- Density-space additivity
- Basic optimization

#### Phase 3: Advanced Features (Weeks 5-8)

- Full Heiland-like algorithm (after research)
- Paper calibration system
- Advanced user controls

### 1.2 Risk Mitigation

- Maintain legacy algorithm as fallback
- Gradual rollout with user testing
- Configuration options for algorithm selection

## 2. Phase 1: Dynamic Filter Selection

### 2.1 Technical Specifications

#### Files to Modify:

1. `lib/light_sensor.py` - Core algorithm
2. `index.html` - METER tab UI
3. Test files - Validation

#### Algorithm Changes:

```python
# Current (simplified):
soft_filter = '00'
hard_filter = '5'

# New:
def select_filters_based_on_contrast(ΔEV, filter_system):
    if filter_system == 'ilford':
        if ΔEV < 1.0:
            return '1', '3'   # Very low contrast
        elif ΔEV < 1.5:
            return '0', '4'   # Low contrast
        elif ΔEV < 2.5:
            return '00', '5'  # Normal contrast
        else:
            return '00', '5'  # High contrast (with adjustments)
```

### 2.2 UI Updates

#### Current METER Tab:

```
SPLIT-GRADE ANALYZER
[Calculate Split-Grade]
Soft: Grade 00 - X.Xs
Hard: Grade 5 - X.Xs
```

#### Enhanced METER Tab:

```
ADVANCED SPLIT-GRADE CALCULATOR
Contrast: ΔEV X.X (Description)
[Calculate Split-Grade]
Soft: Grade XX - X.Xs (X%)
Hard: Grade XX - X.Xs (X%)
Total: X.Xs

[Advanced Options] → Filter override, algorithm selection
```

### 2.3 Implementation Steps

#### Step 1: Algorithm Update (light_sensor.py)

1. Create `calculate_split_grade_v2()` method
2. Implement dynamic filter selection tables
3. Add contrast adjustment factors
4. Maintain `calculate_split_grade()` for compatibility

#### Step 2: UI Integration (index.html)

1. Update METER tab to show selected filters
2. Add contrast display and description
3. Add advanced options toggle
4. Update JavaScript to use new endpoint

#### Step 3: Backend Integration (http_server.py)

1. Add new endpoint `/light-meter-split-grade-v2`
2. Call new algorithm method
3. Return enhanced response format

#### Step 4: Testing

1. Update `test_split_grade.py`
2. Add test cases for different contrast ranges
3. Validate mathematical consistency
4. User interface testing

## 3. Phase 2: Enhanced Calculation

### 3.1 Technical Specifications

#### Paper γ Data Structure:

```python
PAPER_γ_VALUES = {
    'ilford_mg_iv': {
        '00': 0.4, '0': 0.5, '1': 0.6, '2': 0.7,
        '3': 0.9, '4': 1.1, '5': 1.3
    },
    'foma_fomaspeed': {
        '2xY': 0.4, 'Y': 0.5, '': 0.6, 'M1': 0.8,
        '2xM1': 1.0, 'M2': 1.2, '2xM2': 1.4
    }
}
```

#### Enhanced Algorithm:

```python
def calculate_split_grade_enhanced(highlight_lux, shadow_lux,
                                   calibration, paper_type='ilford_mg_iv'):
    # 1. Calculate ΔEV
    ΔEV = calculate_delta_ev(highlight_lux, shadow_lux)

    # 2. Select filters based on ΔEV
    soft_filter, hard_filter = select_filters(ΔEV, paper_type)

    # 3. Get paper γ values
    γ_soft = PAPER_γ_VALUES[paper_type][soft_filter]
    γ_hard = PAPER_γ_VALUES[paper_type][hard_filter]

    # 4. Calculate in density space
    logE_highlight = math.log10(calibration / highlight_lux)
    logE_shadow = math.log10(calibration / shadow_lux)

    # 5. Optimize exposures (simplified)
    soft_time, hard_time = optimize_exposures(
        logE_highlight, logE_shadow, γ_soft, γ_hard
    )

    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'delta_ev': ΔEV,
        'paper_type': paper_type,
        'algorithm_version': 'enhanced_v2'
    }
```

### 3.2 Implementation Steps

#### Step 1: Paper Database

1. Create paper database structure
2. Add common paper types (Ilford MG IV, FOMA, etc.)
3. Implement paper selection in UI

#### Step 2: Density-Space Calculation

1. Implement log exposure conversion
2. Add γ-based calculation
3. Create optimization function

#### Step 3: Calibration Interface

1. Add paper calibration section
2. Implement calibration storage
3. Add custom paper profiles

#### Step 4: Advanced UI

1. Paper type selection dropdown
2. γ value display (advanced mode)
3. Calibration controls

## 4. Phase 3: Advanced Features

### 4.1 Research-Dependent Features

1. **Heiland Algorithm**: Requires detailed documentation
2. **Full Optimization**: Advanced mathematical solver
3. **Paper Characterization**: Complete D-logE curve modeling

### 4.2 Implementation Timeline

- **Research Phase**: 2-4 weeks (concurrent with Phase 2)
- **Algorithm Development**: 2-3 weeks
- **Integration**: 1-2 weeks
- **Testing**: 1-2 weeks

## 5. Testing Plan

### 5.1 Unit Tests

```python
# Test dynamic filter selection
def test_filter_selection():
    assert select_filters(0.5, 'ilford') == ('1', '3')
    assert select_filters(2.0, 'ilford') == ('00', '5')
    assert select_filters(4.0, 'ilford') == ('00', '5')  # with adjustment

# Test enhanced calculation
def test_enhanced_calculation():
    result = calculate_split_grade_enhanced(100, 400, 1000)
    assert result['soft_time'] > 0
    assert result['hard_time'] > 0
    assert result['soft_time'] + result['hard_time'] < 60  # Reasonable total
```

### 5.2 Integration Tests

1. End-to-end workflow: Measurement → Calculation → Display
2. UI responsiveness and updates
3. Error handling and edge cases

### 5.3 User Acceptance Testing

1. Compare with current algorithm using test negatives
2. Gather feedback from darkroom practitioners
3. Adjust algorithm based on real-world results

## 6. Deployment Strategy

### 6.1 Version Management

```
Algorithm Versions:
- v1.0: Current (legacy)
- v1.1: Dynamic filter selection (Phase 1)
- v2.0: Enhanced calculation (Phase 2)
- v3.0: Advanced features (Phase 3)
```

### 6.2 Configuration Options

```javascript
// User settings
splitGradeAlgorithm: {
  version: 'v1.1',  // or 'v1.0', 'v2.0', 'v3.0'
  paperType: 'ilford_mg_iv',
  showAdvanced: false,
  autoSelectFilters: true
}
```

### 6.3 Migration Path

1. **Initial Release**: v1.1 as default, v1.0 available
2. **Stable Release**: v2.0 as default after testing
3. **Advanced Release**: v3.0 as optional advanced feature

## 7. Resource Requirements

### 7.1 Development Resources

- **Primary Developer**: 1 person (4-8 weeks)
- **Testing**: 1 person (2-4 weeks)
- **Research**: Part-time (concurrent)

### 7.2 Technical Resources

- **Pico 2 W**: Sufficient for all phases
- **Storage**: Additional ~10KB for paper database
- **Processing**: Minimal increase for Phases 1-2

### 7.3 External Dependencies

- **Research Materials**: Heiland documentation, sensitometric data
- **Testing Equipment**: Light meter, test negatives, darkroom access
- **User Feedback**: Darkroom practitioner community

## 8. Success Metrics

### 8.1 Technical Metrics

- Algorithm produces realistic exposure times (0.5-60s range)
- Filter selection appropriate for contrast range
- Calculation time < 100ms on Pico 2 W
- Memory usage increase < 5KB

### 8.2 User Experience Metrics

- Users report more realistic results
- Reduced need for manual adjustments
- Positive feedback on new features
- Adoption rate of new algorithm

### 8.3 Quality Metrics

- All unit tests pass
- No regression in existing functionality
- Error rate < 1% for valid inputs
- Graceful degradation for edge cases

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk                           | Probability | Impact | Mitigation                          |
| ------------------------------ | ----------- | ------ | ----------------------------------- |
| Algorithm too complex for Pico | Low         | High   | Phased approach, optimization       |
| Paper γ data inaccurate        | Medium      | Medium | User calibration, adjustable values |
| Performance degradation        | Low         | Medium | Profiling, optimization             |

### 9.2 User Experience Risks

| Risk                                 | Probability | Impact | Mitigation                           |
| ------------------------------------ | ----------- | ------ | ------------------------------------ |
| Users confused by changes            | Medium      | Medium | Gradual rollout, clear documentation |
| New algorithm produces worse results | Low         | High   | A/B testing, fallback option         |
| Calibration too complex              | Medium      | Medium | Simplified calibration, defaults     |

## 10. Timeline

### 10.1 Phase 1: Dynamic Filter Selection

- **Week 1**: Algorithm development and unit tests
- **Week 2**: UI integration and testing
- **Week 2-end**: Release v1.1

### 10.2 Phase 2: Enhanced Calculation

- **Week 3**: Paper database and γ implementation
- **Week 4**: Density-space calculation and optimization
- **Week 4-end**: Release v2.0 beta

### 10.3 Phase 3: Advanced Features

- **Weeks 5-6**: Research and algorithm development
- **Week 7**: Integration and testing
- **Week 8**: Release v3.0 (optional)

## 11. Conclusion

This implementation plan provides a structured approach to replacing the split-grade analyzer with an improved tool that addresses the core issue of unrealistic exposure times. By starting with dynamic filter selection (Phase 1), we can deliver immediate improvements while laying the foundation for more advanced sensitometric features in later phases.

**Recommended Next Step**: Begin Phase 1 implementation with the dynamic filter selection algorithm, as it provides the best balance of improvement value, implementation risk, and user benefit.
