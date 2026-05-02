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
    get_filter_data,
    get_splitgrade_config,
)
from lib.exposure_calc import apply_reciprocity, recommend_filter_grade

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
    overall_offset_stops=0.0,
    contrast_bias_stops=0.0,
    soft_trim_stops=0.0,
    hard_trim_stops=0.0,
):
    """
    Canonical RH Designs StopClock Vario / Heiland Splitgrade-style
    equivalent-grade split.

    Algorithm:

      1. ΔEV = |log2(shadow_lux / highlight_lux)|  → measured contrast.
      2. Effective ΔEV for grade lookup = ΔEV − contrast_bias_stops.
         Positive bias → smaller effective ΔEV → harder equivalent grade
         (more contrast on the print). Negative bias → softer grade.
      3. Equivalent single grade G_eq is the closest filter whose ISO R
         matches the effective ΔEV (via recommend_filter_grade).
      4. Total time is set so the geometric-mean midpoint lux lands at
         Zone V, with a global stops offset applied directly:
             base_time = (K / lux_mid) · 2^(overall_offset_stops)
      5. Soft fraction α is interpolated from the equivalent grade's ISO R
         between the paper's hardest- and softest-filter ISO R endpoints:
             α = (ISO_R_eq − ISO_R_hard) / (ISO_R_soft − ISO_R_hard)
         clamped to [0, 1]. α=1 → pure soft (00/2xY), α=0 → pure hard (5/2xM2).
      6. Legs sized so combined exposure at the midpoint matches the
         equivalent single-grade exposure (single-emulsion equivalence):
             T_soft = α     · factor_soft · base_time · 2^soft_trim
             T_hard = (1−α) · factor_hard · base_time · 2^hard_trim
         Highlights and shadows then land at zones determined by the
         equivalent grade's contrast curve — canonical split-grade behaviour.

    Args:
        highlight_lux: Lux at the print's lightest tone (dim spot at paper plane).
        shadow_lux: Lux at the print's darkest tone (bright spot at paper plane).
        calibration: K_paper (unfiltered, mid-gray Zone V) in lux × seconds.
        system: paper_id (e.g. 'ilford_cooltone'). Falls back to ilford_cooltone.
        overall_offset_stops: Global brightness offset (stops, default 0).
            Positive = darker print; negative = lighter print.
        contrast_bias_stops: Shifts the equivalent-grade lookup (stops, default 0).
            Positive = harder grade than auto pick; negative = softer.
        soft_trim_stops: Per-leg soft fine-tune (stops, default 0).
        hard_trim_stops: Per-leg hard fine-tune (stops, default 0).

    Returns:
        dict with soft/hard times, filters, factors, delta_ev, equivalent
        grade info, soft fraction (alpha), reciprocity flag, and inputs.
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
    iso_r_soft = soft_filter_data.get('iso_r')
    iso_r_hard = hard_filter_data.get('iso_r')
    if not factor_soft or not factor_hard or factor_soft <= 0 or factor_hard <= 0:
        return None

    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    if delta_ev is None:
        return None

    # ── Steps 1–3: equivalent grade for biased contrast ────────────────
    delta_ev_effective = max(0.0, delta_ev - contrast_bias_stops)
    equivalent = recommend_filter_grade(delta_ev_effective, paper_id=paper_id)
    if not equivalent:
        return None

    grade_eq = equivalent.get('grade')
    iso_r_eq = equivalent.get('iso_r')
    factor_eq = equivalent.get('factor', 1.0)
    eq_match_quality = equivalent.get('match_quality')
    eq_out_of_range = equivalent.get('out_of_range')

    # Soft fraction α via ISO R interpolation (paper-specific endpoints).
    if (iso_r_soft is not None and iso_r_hard is not None
            and iso_r_eq is not None and iso_r_soft != iso_r_hard):
        alpha = (iso_r_eq - iso_r_hard) / (iso_r_soft - iso_r_hard)
        alpha = max(0.0, min(1.0, alpha))
    else:
        alpha = 0.5

    # ── Step 4: midpoint-anchored base time, with overall offset ──────
    lux_mid = math.sqrt(highlight_lux * shadow_lux)
    base_time = (calibration / lux_mid) * (2.0 ** overall_offset_stops)

    # ── Step 5: equivalent-exposure split, with per-leg trims ─────────
    soft_time = alpha * factor_soft * base_time * (2.0 ** soft_trim_stops)
    hard_time = (1.0 - alpha) * factor_hard * base_time * (2.0 ** hard_trim_stops)

    # Reciprocity applied to the cumulative exposure, scaled back to legs.
    # Internally consistent (legs still sum to corrected_total) and small
    # for typical darkroom timings; clamp via apply_reciprocity for short
    # exposures where Schwarzschild form does not apply.
    total_time = soft_time + hard_time
    corrected_total, reciprocity_applied, scale = apply_reciprocity(
        total_time, paper_id
    )
    if reciprocity_applied:
        soft_time *= scale
        hard_time *= scale
        total_time = corrected_total
    reciprocity_p = sg_config.get('reciprocity_p', 0.0)

    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'total_time': total_time,
        'soft_factor': factor_soft,
        'hard_factor': factor_hard,
        'delta_ev': delta_ev,
        'delta_ev_effective': delta_ev_effective,
        'soft_alpha': alpha,
        'equivalent_grade_calc': grade_eq,
        'equivalent_iso_r': iso_r_eq,
        'equivalent_factor': factor_eq,
        'equivalent_match_quality': eq_match_quality,
        'equivalent_out_of_range': eq_out_of_range,
        'overall_offset_stops': overall_offset_stops,
        'contrast_bias_stops': contrast_bias_stops,
        'soft_trim_stops': soft_trim_stops,
        'hard_trim_stops': hard_trim_stops,
        'reciprocity_applied': reciprocity_applied,
        'reciprocity_p': reciprocity_p,
        'highlight_lux': highlight_lux,
        'shadow_lux': shadow_lux,
        'paper_id': paper_id,
        'algorithm': 'rh_designs_equivalent_grade_split',
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
            print(f"  Equivalent grade: {result['equivalent_grade_calc']} "
                  f"(ISO R {result['equivalent_iso_r']}, "
                  f"factor {result['equivalent_factor']:.2f})")
            print(f"  Filters: {result['soft_filter']} + {result['hard_filter']}")
            print(f"  α (soft fraction): {result['soft_alpha']*100:.0f}% soft / "
                  f"{(1-result['soft_alpha'])*100:.0f}% hard")
            print(f"  Times: {result['soft_time']:.2f}s + {result['hard_time']:.2f}s "
                  f"= {result['total_time']:.2f}s")
            print(f"  Reciprocity applied: {result['reciprocity_applied']}")

    print("\n" + "=" * 60)
    print("Split-grade calculator ready!")
