# Contrast Filter UI Transformation Plan

## Objective

Transform the "Contrast Filter Adjustment" tool's paper type selection from toggle buttons to dropdown menus, consistent with the METER tab's "PAPER & FILTER SETUP" UI pattern.

## Current State (CALC Tab)

1. **Paper Brand Selection**: Dropdown with 3 options (FOMA, Ilford Multigrade, Kodak Polycontrast)
2. **Paper Type Selection**: Toggle buttons (4 FOMA paper types only, shown when FOMA selected)
3. **Contrast Filter**: Dropdown (populated based on brand)
4. **ISO R & Contrast Factor**: Display boxes

## Desired State (CALC Tab)

1. **Paper Brand Selection**: Toggle buttons (Ilford and FOMA only)
2. **Paper Type Selection**: Dropdowns (Ilford paper type dropdown when Ilford selected, FOMA paper type dropdown when FOMA selected)
3. **Contrast Filter**: Dropdown (unchanged)
4. **ISO R & Contrast Factor**: Display boxes (unchanged)

## Changes Required

### 1. HTML Changes (CALC Tab)

#### Section: Lines 2017-2097 in index.html

**Current HTML:**

```html
<div class="control">
  <div class="control-label">
    <span>PAPER BRAND</span>
  </div>
  <select class="settings-input" id="contrastBrandSelect">
    <option value="FOMA">FOMA</option>
    <option value="Ilford">Ilford Multigrade</option>
    <option value="Kodak">Kodak Polycontrast</option>
  </select>
</div>
```

**New HTML (toggle buttons):**

```html
<div class="control">
  <div class="control-label">
    <span>PAPER BRAND</span>
  </div>
  <div class="settings-group" style="margin-top: 5px">
    <button class="toggle-btn active" data-brand="FOMA" id="btnContrastFoma">
      FOMA
    </button>
    <button class="toggle-btn" data-brand="Ilford" id="btnContrastIlford">
      Ilford
    </button>
  </div>
</div>
```

**Current Paper Type Section (toggle buttons):**

```html
<div class="info-box" id="paperTypeBox">
  <div class="label-sm">Paper Type</div>
  <div class="paper-selector" style="margin-top: 5px">
    <button class="toggle-btn active" data-paper="fomaspeed" id="btnFomaspeed">
      FOMASPEED<br />Variant III
    </button>
    <!-- ... 3 more buttons ... -->
  </div>
</div>
```

**New Paper Type Section (dropdowns):**

```html
<!-- Ilford Paper Type (hidden by default) -->
<div id="ilfordPaperSelector" class="control" style="display: none">
  <div class="control-label">
    <span>ILFORD PAPER TYPE</span>
  </div>
  <select class="settings-input" id="ilfordPaperType" style="width: 100%">
    <option value="cooltone">Multigrade RC Cooltone</option>
    <option value="portfolio">Multigrade IV RC Portfolio (Discontinued)</option>
    <option value="rc_deluxe_new">MULTIGRADE RC DELUXE (NEW)</option>
    <option value="rc_portfolio_new">MULTIGRADE RC PORTFOLIO (NEW)</option>
    <option value="fb_classic">Multigrade FB Classic</option>
    <option value="fb_warmtone">Multigrade FB Warmtone</option>
    <option value="fb_cooltone">Multigrade FB Cooltone</option>
  </select>
</div>

<!-- FOMA Paper Type (visible when FOMA selected) -->
<div id="fomaPaperSelector" class="control">
  <div class="control-label">
    <span>FOMA PAPER TYPE</span>
  </div>
  <select class="settings-input" id="fomaPaperType" style="width: 100%">
    <option value="fomaspeed">FOMASPEED VARIANT</option>
    <option value="fomabrom">FOMABROM VARIANT</option>
    <option value="fomapastel_mg">
      FOMAPASTEL MG (Special FB Colored Base)
    </option>
    <option value="fomatone_mg_classic_variant">
      FOMATONE MG Classic (Warm Tone)
    </option>
  </select>
</div>
```

**Note**: The `paperTypeBox` div will be replaced with these dropdown containers. The `exp-info` grid layout may need adjustment to maintain 2-column layout.

### 2. JavaScript Changes (EnlargerHeightCalculator Class)

#### Current Properties to Update:

- `currentBrand` initialization (remove "Kodak" default)
- `paperTypes` object (keep Kodak data but remove from UI flow)
- Event listeners for brand selection (change from dropdown to button clicks)
- `updateBrandUI()` method (show/hide paper type dropdowns instead of buttons)
- `selectPaper()` method (rename to `setPaperType()` and handle dropdown change)
- `updateFilterOptions()` method (remove Kodak branch)

#### New Methods Needed:

- `setPaperBrand(brand)` - Similar to METER tab's implementation
- `setIlfordPaperType(type)` - Handle Ilford dropdown changes
- `setFomaPaperType(type)` - Handle FOMA dropdown changes

#### Event Listener Changes:

- Remove `contrastBrandSelect` change listener
- Add click listeners for `btnContrastFoma` and `btnContrastIlford`
- Add change listeners for `ilfordPaperType` and `fomaPaperType` dropdowns
- Remove click listeners for paper type buttons (`btnFomaspeed`, `btnFomatonemg`, etc.)

### 3. SPLIT Tab Changes

#### HTML Changes:

Remove Kodak Polycontrast option from `splitPaperBrand` dropdown (line 2271):

```html
<select class="settings-input" id="splitPaperBrand">
  <option value="FOMA">FOMA</option>
  <option value="Ilford">Ilford Multigrade</option>
  <option value="Custom">Custom Factors</option>
</select>
```

#### JavaScript Changes:

- Update any Kodak-related logic in split-grade calculator
- Ensure filter options don't include Kodak grades

### 4. Data Consistency

#### Paper Type Mapping:

Ensure paper type values match between CALC and METER tabs:

- FOMA: `fomaspeed`, `fomabrom`, `fomapastel_mg`, `fomatone_mg_classic_variant`
- Ilford: `cooltone`, `portfolio`, `rc_deluxe_new`, `rc_portfolio_new`, `fb_classic`, `fb_warmtone`, `fb_cooltone`

#### Filter Data:

Kodak filter data should remain in `paperTypes` object for backward compatibility but not be accessible via UI.

## Implementation Steps

1. **Backup current HTML section** (lines 2017-2097)
2. **Replace paper brand dropdown with toggle buttons**
3. **Replace paper type toggle buttons with dropdown containers**
4. **Update JavaScript event listeners and methods**
5. **Test brand selection and paper type dropdown visibility**
6. **Test filter dropdown population**
7. **Test ISO R and Contrast Factor updates**
8. **Update SPLIT tab to remove Kodak option**
9. **Test overall functionality**
10. **Verify visual consistency with METER tab**

## Testing Checklist

- [ ] Ilford brand button selects Ilford, shows Ilford paper type dropdown
- [ ] FOMA brand button selects FOMA, shows FOMA paper type dropdown
- [ ] Paper type dropdowns populate correct filter options
- [ ] Contrast filter dropdown updates based on brand and paper type
- [ ] ISO R value updates correctly
- [ ] Contrast Factor updates correctly
- [ ] Kodak option completely removed from CALC tab
- [ ] Kodak option removed from SPLIT tab
- [ ] No JavaScript errors in console
- [ ] UI matches METER tab styling

## Notes

- The `paperTypeBox` and `isoRBox` elements will need ID updates or removal
- Consider keeping the `exp-info` grid layout (2 columns) with adjusted content
- Ensure dropdowns use same styling as METER tab (`settings-input` class)
- Maintain backward compatibility with saved settings that might reference Kodak
