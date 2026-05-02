"""
Enhanced Split-Grade Calculation Module

This module implements Heiland-like split-grade calculations with:
1. Dynamic filter selection based on contrast (ΔEV)
2. Paper characteristic curve integration
3. Exposure optimization for balanced results
4. Backward compatibility with existing API

Based on research into Heiland Splitgrade Controller methodology.
"""

import math
from lib.paper_database import (
    get_paper_data,
    get_filter_selection,
    get_filter_data,
    get_splitgrade_config,
    validate_exposure_times,
)
from lib.exposure_calc import apply_reciprocity

def calculate_delta_ev(highlight_lux, shadow_lux):
    """
    Calculate contrast range (ΔEV) from highlight and shadow readings.
    
    ΔEV = abs(log₂(shadow_lux / highlight_lux))
    
    Args:
        highlight_lux: Lux reading at paper highlight area
        shadow_lux: Lux reading at paper shadow area
    
    Returns:
        float: Contrast range in EV stops (always positive)
    """
    if highlight_lux is None or shadow_lux is None:
        return None
    
    if highlight_lux <= 0 or shadow_lux <= 0:
        return None
    
    # Shadow areas receive more light than highlight areas
    # because they're less dense on the negative
    delta_ev = abs(math.log2(shadow_lux / highlight_lux))
    return delta_ev

# ---------------------------------------------------------------------------
# Helper functions extracted from DarkroomLightMeter (split-grade specific)
# ---------------------------------------------------------------------------

# ISO R values define paper's exposure latitude (printable ΔEV range)
ISO_R_TO_EV = {
    180: 8.0,   # Grade 00 - very soft (gamma 0.4)
    160: 7.5,   # Grade 0 (gamma 0.5)
    135: 7.0,   # FOMA 2xY (gamma 0.4)
    130: 6.8,   # Grade 1 (gamma 0.6)
    120: 6.5,   # FOMA Y (gamma 0.5)
    110: 6.2,   # Grade 2 (normal) (gamma 0.7)
    105: 6.0,   # FOMA no filter (gamma 0.6)
    90: 5.6,    # Grade 3 / FOMA M1 (gamma 0.8)
    80: 5.2,    # FOMA 2xM1 (gamma 0.8)
    75: 5.0,    # FOMA 2xM1 (gamma 0.8)
    65: 4.8,    # Grade 4 / FOMA M2 (gamma 0.9)
    60: 4.6,    # Grade 4 (gamma 0.9)
    55: 4.4,    # Grade 5 / FOMA 2xM2 (gamma 1.0)
    40: 4.0,    # Grade 5 - very hard (gamma 1.0)
}


def iso_r_to_ev(iso_r):
    """
    Interpolate EV from ISO R value using the ISO_R_TO_EV lookup table.

    Args:
        iso_r: ISO R value (40–180 typical range)

    Returns:
        float: Estimated EV printable range
    """
    sorted_pairs = sorted(ISO_R_TO_EV.items(), reverse=True)

    for i, (r, ev) in enumerate(sorted_pairs):
        if iso_r >= r:
            if i == 0:
                return ev
            prev_r, prev_ev = sorted_pairs[i - 1]
            ratio = (iso_r - r) / (prev_r - r)
            return ev + ratio * (prev_ev - ev)

    return sorted_pairs[-1][1]


def evaluate_split_match(delta_ev, filter_selection):
    """
    Evaluate how well the selected filter pair matches the negative contrast.

    Checks how well delta_ev fits within the selected filter bin from
    the filter selection rules. A delta_ev centered in its bin is excellent;
    near the edges is good; outside is fair/poor.

    Args:
        delta_ev: Measured contrast range in EV stops
        filter_selection: Dict from get_filter_selection() with bin bounds

    Returns:
        str: Match quality ('excellent', 'good', 'fair', 'poor')
    """
    bin_min = filter_selection.get('bin_min', 0.0)
    bin_max = filter_selection.get('bin_max', 10.0)
    bin_range = bin_max - bin_min

    if bin_range <= 0:
        return 'good'

    # How far from center, normalized: 0.0 (center) to 0.5 (edge)
    bin_center = (bin_min + bin_max) / 2.0
    offset = abs(delta_ev - bin_center) / bin_range

    if offset <= 0.25:
        return 'excellent'
    elif offset <= 0.5:
        return 'good'
    elif offset <= 0.75:
        return 'fair'
    else:
        return 'poor'


def calculate_split_grade_legacy(
    highlight_lux,
    shadow_lux,
    calibration=1000.0,
    paper_id='ilford_cooltone',
):
    """
    Calculate split-grade exposure times (legacy method - uses fixed filters).

    Split-grade printing uses two exposures:
    1. Soft filter (controls highlights) - based on highlight lux
    2. Hard filter (controls shadows) - based on shadow lux

    Args:
        highlight_lux: Lux reading at highlight area
        shadow_lux: Lux reading at shadow area
        calibration: Calibration constant (lux × seconds)
        paper_id: Paper identifier from paper_database

    Returns:
        dict: Split-grade result with filter, time, and contrast data
    """
    if highlight_lux is None or shadow_lux is None:
        return None

    if highlight_lux <= 0 or shadow_lux <= 0:
        return None

    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return None

    manufacturer = paper_data.get('manufacturer', 'Ilford').lower()

    if 'ilford' in manufacturer:
        soft_filter = '00'
        hard_filter = '5'
    else:  # FOMA
        soft_filter = '2xY'
        hard_filter = '2xM2'

    soft_filter_data = get_filter_data(paper_id, soft_filter)
    hard_filter_data = get_filter_data(paper_id, hard_filter)

    if not soft_filter_data or not hard_filter_data:
        return None

    soft_factor = soft_filter_data['factor']
    hard_factor = hard_filter_data['factor']

    soft_time = (calibration / highlight_lux) * soft_factor
    hard_time = (calibration / shadow_lux) * hard_factor

    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)

    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'total_time': soft_time + hard_time,
        'delta_ev': delta_ev,
        'soft_factor': soft_factor,
        'hard_factor': hard_factor,
        'highlight_lux': highlight_lux,
        'shadow_lux': shadow_lux,
    }


def calculate_split_grade_heiland(
    highlight_lux,
    shadow_lux,
    calibration=1000.0,
    system=None,
    highlight_zone=7,
    shadow_zone=3,
    soft_trim_stops=0.0,
    hard_trim_stops=0.0,
):
    """
    Gamma-aware split-grade calculation (RH Designs StopClock Vario style).

    Models each filter leg as primarily exposing one emulsion with its own
    gamma (γ_soft for the green-sensitive emulsion, γ_hard for the
    blue-sensitive emulsion) and assumes the resulting densities ADD on the
    final print. This captures the cross-emulsion bleed that the
    independent-leg model ignores: at the shadow area the soft leg also
    contributes density, and at the highlight area the hard leg also
    contributes — both push tones darker than the simple zone-offset
    formulas predict.

    Algorithm
    ---------
    1. Initial solution from zone-offset formulas (independent-leg).
    2. Predict midtone density using the additive model with per-filter
       gammas. Apply a multiplicative correction to BOTH legs so the
       midtone lands at Zone V (matches single-grade calibration K).
    3. Predict the resulting endpoint zones for diagnostic output. With
       the additive model the print's effective gamma equals
       γ_soft + γ_hard, so when the negative's contrast doesn't match
       (Z_h − Z_s) × γ_ref / (γ_soft + γ_hard), endpoints drift
       proportionally and predicted_zone_h / _s reflect that drift.
    4. Apply per-leg user trims (multiplicative, independent).
    5. Apply reciprocity-failure correction on the total exposure.

    The midtone anchor fixes the user's "grey card off in split-grade"
    symptom even though the per-filter gammas alone can't fully decouple
    endpoint placement (the additive model is inherently rank-1 in
    density-space). Endpoints that drift can be compensated with
    per-leg trims after observing a test print.

    When per-filter gamma data is missing for a paper, the function
    falls back to the independent-leg behavior of the previous version.

    Args:
        highlight_lux: Lux at the print's lightest tone (dim spot at paper plane).
        shadow_lux: Lux at the print's darkest tone (bright spot at paper plane).
        calibration: K_paper (unfiltered, mid-gray) in lux × seconds.
        system: paper_id (e.g. 'ilford_cooltone').
        highlight_zone: Target zone for the highlight reading. Default 7.
        shadow_zone: Target zone for the shadow reading. Default 3.
        soft_trim_stops: Per-paper user trim on the soft leg (stops).
        hard_trim_stops: Per-paper user trim on the hard leg (stops).

    Model limitation note
    ---------------------
    The additive density model has an effective print gamma of
    (γ_soft + γ_hard), which over-predicts real split-grade print
    contrast. The MIDTONE prediction is reliable (rank-1 system → the
    average density across the metered range is well-determined) and is
    used to anchor the print to the user's calibration. Per-endpoint
    predictions are not reliable enough to expose to the user; the
    actionable knob for endpoint drift is per-leg trim adjustment after
    a test print.

    Returns:
        dict including all original fields (soft_time, hard_time, etc.)
        plus gamma-aware diagnostic fields:
          - soft_gamma, hard_gamma, reference_gamma
          - midtone_correction_stops — stops applied to BOTH legs to
            anchor the midtone density to Zone V (matches calibration K)
          - midtone_density_offset_pre_correction — predicted density
            error at midtone before the anchor correction was applied
          - algorithm: 'gamma_aware_v1' or 'independent_leg_fallback'
    """
    if highlight_lux is None or shadow_lux is None:
        return None
    if highlight_lux <= 0 or shadow_lux <= 0:
        return None
    if calibration is None or calibration <= 0:
        return None

    paper_id = system or 'ilford_cooltone'
    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return None

    sg_config = get_splitgrade_config(paper_id)
    if not sg_config:
        return None

    soft_filter = sg_config['soft_filter']
    hard_filter = sg_config['hard_filter']
    filters = paper_data.get('filters', {})

    soft_filter_data = filters.get(soft_filter)
    hard_filter_data = filters.get(hard_filter)
    if not soft_filter_data or not hard_filter_data:
        return None

    factor_soft = soft_filter_data.get('factor')
    factor_hard = hard_filter_data.get('factor')
    if not factor_soft or not factor_hard or factor_soft <= 0 or factor_hard <= 0:
        return None

    # Per-filter gammas drive the gamma-aware solver. Both must be present
    # and positive; otherwise we fall back to the independent-leg model.
    gamma_soft = soft_filter_data.get('gamma')
    gamma_hard = hard_filter_data.get('gamma')
    use_gamma_aware = (
        gamma_soft is not None and gamma_hard is not None
        and gamma_soft > 0 and gamma_hard > 0
    )

    # Reference gamma — used to convert zone numbers ↔ density. The
    # calibrated grade's gamma is the right anchor since K is calibrated
    # at that grade. Try Ilford grade 2 first, then FOMA's 2xM1 (normal).
    ref_filter_data = filters.get('2') or filters.get('2xM1')
    gamma_ref = (ref_filter_data or {}).get('gamma')
    if not gamma_ref or gamma_ref <= 0:
        gamma_ref = 0.85  # Sensible default if reference filter is missing

    log10_2 = math.log10(2.0)

    # ---------------------------------------------------------------
    # Step 1 — Initial solution (zone-offset formulas, independent-leg)
    # ---------------------------------------------------------------
    delta_soft_stops_init = math.log2(factor_soft) - (highlight_zone - 5)
    delta_hard_stops_init = math.log2(factor_hard) + (5 - shadow_zone)

    soft_time = (calibration / highlight_lux) * (2.0 ** delta_soft_stops_init)
    hard_time = (calibration / shadow_lux) * (2.0 ** delta_hard_stops_init)

    # ---------------------------------------------------------------
    # Step 2 — Gamma-aware midtone anchor
    # Density model (additive, per-filter gammas):
    #   D - D_zoneV = γ_s × log10(E_s/K) + γ_h × log10(E_h/K)
    # where E_s = (lux/factor_s) × T_s and E_h similar.
    # K is the Zone V exposure on each filter alone — same for both
    # under the speed-matched filter assumption.
    # ---------------------------------------------------------------
    midtone_density_offset = 0.0
    midtone_correction_stops = 0.0

    if use_gamma_aware:
        lux_mid = math.sqrt(highlight_lux * shadow_lux)
        E_soft_mid = (lux_mid / factor_soft) * soft_time
        E_hard_mid = (lux_mid / factor_hard) * hard_time
        if E_soft_mid > 0 and E_hard_mid > 0:
            midtone_density_offset = (
                gamma_soft * math.log10(E_soft_mid / calibration)
                + gamma_hard * math.log10(E_hard_mid / calibration)
            )
            # Multiplicative α applied to BOTH legs cancels the midtone
            # density error: (γ_s + γ_h) × log10(α) + δ_d_mid = 0
            log10_alpha = -midtone_density_offset / (gamma_soft + gamma_hard)
            alpha = 10.0 ** log10_alpha
            soft_time *= alpha
            hard_time *= alpha
            midtone_correction_stops = log10_alpha / log10_2

    # ---------------------------------------------------------------
    # Step 3 — Per-leg user trims (independent, multiplicative)
    # Positive trim = more exposure on that leg = darker that endpoint.
    # ---------------------------------------------------------------
    if soft_trim_stops:
        soft_time *= 2.0 ** soft_trim_stops
    if hard_trim_stops:
        hard_time *= 2.0 ** hard_trim_stops

    # ---------------------------------------------------------------
    # Step 4 — Reciprocity correction on total exposure (lengthens long
    # prints only — clamp inside apply_reciprocity).
    # ---------------------------------------------------------------
    total_time = soft_time + hard_time
    corrected_total, reciprocity_applied, scale = apply_reciprocity(
        total_time, paper_id
    )
    if reciprocity_applied:
        soft_time *= scale
        hard_time *= scale
        total_time = corrected_total
    reciprocity_p = sg_config.get('reciprocity_p', 0.0)

    # Final delta_soft / delta_hard expressed as stops-from-Zone-V (kept
    # for backward compatibility with logs and the SPA).
    if highlight_lux > 0 and calibration > 0 and soft_time > 0:
        delta_soft_stops = math.log2(soft_time * highlight_lux / calibration)
    else:
        delta_soft_stops = 0.0
    if shadow_lux > 0 and calibration > 0 and hard_time > 0:
        delta_hard_stops = math.log2(hard_time * shadow_lux / calibration)
    else:
        delta_hard_stops = 0.0

    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)

    return {
        # Backward-compatible fields
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'total_time': total_time,
        'soft_factor': factor_soft,
        'hard_factor': factor_hard,
        'delta_soft_stops': delta_soft_stops,
        'delta_hard_stops': delta_hard_stops,
        'delta_ev': delta_ev,
        'highlight_zone': highlight_zone,
        'shadow_zone': shadow_zone,
        'soft_trim_stops': soft_trim_stops,
        'hard_trim_stops': hard_trim_stops,
        'reciprocity_applied': reciprocity_applied,
        'reciprocity_p': reciprocity_p,
        'highlight_lux': highlight_lux,
        'shadow_lux': shadow_lux,
        'paper_id': paper_id,
        # Gamma-aware diagnostic fields
        'soft_gamma': gamma_soft,
        'hard_gamma': gamma_hard,
        'reference_gamma': gamma_ref,
        'midtone_correction_stops': midtone_correction_stops,
        'midtone_density_offset_pre_correction': midtone_density_offset,
        'algorithm': (
            'gamma_aware_v1' if use_gamma_aware else 'independent_leg_fallback'
        ),
    }


# Test function
if __name__ == "__main__":
    print("Enhanced Split-Grade Calculator Test")
    print("=" * 60)

    test_cases = [
        ("Low contrast", 100.0, 150.0),
        ("Normal contrast", 100.0, 400.0),
        ("High contrast", 100.0, 800.0),
        ("Extreme contrast", 100.0, 1600.0),
    ]

    for name, highlight, shadow in test_cases:
        print(f"\n{name}: Highlight={highlight} lux, Shadow={shadow} lux")

        result = calculate_split_grade_heiland(
            highlight, shadow, 1000.0, 'ilford_multigrade_rc_deluxe_new'
        )

        if result:
            print(f"  ΔEV: {result['delta_ev']:.2f}")
            print(f"  Filters: {result['soft_filter']} + {result['hard_filter']}")
            print(f"  Times: {result['soft_time']:.1f}s + {result['hard_time']:.1f}s = {result['total_time']:.1f}s")
            print(f"  Offsets: soft {result['delta_soft_stops']:+.2f} stops, "
                  f"hard {result['delta_hard_stops']:+.2f} stops")
            print(f"  Reciprocity applied: {result['reciprocity_applied']}")

    print("\n" + "=" * 60)
    print("Split-grade calculator ready!")
