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
    validate_exposure_times,
)

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


def evaluate_split_match(delta_ev, total_printable_ev):
    """
    Evaluate how well the split-grade filters match the negative contrast.

    Args:
        delta_ev: Measured contrast range
        total_printable_ev: Combined printable EV range of filters

    Returns:
        str: Match quality ('excellent', 'good', 'fair', 'poor')
    """
    diff = abs(delta_ev - total_printable_ev)
    if diff < 0.5:
        return 'excellent'
    elif diff < 1.0:
        return 'good'
    elif diff < 1.5:
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
):
    """
    Heiland-like split-grade calculation with dynamic filter selection.

    Based on research into Heiland Splitgrade Controller methodology:
    1. Dynamic filter selection based on measured contrast (ΔEV)
    2. Paper characteristic curve consideration
    3. Exposure optimization for balanced results

    Uses unified filter selection logic from paper_database.py for consistency.

    Args:
        highlight_lux: Lux reading at highlight area
        shadow_lux: Lux reading at shadow area
        calibration: Calibration constant (lux × seconds)
        system: Filter system or paper_id (optional, defaults to 'ilford')

    Returns:
        dict: Enhanced split-grade results with Heiland-like features
    """
    if highlight_lux is None or shadow_lux is None:
        return None

    if highlight_lux <= 0 or shadow_lux <= 0:
        return None

    system = system or 'ilford'

    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)

    filter_selection = get_filter_selection(delta_ev, system)
    soft_filter = filter_selection['soft_filter']
    hard_filter = filter_selection['hard_filter']
    selection_reason = filter_selection['description']
    contrast_level = filter_selection['contrast_level']

    # get_paper_data accepts paper_id; system may be a paper_id passed by HTTP server
    paper_data = get_paper_data(system)
    if not paper_data:
        return None

    filter_data = paper_data.get('filters', {})

    if soft_filter not in filter_data:
        if system.startswith('ilford'):
            soft_filter = '00'
            hard_filter = '5'
        else:
            soft_filter = '2xY'
            hard_filter = '2xM2'

    if soft_filter not in filter_data or hard_filter not in filter_data:
        return None

    soft_factor = filter_data[soft_filter]['factor']
    hard_factor = filter_data[hard_filter]['factor']

    soft_time = (calibration / highlight_lux) * soft_factor
    hard_time = (calibration / shadow_lux) * hard_factor

    soft_time_opt, hard_time_opt, optimization_applied = validate_exposure_times(
        soft_time, hard_time, None
    )

    total_time = soft_time_opt + hard_time_opt
    if total_time > 0:
        soft_percent = (soft_time_opt / total_time) * 100
        hard_percent = (hard_time_opt / total_time) * 100
    else:
        soft_percent = 50.0
        hard_percent = 50.0

    soft_iso_r = filter_data[soft_filter]['iso_r']
    hard_iso_r = filter_data[hard_filter]['iso_r']
    soft_printable_ev = iso_r_to_ev(soft_iso_r)
    hard_printable_ev = iso_r_to_ev(hard_iso_r)
    total_printable_ev = soft_printable_ev + hard_printable_ev
    match_quality = evaluate_split_match(delta_ev, total_printable_ev)

    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time_opt,
        'hard_time': hard_time_opt,
        'total_time': total_time,
        'delta_ev': delta_ev,
        'soft_factor': soft_factor,
        'hard_factor': hard_factor,
        'soft_percent': soft_percent,
        'hard_percent': hard_percent,
        'match_quality': match_quality,
        'selection_reason': selection_reason,
        'contrast_level': contrast_level,
        'algorithm': 'heiland_unified',
        'highlight_lux': highlight_lux,
        'shadow_lux': shadow_lux,
        'optimization_applied': optimization_applied,
        'system': system,
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
            print(f"  Percentages: {result['soft_percent']:.0f}% / {result['hard_percent']:.0f}%")
            print(f"  Match quality: {result['match_quality']}")
            print(f"  Selection: {result['selection_reason']}")

    print("\n" + "=" * 60)
    print("Split-grade calculator ready!")
