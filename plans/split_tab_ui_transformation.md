# SPLIT Tab UI Transformation Plan

## Objective

Transform the SPLIT tab's Split-Grade tool UI to match the PAPER & FILTER SETUP at the CALC tab, ensuring consistency across the application.

## Current State Analysis

### SPLIT Tab Current Structure:

1. **Paper Brand selector**: Dropdown (`<select id="splitPaperBrand">`) with 3 options:
   - FOMA
   - Ilford Multigrade
   - Custom Factors

2. **FOMA Paper Type selection**: Toggle buttons (2 options):
   - FOMASPEED Variant III (button)
   - FOMATONE MG Classic (button)

3. **Ilford Paper Type selection**: None (missing)

4. **Custom Factors section**: Input fields for all 7 grades

### Target State (matching CALC tab):

1. **Paper Brand selector**: Toggle switch buttons (like CALC tab's Contrast Filter Adjustment)
   - FOMA button
   - Ilford button
   - Remove "Custom Factors" option

2. **FOMA Paper Type selector**: Dropdown menu with all FOMA paper types
   - FOMASPEED VARIANT
   - FOMABROM VARIANT
   - FOMAPASTEL MG (Special FB Colored Base)
   - FOMATONE MG Classic (Warm Tone)

3. **Ilford Paper Type selector**: Dropdown menu with all Ilford paper types
   - Multigrade RC Cooltone
   - Multigrade IV RC Portfolio (Discontinued)
   - MULTIGRADE RC DELUXE (NEW)
   - MULTIGRADE RC PORTFOLIO (NEW)
   - MULTIGRADE FB CLASSIC
   - MULTIGRADE FB WARM TONE
   - MULTIGRADE ART 300

## Implementation Steps

### Phase 1: HTML Structure Changes

1. **Replace Paper Brand dropdown with toggle buttons**:
   - Remove `<select id="splitPaperBrand">`
   - Add two toggle buttons: `btnSplitFoma` and `btnSplitIlford`
   - Style to match CALC tab's toggle buttons

2. **Transform FOMA Paper Type toggle buttons to dropdown**:
   - Remove existing button group (`<div class="paper-selector">`)
   - Add `<select id="splitFomaPaperType">` dropdown
   - Populate with all 4 FOMA paper types

3. **Add Ilford Paper Type dropdown**:
   - Add `<select id="splitIlfordPaperType">` dropdown (initially hidden)
   - Populate with all 7 Ilford paper types

4. **Remove Custom Factors section**:
   - Hide or remove the custom factors input section
   - Update JavaScript to handle removal

### Phase 2: JavaScript Logic Updates

1. **Update `SplitGradeCalculator` class**:
   - Modify constructor to initialize new UI elements
   - Add `setPaperBrand()` method similar to CALC tab
   - Add `updatePaperTypeUI()` method to show/hide appropriate dropdowns
   - Update filter factor retrieval logic

2. **Event handling**:
   - Add click listeners for new toggle buttons
   - Add change listeners for new dropdowns
   - Ensure calculations update when paper type changes

3. **Data synchronization**:
   - Ensure paper database consistency with CALC tab
   - Update `FILTER_FACTORS` static property to include all paper types

### Phase 3: CSS Styling

1. **Style toggle buttons** to match CALC tab
2. **Style dropdowns** to match application theme
3. **Ensure responsive layout** for new elements

## Technical Considerations

### Paper Database Consistency

The SPLIT tab should use the same paper database as the CALC tab. Need to check if `SplitGradeCalculator.FILTER_FACTORS` needs to be expanded or if we should reference the same data structure.

### Backward Compatibility

- Existing saved presets might reference "Custom" brand - need migration or default handling
- Update any code that references the old `splitPaperBrand` element

### UI/UX Consistency

- Match toggle button active/inactive states
- Match dropdown styling and behavior
- Ensure proper spacing and alignment

## Files to Modify

1. `index.html` - SPLIT tab section (lines ~2278-2600)
2. `index.html` - `SplitGradeCalculator` class (lines ~10374-11000)
3. CSS styles within `index.html`

## Success Criteria

1. Paper Brand selector uses toggle buttons (no dropdown)
2. FOMA and Ilford paper types use dropdown menus
3. All paper type options match CALC tab
4. UI updates correctly when switching brands
5. Calculations work with new paper types
6. No "Custom Factors" option visible
7. Consistent styling with CALC tab
