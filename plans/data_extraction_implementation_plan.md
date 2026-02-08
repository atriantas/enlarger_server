# Data Extraction and Implementation Plan for Split-Grade Analyzer Replacement

## Executive Summary

This plan outlines the steps to extract manufacturer data from Ilford and FOMA documentation and implement an improved split-grade algorithm that addresses the current limitations and provides Heiland-like functionality.

## Phase 1: Data Extraction and Analysis

### 1.1 Documentation Access and Review

#### 1.1.1 Ilford Documentation

**URLs to Access:**

1. https://www.ilfordphoto.com/amfile/file/download/file/1956/product/1696/
2. https://www.ilfordphoto.com/amfile/file/download/file/1824/product/1696/

**Expected Documents:**

- Multigrade technical datasheets
- Filter factor tables
- Paper characteristic curves
- ISO R/P values
- Exposure recommendations

**Extraction Tasks:**

1. Download PDF documents
2. Extract filter factor tables for grades 00-5
3. Extract ISO R values for each filter
4. Digitize paper characteristic curves (D-logE)
5. Extract paper speed (ISO P) data
6. Note any exposure latitude information

#### 1.1.2 FOMA Documentation

**URLs to Access:**

1. https://www.foma.cz/en/fomaspeed-variant
2. https://www.foma.cz/en/fomabrom-variant
3. https://www.foma.cz/en/fomatone-MG

**Expected Documents:**

- FOMASPEED Variant III technical data
- FOMABROM Variant technical data
- FOMATONE MG technical data
- Filter system specifications
- Paper sensitometric curves

**Extraction Tasks:**

1. Download technical datasheets
2. Extract filter data for 2xY, Y, M1, 2xM1, M2, 2xM2
3. Extract ISO R values for FOMA system
4. Digitize sensitometric curves
5. Note filter factor relationships

### 1.2 Data Processing and Validation

#### 1.2.1 Data Structure Creation

```python
# Proposed enhanced data structure
MANUFACTURER_DATA = {
    'ilford': {
        'multigrade_iv': {
            'paper_type': 'Multigrade IV RC',
            'base_iso_p': 100,
            'dmin': 0.05,
            'dmax': 2.10,
            'exposure_latitude': 1.8,
            'filters': {
                '00': {
                    'factor': 1.6,
                    'iso_r': 180,
                    'gamma': 0.4,
                    'contrast_index': 0.8,
                    'dmin_effect': 0.05,
                    'dmax_effect': 1.8
                },
                # ... other grades with extracted data
            },
            'characteristic_curve': {
                'toe_slope': 0.2,
                'straight_slope': 0.7,
                'shoulder_slope': 0.1,
                'logE_range': 1.8,
                'speed_point': 0.6
            }
        }
    },
    'foma': {
        'fomaspeed_variant_iii': {
            # ... similar structure with extracted data
        }
    }
}
```

#### 1.2.2 Data Validation Steps

1. **Cross-reference** extracted data with current implementation
2. **Verify consistency** with photographic principles
3. **Check unit conversions** (lux, seconds, EV, density)
4. **Validate mathematical relationships** (filter factors, ISO R progression)
5. **Test sample calculations** with extracted data

## Phase 2: Algorithm Design and Implementation

### 2.1 Dynamic Filter Selection Algorithm

#### 2.1.1 Core Logic

```python
def select_optimal_filters(delta_ev, paper_data, filter_system='ilford'):
    """
    Select optimal filter pair based on measured contrast.

    Parameters:
        delta_ev: Measured contrast in stops (0-5 typical)
        paper_data: Enhanced paper database entry
        filter_system: 'ilford' or 'foma'

    Returns:
        (soft_filter, hard_filter): Optimal filter pair
        selection_reason: Explanation of selection logic
    """

    # Algorithm steps:
    # 1. Determine paper's printable contrast range for each filter
    # 2. Map negative contrast (ΔEV) to required paper contrast
    # 3. Select filter pair that covers required range
    # 4. Optimize for balanced exposure times
    # 5. Return selection with reasoning

    # Implementation logic based on ΔEV:
    # ΔEV < 1.0: Low contrast -> Use closer filters (e.g., 1 & 2)
    # 1.0 ≤ ΔEV < 2.5: Normal contrast -> Standard split (e.g., 00 & 3)
    # 2.5 ≤ ΔEV < 4.0: High contrast -> Wider split (e.g., 00 & 4)
    # ΔEV ≥ 4.0: Very high contrast -> Extreme split (e.g., 00 & 5)

    pass
```

#### 2.1.2 Filter Selection Rules

Based on ΔEV measurements:

| ΔEV Range | Contrast Level | Recommended Filters (Ilford) | Recommended Filters (FOMA) |
| --------- | -------------- | ---------------------------- | -------------------------- |
| 0.0-1.0   | Very Low       | 1 & 2                        | Y & M1                     |
| 1.0-1.5   | Low            | 00 & 2                       | 2xY & M1                   |
| 1.5-2.0   | Medium-Low     | 00 & 3                       | 2xY & 2xM1                 |
| 2.0-2.5   | Normal         | 00 & 3                       | 2xY & 2xM1                 |
| 2.5-3.0   | Medium-High    | 00 & 4                       | 2xY & M2                   |
| 3.0-3.5   | High           | 00 & 4                       | 2xY & 2xM2                 |
| 3.5-4.0   | Very High      | 00 & 5                       | 2xY & 2xM2                 |
| 4.0+      | Extreme        | 00 & 5                       | 2xY & 2xM2                 |

### 2.2 Enhanced Exposure Calculation

#### 2.2.1 Mathematical Model

```python
def calculate_split_grade_enhanced(highlight_lux, shadow_lux, paper_id, filter_system='ilford'):
    """
    Enhanced split-grade calculation using paper characteristics.

    Uses manufacturer data to calculate exposures that consider:
    1. Paper characteristic curves (D-logE)
    2. Filter-specific gamma values
    3. Optimal tonal placement
    4. Balanced exposure times
    """

    # Step 1: Calculate ΔEV
    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)

    # Step 2: Select optimal filters based on ΔEV
    soft_filter, hard_filter = select_optimal_filters(delta_ev, paper_id, filter_system)

    # Step 3: Get filter data from manufacturer database
    soft_data = MANUFACTURER_DATA[filter_system][paper_id]['filters'][soft_filter]
    hard_data = MANUFACTURER_DATA[filter_system][paper_id]['filters'][hard_filter]

    # Step 4: Calculate base exposures using paper characteristics
    # Instead of simple linear calculation:
    # time = calibration / lux × filter_factor
    # Use paper response curve to determine optimal exposure

    # Step 5: Apply optimization for balanced exposures
    # Ensure neither exposure is too short or too long
    # Apply limits: min 2 seconds, max 120 seconds

    # Step 6: Return comprehensive results
    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': optimized_soft_time,
        'hard_time': optimized_hard_time,
        'total_time': total_time,
        'delta_ev': delta_ev,
        'selection_reason': selection_reason,
        'paper_used': paper_id,
        'optimization_applied': True
    }
```

#### 2.2.2 Optimization Criteria

1. **Exposure Balance**: Neither exposure should dominate (ratio 1:10 max)
2. **Minimum Exposure**: Each exposure ≥ 2 seconds for consistency
3. **Maximum Exposure**: Each exposure ≤ 120 seconds for practicality
4. **Tonal Placement**: Highlights at Dmin + 0.04, shadows at Dmax - 0.10
5. **Error Minimization**: Minimize density error from target values

### 2.3 Backward Compatibility

#### 2.3.1 Legacy Support

```python
def calculate_split_grade(highlight_lux, shadow_lux, calibration=None, system=None):
    """
    Maintain backward compatibility with existing code.

    Calls enhanced version with default paper selection.
    """
    # Use default paper based on filter system
    paper_id = get_default_paper_id(system)

    # Call enhanced calculation
    result = calculate_split_grade_enhanced(
        highlight_lux, shadow_lux, paper_id, system
    )

    # Format result to match existing structure
    return format_legacy_result(result)
```

#### 2.3.2 Migration Path

1. **Phase 1**: Add enhanced method alongside existing
2. **Phase 2**: Update UI to use enhanced method by default
3. **Phase 3**: Deprecate old method with warning
4. **Phase 4**: Remove old method after migration period

## Phase 3: Implementation Steps

### 3.1 File Structure Updates

#### 3.1.1 New Files to Create

```
lib/
├── paper_database.py          # Enhanced manufacturer data
├── splitgrade_enhanced.py     # New algorithm implementation
└── filter_selector.py         # Dynamic filter selection logic
```

#### 3.1.2 Updates to Existing Files

```
lib/light_sensor.py:
- Add import for enhanced modules
- Update calculate_split_grade() to use enhanced version
- Add new methods for paper database access
- Maintain backward compatibility
```

### 3.2 Code Implementation Sequence

#### Step 1: Create Paper Database Module

```python
# lib/paper_database.py
PAPER_DATABASE = {
    # Structure with extracted manufacturer data
}

def get_paper_data(paper_id):
    """Retrieve paper data from database."""
    pass

def validate_paper_data(paper_data):
    """Validate extracted manufacturer data."""
    pass
```

#### Step 2: Create Filter Selector Module

```python
# lib/filter_selector.py
def select_filters_by_contrast(delta_ev, paper_data, system='ilford'):
    """Select optimal filter pair based on contrast."""
    pass

def get_filter_recommendation(delta_ev, system='ilford'):
    """Get human-readable filter recommendation."""
    pass
```

#### Step 3: Create Enhanced Split-Grade Module

```python
# lib/splitgrade_enhanced.py
def calculate_enhanced_split_grade(highlight_lux, shadow_lux, paper_id, system='ilford'):
    """Enhanced calculation with manufacturer data."""
    pass

def optimize_exposure_times(soft_time, hard_time, paper_data):
    """Apply optimization rules for balanced exposures."""
    pass
```

#### Step 4: Update Light Sensor Module

```python
# lib/light_sensor.py
# Add imports
from lib.paper_database import PAPER_DATABASE, get_paper_data
from lib.filter_selector import select_filters_by_contrast
from lib.splitgrade_enhanced import calculate_enhanced_split_grade

# Update existing method
def calculate_split_grade(self, highlight_lux, shadow_lux, calibration=None, system=None):
    """Enhanced version with backward compatibility."""
    # Call enhanced calculation
    result = calculate_enhanced_split_grade(
        highlight_lux, shadow_lux,
        get_default_paper_id(system),
        system
    )
    return result
```

### 3.3 Testing Strategy

#### 3.3.1 Unit Tests

```python
# test_split_grade_enhanced.py
def test_dynamic_filter_selection():
    """Test filter selection based on ΔEV."""
    pass

def test_enhanced_exposure_calculation():
    """Test exposure calculation with manufacturer data."""
    pass

def test_backward_compatibility():
    """Ensure existing tests still pass."""
    pass
```

#### 3.3.2 Integration Tests

1. **Test with real lux values** from sensor
2. **Validate against manufacturer specifications**
3. **Compare with current algorithm results**
4. **Test edge cases** (very low/high contrast)

#### 3.3.3 User Testing

1. **Create test interface** for comparison
2. **Collect user feedback** on exposure times
3. **Adjust algorithm** based on practical results
4. **Validate with actual printing**

## Phase 4: UI Integration

### 4.1 METER Tab Updates

#### 4.1.1 Enhanced Interface

```html
<!-- index.html METER tab updates -->
<div class="split-grade-section">
  <h3>SPLIT-GRADE ANALYZER (Enhanced)</h3>

  <!-- Paper selection -->
  <div class="paper-selection">
    <label>Paper Type:</label>
    <select id="paper-type">
      <option value="ilford_mg_iv">Ilford Multigrade IV</option>
      <option value="foma_fomaspeed">FOMA FOMASPEED</option>
      <option value="foma_fomatone">FOMA FOMATONE</option>
    </select>
  </div>

  <!-- Algorithm selection -->
  <div class="algorithm-selection">
    <label>Algorithm:</label>
    <select id="algorithm-type">
      <option value="enhanced">Enhanced (Recommended)</option>
      <option value="legacy">Legacy (Original)</option>
    </select>
  </div>

  <!-- Results display -->
  <div class="results-enhanced">
    <div class="filter-selection">
      <strong>Selected Filters:</strong>
      <span id="soft-filter">00</span> (Soft) +
      <span id="hard-filter">5</span> (Hard)
      <div class="selection-reason" id="selection-reason">
        Based on measured contrast of 2.5 EV
      </div>
    </div>
    <!-- ... rest of results -->
  </div>
</div>
```

#### 4.1.2 Real-time Comparison

- **Show both algorithms** side by side
- **Highlight differences** in exposure times
- **Provide explanation** for improvements
- **Allow user switching** between algorithms

### 4.2 Calibration Interface

#### 4.2.1 Paper Calibration

```python
# New calibration interface
def calibrate_paper(paper_id, test_strip_results):
    """
    Calibrate paper using test strip results.

    Updates manufacturer data with user-specific calibration.
    """
    pass
```

#### 4.2.2 User Preferences

- **Save preferred papers**
- **Store custom calibrations**
- **Recall previous settings**
- **Export/import calibration data**

## Phase 5: Documentation and Deployment

### 5.1 Documentation Updates

#### 5.1.1 User Documentation

1. **Updated USER_MANUAL.md** with new features
2. **Algorithm explanation** for advanced users
3. **Calibration guide** for specific papers
4. **Troubleshooting** for common issues

#### 5.1.2 Technical Documentation

1. **Algorithm specification** with mathematical details
2. **Data structure documentation**
3. **API reference** for developers
4. **Testing methodology**

### 5.2 Deployment Strategy

#### 5.2.1 Staged Rollout

1. **Alpha**: Internal testing with simulated data
2. **Beta**: Limited user testing with feedback
3. **Release Candidate**: Full feature testing
4. **Production**: General availability

#### 5.2.2 Migration Support

1. **Automatic migration** of existing calibrations
2. **Fallback mechanism** to legacy algorithm
3. **User education** on new features
4. **Support channels** for questions

## Success Metrics

### 6.1 Technical Success Criteria

1. **Algorithm Accuracy**: Exposure times within ±10% of optimal
2. **Performance**: Calculation time < 100ms on Pico 2 W
3. **Memory Usage**: < 50KB additional memory
4. **Reliability**: No crashes or errors in normal use

### 6.2 User Success Criteria

1. **Usability**: Intuitive interface with clear results
2. **Accuracy**: Realistic exposure times matching darkroom experience
3. **Flexibility**: Support for multiple paper types
4. **Satisfaction**: Positive user feedback on improvements

### 6.3 Business Success Criteria

1. **Adoption**: >80% of users switch to enhanced algorithm
2. **Feedback**: Reduced support requests for split-grade issues
3. **Engagement**: Increased usage of split-grade feature
4. **Innovation**: Foundation for future advanced features

## Timeline and Resources

### 7.1 Estimated Effort

- **Phase 1 (Data Extraction)**: 2-3 days
- **Phase 2 (Algorithm Design)**: 3-4 days
- **Phase 3 (Implementation)**: 4-5 days
- **Phase 4 (UI Integration)**: 2-3 days
- **Phase 5 (Documentation)**: 1-2 days
- **Testing and Refinement**: 3-4 days

**Total**: 15-21 days of focused development

### 7.2 Resource Requirements

1. **Development**: Python/MicroPython expertise
2. **Testing**: Access to darkroom equipment for validation
3. **Documentation**: Technical writing skills
4. **User Testing**: Community of photographers for feedback

## Risks and Mitigations

### 8.1 Technical Risks

1. **Risk**: Manufacturer data incomplete or inconsistent
   **Mitigation**: Use multiple
