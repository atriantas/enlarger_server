# Current Filter Data Analysis and Manufacturer Data Requirements

## Current Filter Data Structure

Based on analysis of [`lib/light_sensor.py`](lib/light_sensor.py:525), the current implementation uses the following filter data:

### 1. Ilford Multigrade Filters (Lines 526-536)

```python
ILFORD_FILTERS = {
    '00': {'iso_r': 180, 'factor': 1.6, 'name': 'Grade 00'},
    '0':  {'iso_r': 160, 'factor': 1.4, 'name': 'Grade 0'},
    '1':  {'iso_r': 130, 'factor': 1.3, 'name': 'Grade 1'},
    '2':  {'iso_r': 110, 'factor': 1.1, 'name': 'Grade 2'},
    '3':  {'iso_r': 90,  'factor': 0.9, 'name': 'Grade 3'},
    '4':  {'iso_r': 60,  'factor': 0.6, 'name': 'Grade 4'},
    '5':  {'iso_r': 40,  'factor': 0.4, 'name': 'Grade 5'},
    '':   {'iso_r': 110, 'factor': 1.0, 'name': 'No Filter'},
    'none': {'iso_r': 110, 'factor': 1.0, 'name': 'No Filter'}
}
```

### 2. FOMA FOMASPEED Filters (Lines 540-549)

```python
FOMA_FOMASPEED_FILTERS = {
    '2xY':  {'iso_r': 135, 'factor': 1.6, 'name': '2×Y (Soft)'},
    'Y':    {'iso_r': 120, 'factor': 1.4, 'name': 'Y'},
    '':     {'iso_r': 105, 'factor': 1.0, 'name': 'No Filter'},
    'none': {'iso_r': 105, 'factor': 1.0, 'name': 'No Filter'},
    'M1':   {'iso_r': 90,  'factor': 1.4, 'name': 'M1'},
    '2xM1': {'iso_r': 80,  'factor': 2.1, 'name': '2×M1'},
    'M2':   {'iso_r': 65,  'factor': 2.6, 'name': 'M2'},
    '2xM2': {'iso_r': 55,  'factor': 4.6, 'name': '2×M2 (Hard)'}
}
```

### 3. FOMA FOMATONE Filters (Lines 553-562)

```python
FOMA_FOMATONE_FILTERS = {
    '2xY':  {'iso_r': 120, 'factor': 2.0, 'name': '2×Y (Soft)'},
    'Y':    {'iso_r': 105, 'factor': 1.5, 'name': 'Y'},
    '':     {'iso_r': 90,  'factor': 1.0, 'name': 'No Filter'},
    'none': {'iso_r': 90,  'factor': 1.0, 'name': 'No Filter'},
    'M1':   {'iso_r': 80,  'factor': 1.5, 'name': 'M1'},
    '2xM1': {'iso_r': 75,  'factor': 1.8, 'name': '2×M1'},
    'M2':   {'iso_r': 65,  'factor': 2.0, 'name': 'M2'},
    '2xM2': {'iso_r': 55,  'factor': 3.0, 'name': '2×M2 (Hard)'}
}
```

## Current Algorithm Limitations

### 1. Fixed Filter Selection (Lines 825-834)

```python
if system == 'ilford':
    soft_filter = '00'  # Always Grade 00
    hard_filter = '5'   # Always Grade 5
elif system == 'foma_fomaspeed':
    soft_filter = '2xY'  # Always 2×Y
    hard_filter = '2xM2' # Always 2×M2
else:  # foma_fomatone
    soft_filter = '2xY'  # Always 2×Y
    hard_filter = '2xM2' # Always 2×M2
```

**Problem**: Uses extreme filters regardless of contrast, leading to unrealistic exposure times.

### 2. Simple Linear Calculation (Lines 841-846)

```python
soft_base_time = cal / highlight_lux
hard_base_time = cal / shadow_lux
soft_time = soft_base_time * soft_factor
hard_time = hard_base_time * hard_factor
```

**Problem**: Ignores paper characteristic curves and assumes linear response.

## Missing Data for Heiland-like Algorithm

### 1. Paper Characteristic Data (D-logE Curves)

**Current**: None
**Required for Heiland**:

- Base + fog density (Dmin)
- Maximum density (Dmax)
- Gamma (γ) for each filter grade
- Toe and shoulder characteristics
- Log exposure range (ΔlogE)

### 2. Paper Speed Data

**Current**: Only ISO R values
**Required for Heiland**:

- ISO P values (paper speed)
- Exposure latitude
- Speed point (0.6 above Dmin)

### 3. Filter Performance Data

**Current**: Only filter factors and ISO R
**Required for Heiland**:

- Spectral transmission curves
- Contrast index (CI) for each filter
- Filter factor vs. paper type relationship
- Recommended filter combinations

### 4. Optimization Parameters

**Current**: None
**Required for Heiland**:

- Target densities for highlights and shadows
- Acceptable density error tolerance
- Weighting factors for highlight vs shadow
- Optimization criteria (minimize error, maximize tonal separation)

## Manufacturer Documentation Analysis Plan

### 1. Ilford Documentation URLs

1. https://www.ilfordphoto.com/amfile/file/download/file/1956/product/1696/
2. https://www.ilfordphoto.com/amfile/file/download/file/1824/product/1696/

**Expected Content**:

- Multigrade technical datasheets
- Filter factor tables
- Paper characteristic curves
- ISO R/P values
- Exposure recommendations

### 2. FOMA Documentation URLs

1. https://www.foma.cz/en/fomaspeed-variant
2. https://www.foma.cz/en/fomabrom-variant
3. https://www.foma.cz/en/fomatone-MG

**Expected Content**:

- FOMASPEED Variant III technical data
- FOMABROM Variant technical data
- FOMATONE MG technical data
- Filter system specifications
- Paper sensitometric curves

## Data Extraction Requirements

### 1. Quantitative Data to Extract

```
1. Filter Factors:
   - For each filter grade (Ilford: 00-5, FOMA: 2xY-2xM2)
   - At different wavelengths if available

2. ISO Values:
   - ISO R (printing speed) for each filter
   - ISO P (paper speed) if available
   - Exposure latitude in stops

3. Paper Characteristics:
   - Dmin, Dmax for each grade
   - Gamma (γ) for each filter grade
   - Log exposure range (ΔlogE)
   - Toe and shoulder parameters

4. Spectral Data:
   - Filter transmission curves
   - Paper spectral sensitivity
   - Recommended light sources
```

### 2. Qualitative Data to Extract

```
1. Usage Recommendations:
   - Recommended filter combinations
   - Exposure adjustment guidelines
   - Development recommendations

2. System Specifications:
   - Filter numbering system
   - Compatibility information
   - Historical context

3. Calibration Procedures:
   - Test strip recommendations
   - Calibration methods
   - Quality control procedures
```

## Enhanced Data Structure Proposal

### 1. Paper Database Structure

```python
PAPER_DATABASE = {
    'ilford_mg_iv': {
        'manufacturer': 'Ilford',
        'paper_type': 'Multigrade IV RC',
        'base_speed': 100,  # ISO P
        'dmin': 0.05,
        'dmax': 2.10,
        'exposure_latitude': 1.8,  # stops
        'filters': {
            '00': {
                'factor': 1.6,
                'iso_r': 180,
                'gamma': 0.4,
                'ci': 0.8,  # Contrast Index
                'dmin': 0.05,
                'dmax': 1.8
            },
            # ... other grades
        },
        'characteristic_curve': {
            'toe_slope': 0.2,
            'straight_gamma': 0.7,
            'shoulder_slope': 0.1,
            'logE_range': 1.8,
            'speed_point': 0.6  # density above Dmin
        }
    },
    # ... other papers
}
```

### 2. Filter Selection Algorithm

```python
def select_filters_based_on_contrast(delta_ev, paper_data):
    """
    Select optimal filter pair based on measured contrast.

    Parameters:
        delta_ev: Measured contrast in stops
        paper_data: Paper database entry

    Returns:
        (soft_filter, hard_filter): Optimal filter pair
    """
    # Algorithm:
    # 1. Determine required paper contrast range
    # 2. Match negative contrast to paper capabilities
    # 3. Select filters that provide optimal tonal placement
    # 4. Ensure exposure times are balanced
    pass
```

### 3. Enhanced Exposure Calculation

```python
def calculate_split_grade_enhanced(highlight_lux, shadow_lux, paper_id):
    """
    Enhanced split-grade calculation using paper characteristics.

    Uses paper D-logE curves to calculate exposures that place
    highlight and shadow densities at optimal points on the curve.
    """
    # Algorithm:
    # 1. Convert lux to log exposure
    # 2. Map to paper characteristic curve
    # 3. Calculate required exposure for target densities
    # 4. Optimize filter selection
    # 5. Return balanced exposure times
    pass
```

## Implementation Priority

### 1. Immediate Improvements (Phase 1)

- **Dynamic filter selection** based on ΔEV
- **Enhanced data structure** with manufacturer data
- **Basic optimization** for balanced exposures

### 2. Medium-term Improvements (Phase 2)

- **Paper characteristic curve integration**
- **Advanced optimization algorithms**
- **User calibration interface**

### 3. Long-term Improvements (Phase 3)

- **Full Heiland-like algorithm**
- **Machine learning optimization**
- **Advanced paper database**

## Next Steps

1. **Access Documentation**: Download manufacturer PDFs
2. **Data Extraction**: Extract sensitometric data
3. **Data Integration**: Update filter data structures
4. **Algorithm Implementation**: Implement dynamic filter selection
5. **Testing**: Validate with test cases and user feedback

This analysis provides the foundation for extracting the necessary manufacturer data to create a Heiland-like split-grade algorithm that addresses the current limitations.
