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


def _estimate_grade_from_gamma(filters, target_gamma):
    """Closest-match filter grade for a target effective gamma.

    Returns the filter key (e.g. '2', '2xM1') whose gamma is nearest
    to target_gamma. Returns None if no filter has gamma data.
    """
    if target_gamma is None or not filters:
        return None

    best_name = None
    best_diff = float('inf')
    for fname, fdata in filters.items():
        g = (fdata or {}).get('gamma')
        if g is None or g <= 0:
            continue
        diff = abs(g - target_gamma)
        if diff < best_diff:
            best_diff = diff
            best_name = fname
    return best_name


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
    Effective-gamma split-grade solver.

    Models the combined soft+hard exposure as a single emulsion whose
    effective gamma is the exposure-weighted blend of the two leg
    gammas:

        γ_eff = (E_soft × γ_soft + E_hard × γ_hard) / (E_soft + E_hard)

    This replaces the old additive density model
    (D = γ_s·log10(E_s/K) + γ_h·log10(E_h/K)) which had γ_eff =
    γ_soft + γ_hard locked by construction — too steep, so endpoints
    landed beyond their target zones (e.g. shadows clipping to Zone I
    on a 4-stop scene with an Ilford 00+5 pair).

    Algorithm
    ---------
    1. γ_target = (highlight_zone − shadow_zone) / Δstops, the print
       contrast that maps the metered lux range onto the requested
       zone span. Clamp to [γ_soft, γ_hard] — the filter pair's
       achievable contrast range.
    2. Solve a 2×2 linear system at the midtone (lux_mid =
       sqrt(highlight_lux·shadow_lux)) for the per-leg exposures:

           E_s_mid + E_h_mid                          = K
           γ_s·E_s_mid + γ_h·E_h_mid (both / K)       = γ_target·K

       Closed form:
           E_s_mid = K · (γ_h − γ_target) / (γ_h − γ_s)
           E_h_mid = K · (γ_target − γ_s) / (γ_h − γ_s)

       This anchors the midtone at Zone V and produces the requested
       effective gamma in one shot — no iterative correction needed.
    3. Convert mid-point exposures to leg times:
           T_soft = E_s_mid · factor_soft / lux_mid
           T_hard = E_h_mid · factor_hard / lux_mid
    4. Apply user per-leg trims (independent multipliers).
    5. Apply Schwarzschild reciprocity correction to the total time.

    If gamma data for either filter is missing the solver falls back
    to a 50/50 mid-anchored split (E_s_mid = E_h_mid = K/2) and the
    result reports algorithm='basic_50_50_fallback'.

    Args:
        highlight_lux: Lux at the print's lightest tone (LOWEST baseboard
            reading — densest negative area).
        shadow_lux: Lux at the print's darkest tone (HIGHEST baseboard
            reading — thinnest negative area).
        calibration: K_paper (mid-gray, lux·seconds).
        system: paper_id (e.g. 'ilford_cooltone').
        highlight_zone: Target print zone for the highlight reading.
        shadow_zone: Target print zone for the shadow reading.
        soft_trim_stops: Per-leg user trim, in stops, for the soft filter.
        hard_trim_stops: Per-leg user trim, in stops, for the hard filter.

    Returns:
        dict with:
          - soft_filter, hard_filter, soft_time, hard_time, total_time
          - soft_factor, hard_factor
          - delta_soft_stops, delta_hard_stops (log2(E_leg / K) at the leg's
            metering point — diagnostic only)
          - delta_ev, highlight_zone, shadow_zone
          - soft_trim_stops, hard_trim_stops
          - reciprocity_applied, reciprocity_p
          - highlight_lux, shadow_lux, paper_id
          - soft_gamma, hard_gamma
          - target_gamma_raw — the unclamped (Z_h−Z_s)/Δstops request
          - target_gamma — clamped to [γ_soft, γ_hard]
          - effective_gamma — γ blended at the midtone with the FINAL
            (post-trim) leg ratio
          - gamma_clamp — None | 'too_soft' (request below γ_soft, scene
            too contrasty for the pair) | 'too_hard' (request above γ_hard,
            scene too flat for the pair)
          - target_grade_estimate — closest filter key for effective_gamma
          - algorithm — 'effective_gamma_v1' or 'basic_50_50_fallback'
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

    gamma_soft = soft_filter_data.get('gamma')
    gamma_hard = hard_filter_data.get('gamma')
    have_gammas = (
        gamma_soft is not None and gamma_hard is not None
        and gamma_soft > 0 and gamma_hard > 0
        and gamma_hard > gamma_soft
    )

    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    lux_mid = math.sqrt(highlight_lux * shadow_lux)
    log10_2 = math.log10(2.0)

    # ---------------------------------------------------------------
    # Step 1 — Target effective gamma from zone request
    # ---------------------------------------------------------------
    zone_span = float(highlight_zone) - float(shadow_zone)
    gamma_clamp = None
    if have_gammas:
        if delta_ev is None or delta_ev <= 1e-6:
            # Degenerate: equal lux readings. Pick the midpoint gamma
            # of the filter pair (a "grade 2-ish" balance).
            gamma_target_raw = (gamma_soft + gamma_hard) / 2.0
        else:
            gamma_target_raw = zone_span / delta_ev

        if gamma_target_raw < gamma_soft:
            gamma_target = gamma_soft
            gamma_clamp = 'too_soft'  # scene wants more compression than pair allows
        elif gamma_target_raw > gamma_hard:
            gamma_target = gamma_hard
            gamma_clamp = 'too_hard'  # scene wants more expansion than pair allows
        else:
            gamma_target = gamma_target_raw
    else:
        gamma_target_raw = None
        gamma_target = None

    # ---------------------------------------------------------------
    # Step 2 — Solve 2×2 system at midtone
    # ---------------------------------------------------------------
    if have_gammas:
        denom = gamma_hard - gamma_soft
        E_soft_mid = calibration * (gamma_hard - gamma_target) / denom
        E_hard_mid = calibration * (gamma_target - gamma_soft) / denom
        algorithm = 'effective_gamma_v1'
    else:
        # Fallback: 50/50 mid-anchored split with no contrast targeting.
        E_soft_mid = calibration / 2.0
        E_hard_mid = calibration / 2.0
        algorithm = 'basic_50_50_fallback'

    # ---------------------------------------------------------------
    # Step 3 — Convert mid-point exposures to leg times
    # ---------------------------------------------------------------
    soft_time = E_soft_mid * factor_soft / lux_mid
    hard_time = E_hard_mid * factor_hard / lux_mid

    # ---------------------------------------------------------------
    # Step 4 — Per-leg user trims
    # ---------------------------------------------------------------
    if soft_trim_stops:
        soft_time *= 2.0 ** soft_trim_stops
    if hard_trim_stops:
        hard_time *= 2.0 ** hard_trim_stops

    # ---------------------------------------------------------------
    # Step 5 — Reciprocity on total exposure
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

    # ---------------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------------
    if soft_time > 0 and hard_time > 0 and have_gammas:
        E_soft_post = (lux_mid / factor_soft) * soft_time
        E_hard_post = (lux_mid / factor_hard) * hard_time
        E_total_post = E_soft_post + E_hard_post
        if E_total_post > 0:
            effective_gamma = (
                (E_soft_post * gamma_soft + E_hard_post * gamma_hard)
                / E_total_post
            )
        else:
            effective_gamma = gamma_target
    else:
        effective_gamma = gamma_target

    target_grade_estimate = (
        _estimate_grade_from_gamma(filters, effective_gamma)
        if effective_gamma is not None else None
    )

    if soft_time > 0:
        delta_soft_stops = math.log2(soft_time * highlight_lux / calibration)
    else:
        delta_soft_stops = 0.0
    if hard_time > 0:
        delta_hard_stops = math.log2(hard_time * shadow_lux / calibration)
    else:
        delta_hard_stops = 0.0

    return {
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
        'soft_gamma': gamma_soft,
        'hard_gamma': gamma_hard,
        'target_gamma_raw': gamma_target_raw,
        'target_gamma': gamma_target,
        'effective_gamma': effective_gamma,
        'gamma_clamp': gamma_clamp,
        'target_grade_estimate': target_grade_estimate,
        'algorithm': algorithm,
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
