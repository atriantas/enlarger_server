# Manufacturer Data Research Plan for Heiland Algorithm

## Required Data from Manufacturer Documentation

Based on the provided URLs, we need to extract specific sensitometric data that the Heiland Splitgrade Controller likely uses.

## 1. Ilford Documentation Analysis

### URLs Provided:

1. https://www.ilfordphoto.com/amfile/file/download/file/1956/product/1696/
2. https://www.ilfordphoto.com/amfile/file/download/file/1824/product/1696/

### Expected Documents:

- Ilford Multigrade technical datasheets
- Filter factor tables
- Paper characteristic curves
- ISO R values
- Exposure latitude data

### Key Data to Extract:

#### 1.1 Filter Factors for Multigrade Filters

```
Grade | Filter Factor | ISO R | Contrast Index (γ)
------|---------------|-------|-------------------
00    |              |       |
0     |              |       |
1     |              |       |
2     |              |       |
3     |              |       |
4     |              |       |
5     |              |       |
```

#### 1.2 Paper Characteristic Curves

For each Ilford paper (MG IV, MG V, etc.):

- Base + fog density (Dmin)
- Maximum density (Dmax)
- Log exposure range (ΔlogE)
- Gamma (γ) for each filter grade
- Toe and shoulder characteristics

#### 1.3 Exposure Latitude

- Printable density range for each grade
- ISO R to EV conversion table
- Recommended exposure times for test strips

## 2. FOMA Documentation Analysis

### URLs Provided:

1. https://www.foma.cz/en/fomaspeed-variant
2. https://www.foma.cz/en/fomabrom-variant
3. https://www.foma.cz/en/fomatone-MG

### Expected Documents:

- FOMASPEED Variant III datasheet
- FOMABROM Variant datasheet
- FOMATONE MG datasheet
- Filter system specifications

### Key Data to Extract:

#### 2.1 FOMA Filter System

```
Filter | Designation | Filter Factor | Contrast Effect
-------|-------------|---------------|----------------
2xY    |             |               |
Y      |             |               |
(no filter) |        |               |
M1     |             |               |
2xM1   |             |               |
M2     |             |               |
2xM2   |             |               |
```

#### 2.2 Paper Sensitometric Data

For each FOMA paper:

- Spectral sensitivity
- Development characteristics
- D-logE curves
- Recommended developers and times

#### 2.3 Contrast Control

- Filter effects on paper contrast
- Exposure adjustments for filter changes
- Split-grade printing recommendations

## 3. Heiland Algorithm Data Requirements

### 3.1 Core Mathematical Model Data

```
1. Paper_base_speed: ISO P or ISO R value
2. Filter_factors: Multiplication factors for each grade
3. Paper_γ: Contrast index for each filter grade
4. Dmin, Dmax: Density range for each grade
5. LogE_range: Printable log exposure range
```

### 3.2 Calibration Data

```
1. Calibration_constant: Lux·seconds for proper exposure
2. Paper_response_curve: Parameters for D = f(log E)
3. Developer_effects: Development time adjustments
4. Temperature_coefficients: Developer temperature effects
```

### 3.3 Optimization Parameters

```
1. Target_densities: D_highlight_target, D_shadow_target
2. Tolerance_limits: Acceptable density errors
3. Exposure_weights: Weighting for highlight vs shadow
```

## 4. Research Methodology

### 4.1 Document Analysis Steps

1. **Download and review** all technical datasheets
2. **Extract numerical data** from tables and graphs
3. **Digitize characteristic curves** if provided as images
4. **Cross-reference** between different documents
5. **Verify consistency** with known photographic principles

### 4.2 Data Extraction Techniques

1. **Table extraction**: Copy filter factors and ISO R values
2. **Curve digitization**: Use software to extract D-logE points
3. **Parameter calculation**: Derive γ from curve slopes
4. **Unit conversion**: Convert all units to consistent system (lux, seconds, EV)

### 4.3 Data Validation

1. **Cross-check** with existing implementation in `light_sensor.py`
2. **Verify** with photographic science literature
3. **Test** with sample calculations
4. **Compare** with user experience feedback

## 5. Expected Findings

### 5.1 Ilford Data Structure

Based on existing implementation, we expect:

- Filter factors similar to current values (1.6 for 00, 0.4 for 5)
- ISO R values matching current table (180 for 00, 40 for 5)
- More detailed γ values for each grade

### 5.2 FOMA Data Structure

Expected findings:

- Different filter factor progression than Ilford
- Possibly different contrast control mechanism
- May include spectral sensitivity data

### 5.3 Heiland-Specific Insights

Potential discoveries:

- Exact mathematical formulas used
- Optimization criteria (minimize density error, maximize tonal separation)
- Calibration procedures
- Paper database structure

## 6. Integration with Current System

### 6.1 Data Structure Updates

```python
# Proposed enhanced data structure
PAPER_DATABASE = {
    'ilford_mg_iv': {
        'base_speed': 100,  # ISO P
        'dmin': 0.05,
        'dmax': 2.10,
        'filters': {
            '00': {'factor': 1.6, 'iso_r': 180, 'gamma': 0.4},
            '0':  {'factor': 1.4, 'iso_r': 160, 'gamma': 0.5},
            # ... etc.
        },
        'characteristic_curve': {
            'toe_slope': 0.2,
            'straight_gamma': 0.7,
            'shoulder_slope': 0.1,
            'logE_range': 1.8
        }
    },
    # ... other papers
}
```

### 6.2 Algorithm Enhancement

Using manufacturer data to improve:

1. **Filter selection**: Based on actual paper γ values
2. **Exposure calculation**: Using paper response curves
3. **Contrast matching**: Aligning negative contrast with paper capabilities
4. **Optimization**: Minimizing density errors using actual paper characteristics

## 7. Implementation Plan

### 7.1 Phase 1: Data Collection (1-2 days)

1. Download all manufacturer documents
2. Extract key data points
3. Create structured database

### 7.2 Phase 2: Algorithm Update (2-3 days)

1. Integrate manufacturer data into algorithm
2. Update filter selection logic
3. Enhance exposure calculation

### 7.3 Phase 3: Testing (1-2 days)

1. Validate with test cases
2. Compare with current algorithm
3. Adjust based on results

### 7.4 Phase 4: Documentation (1 day)

1. Update algorithm documentation
2. Create data reference guide
3. Add calibration instructions

## 8. Success Criteria

### 8.1 Data Completeness

- All filter grades covered for Ilford and FOMA
- Complete paper characteristic data for major papers
- Consistent units and formats

### 8.2 Algorithm Improvement

- More accurate exposure times
- Better filter selection for given contrast
- Improved match with darkroom experience

### 8.3 Implementation Quality

- Maintains backward compatibility
- Efficient on Pico 2 W resources
- Clear user interface for paper selection

## 9. Next Steps

1. **Access Documentation**: Download the provided URLs
2. **Data Extraction**: Extract sensitometric data
3. **Algorithm Integration**: Update `light_sensor.py` with manufacturer data
4. **Testing**: Validate improvements with test cases

This research will provide the manufacturer-specific data needed to create a Heiland-like algorithm that accurately reflects paper and filter characteristics.
