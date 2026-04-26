"""
Exposure Calculation Module
Raspberry Pi Pico 2 W - MicroPython v1.27.0

Pure computation functions for darkroom exposure calculations.
Extracted from DarkroomLightMeter to separate concerns:
  - This module: exposure math, filter grade recommendation, virtual proof
  - light_sensor.py: hardware driver + sensor state management
  - splitgrade_enhanced.py: split-grade printing calculations
"""

import math
import sys
from lib.paper_database import (
    get_paper_data,
    get_filter_data,
    get_available_filters,
    PAPER_DATABASE,
)


def calculate_exposure_time(lux, calibration=1000.0, filter_grade=None, paper_id=None):
    """
    Calculate exposure time from lux reading.

    Formula: time = calibration_constant / lux × filter_factor

    Args:
        lux: Measured illuminance in lux
        calibration: Calibration constant (lux × seconds)
        filter_grade: Filter grade for factor adjustment (optional)
                     Can be '', 'none', '00', '0', '1', '2', '3', '4', '5',
                     '2xY', 'Y', 'M1', '2xM1', 'M2', '2xM2'
        paper_id: Paper identifier (e.g., 'ilford_cooltone')

    Returns:
        float: Exposure time in seconds, or None if invalid input
    """
    if lux is None or lux <= 0:
        return None

    base_time = calibration / lux

    # Apply filter factor if specified
    # Empty string or 'none' means no filter (factor = 1.0)
    if filter_grade is not None and filter_grade != '' and filter_grade != 'none':
        if paper_id:
            filter_data = get_filter_data(paper_id, filter_grade)
            if filter_data:
                base_time *= filter_data['factor']

    return base_time


def calculate_virtual_proof_sample(
    lux,
    reference_lux=None,
    paper_id='ilford_cooltone',
    filter_grade=None,
    calibration=1000.0,
):
    """
    Calculate a virtual proof sample (predicted print density/grayscale).

    Models the paper characteristic curve (toe, straight-line, shoulder)
    to predict print density for a given lux reading.

    Args:
        lux: Measured lux at sample point
        reference_lux: Reference (midtone) lux for relative measurement
        paper_id: Paper identifier from paper_database
        filter_grade: Filter grade for gamma selection (optional)
        calibration: Calibration constant (lux × seconds)

    Returns:
        dict: Virtual proof data including density, grayscale, zone, etc.
    """
    if lux is None or lux <= 0:
        return {"error": "Invalid lux"}

    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return {"error": f"Invalid paper_id: {paper_id}"}

    curve = paper_data.get("characteristic_curve", {})
    dmin = float(paper_data.get("dmin", 0.05))
    dmax = float(paper_data.get("dmax", 2.0))

    # Get paper base slopes
    base_straight_slope = float(curve.get("straight_slope", 0.7))
    base_toe_slope = float(curve.get("toe_slope", 0.3))
    base_shoulder_slope = float(curve.get("shoulder_slope", 0.15))

    straight_slope = base_straight_slope
    filter_data = get_filter_data(paper_id, filter_grade) if filter_grade else None
    if filter_data:
        if filter_data.get("dmin_effect") is not None:
            dmin = float(filter_data.get("dmin_effect"))
        if filter_data.get("dmax_effect") is not None:
            dmax = float(filter_data.get("dmax_effect"))
        if filter_data.get("gamma"):
            straight_slope = float(filter_data.get("gamma", straight_slope))

    # Gamma-driven slope scaling
    gamma_ratio = straight_slope / base_straight_slope if base_straight_slope > 0 else 1.0
    toe_slope = base_toe_slope * gamma_ratio
    shoulder_slope = base_shoulder_slope * gamma_ratio

    iso_r = None
    if filter_data and filter_data.get("iso_r"):
        iso_r = float(filter_data.get("iso_r"))

    if iso_r is None:
        filters = paper_data.get("filters", {})
        fallback = filters.get("2") if isinstance(filters, dict) else None
        if fallback and fallback.get("iso_r"):
            iso_r = float(fallback.get("iso_r"))
        else:
            for data in (filters or {}).values():
                if data and data.get("iso_r"):
                    iso_r = float(data.get("iso_r"))
                    break

    if iso_r is None:
        iso_r = 100.0

    # ISO R only: derive logE_range from filter ISO R (logE_range = ISO R / 100)
    log10_2 = math.log10(2.0)
    loge_range = iso_r / 100.0
    source_of_loge_range = "iso_r"

    if loge_range <= 0:
        loge_range = 1.6
        source_of_loge_range = "default_fallback"

    printable_ev = loge_range / log10_2

    has_reference = reference_lux is not None and reference_lux > 0
    if has_reference:
        delta_ev = math.log2(lux / reference_lux)
    else:
        delta_ev = 0.0

    zone = 5.0 - delta_ev if has_reference else 5.0
    zone_clamped = max(0.0, min(10.0, zone))

    loge_mid = loge_range * 0.5
    # Cell brighter at paper plane (delta_ev > 0) receives MORE exposure →
    # higher loge → higher density → darker print tone. Earlier code had a
    # sign flip that inverted the entire grayscale rendering.
    loge = loge_mid + delta_ev * log10_2
    loge = max(0.0, min(loge_range, loge))

    toe_end = loge_range * 0.25
    shoulder_start = loge_range * 0.75
    if toe_end <= 0:
        toe_end = loge_range * 0.2
    if shoulder_start <= toe_end:
        shoulder_start = toe_end + (loge_range - toe_end) * 0.5

    # Control points for smooth curve (same anchor densities as before)
    d0 = dmin
    d1 = dmin + toe_slope * toe_end
    d2 = d1 + straight_slope * (shoulder_start - toe_end)
    d3 = d2 + shoulder_slope * (loge_range - shoulder_start)

    def _hermite(t, p0, p1, m0, m1):
        """Cubic Hermite interpolation, monotonic for matching slopes."""
        t2 = t * t
        t3 = t2 * t
        return (2*t3 - 3*t2 + 1)*p0 + (t3 - 2*t2 + t)*m0 + (-2*t3 + 3*t2)*p1 + (t3 - t2)*m1

    def _curve_density(loge_value):
        if loge_value <= 0:
            return d0
        if loge_value >= loge_range:
            return d3
        if loge_value <= toe_end:
            seg_len = toe_end
            t = loge_value / seg_len if seg_len > 0 else 0
            return _hermite(t, d0, d1, toe_slope * seg_len, straight_slope * seg_len)
        if loge_value <= shoulder_start:
            seg_len = shoulder_start - toe_end
            t = (loge_value - toe_end) / seg_len if seg_len > 0 else 0
            return _hermite(t, d1, d2, straight_slope * seg_len, straight_slope * seg_len)
        seg_len = loge_range - shoulder_start
        t = (loge_value - shoulder_start) / seg_len if seg_len > 0 else 0
        return _hermite(t, d2, d3, straight_slope * seg_len, shoulder_slope * seg_len)

    density_raw = _curve_density(loge)
    density_at_max = _curve_density(loge_range)
    denom = density_at_max - dmin
    if denom <= 0:
        density = dmin
    else:
        scale = (dmax - dmin) / denom
        density = dmin + (density_raw - dmin) * scale

    if density < dmin:
        density = dmin
    if density > dmax:
        density = dmax

    density_range = dmax - dmin
    if density_range <= 0:
        grayscale = 127
    else:
        normalized = (density - dmin) / density_range
        grayscale = int(round(255 * (1.0 - normalized)))

    if grayscale < 0:
        grayscale = 0
    if grayscale > 255:
        grayscale = 255

    clipped_white = density <= dmin + 0.04
    clipped_black = density >= dmax - 0.05

    # Compute exposure time for this cell
    filter_factor = filter_data['factor'] if filter_data and 'factor' in filter_data else 1.0
    exposure_time = round((calibration / lux) * filter_factor, 2) if calibration and lux > 0 else None

    return {
        "paper_id": paper_id,
        "filter_grade": filter_grade or "",
        "lux": lux,
        "reference_lux": reference_lux if has_reference else None,
        "delta_ev": delta_ev,
        "zone": zone,
        "zone_clamped": zone_clamped,
        "logE": loge,
        "logE_mid": loge_mid,
        "logE_range": loge_range,
        "density": density,
        "grayscale": grayscale,
        "clipped_white": clipped_white,
        "clipped_black": clipped_black,
        "gamma": straight_slope,
        "dmin": dmin,
        "dmax": dmax,
        "iso_r": iso_r,
        "printable_ev": printable_ev,
        "calibration": calibration,
        "exposure_time": exposure_time,
        "source_of_loge_range": source_of_loge_range,
    }


def recommend_filter_grade(delta_ev, paper_id='ilford_cooltone'):
    """
    Recommend filter grade based on measured contrast.

    ISO R METHOD: Convert measured contrast to ISO Range (R) and
    match to the closest filter ISO R value for the selected paper.

    Args:
        delta_ev: Measured contrast range (EV stops)
        paper_id: Paper identifier (defaults to 'ilford_cooltone')

    Returns:
        dict: {
            'grade': str,           # Recommended filter grade
            'iso_r': int,           # ISO R value
            'factor': float,        # Exposure factor
            'match_quality': str,   # 'exact', 'close', 'acceptable', 'approximate'
            'reasoning': str        # Why this grade was selected
        }
    """
    if delta_ev is None:
        return None

    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return None

    # ISO R target: delta_ev * 0.30 (log density) * 100
    iso_r_target = abs(delta_ev) * 30.0

    best_match = None
    best_diff = float('inf')
    min_iso_r = float('inf')
    max_iso_r = float('-inf')

    available_filters = get_available_filters(paper_id)

    for grade in available_filters:
        if grade == '' or grade == 'none':
            continue

        filter_data = get_filter_data(paper_id, grade)
        if not filter_data:
            continue

        iso_r = filter_data.get('iso_r')
        if iso_r is None:
            continue

        if iso_r < min_iso_r:
            min_iso_r = iso_r
        if iso_r > max_iso_r:
            max_iso_r = iso_r

        diff = abs(iso_r_target - iso_r)
        if diff < best_diff:
            best_diff = diff
            best_match = {
                'grade': grade,
                'iso_r': iso_r,
                'factor': filter_data.get('factor', 1.0)
            }

    if best_match is None:
        return None

    if best_diff <= 5:
        match_quality = 'exact'
    elif best_diff <= 15:
        match_quality = 'close'
    elif best_diff <= 30:
        match_quality = 'acceptable'
    else:
        match_quality = 'approximate'

    out_of_range = None
    if iso_r_target > max_iso_r:
        out_of_range = 'too_flat'
    elif iso_r_target < min_iso_r:
        out_of_range = 'too_contrasty'

    best_match['match_quality'] = match_quality
    best_match['out_of_range'] = out_of_range

    reasoning = (
        f"ISO R target {iso_r_target:.0f} matches grade {best_match['grade']} "
        f"(ISO R {best_match['iso_r']}) with a {best_diff:.0f} difference"
    )
    if out_of_range == 'too_contrasty':
        reasoning += (
            f"; negative exceeds paper range (min ISO R {min_iso_r:.0f}) — "
            f"consider split-grade printing, pre-flashing, or dodging/burning"
        )
    elif out_of_range == 'too_flat':
        reasoning += (
            f"; negative is flatter than paper range (max ISO R {max_iso_r:.0f}) — "
            f"softest grade will still print with reduced contrast"
        )
    best_match['reasoning'] = reasoning

    return best_match


def calculate_midpoint_exposure_time(
    highlight_lux,
    shadow_lux,
    recommended_grade,
    calibration=1000.0,
):
    """
    Calculate exposure time from the mid-point (gray) lux.

    The midpoint lux is the geometric mean of highlight and shadow.
    Exposure time follows the Exposure Meter formula then applies
    the recommended filter factor.

    Args:
        highlight_lux: Measured lux at highlight area
        shadow_lux: Measured lux at shadow area
        recommended_grade: Output from recommend_filter_grade()
        calibration: Calibration constant (lux × seconds)

    Returns:
        dict: {
            'suggested_time': float,
            'midpoint_lux': float,
            'notes': str
        }
    """
    if not highlight_lux or not shadow_lux:
        return None

    lux_mid = math.sqrt(highlight_lux * shadow_lux)
    if lux_mid <= 0:
        return None

    filter_factor = recommended_grade.get(
        'factor',
        recommended_grade.get('filter_factor', 1.0)
    )

    suggested_time = (calibration / lux_mid) * filter_factor

    return {
        'suggested_time': round(suggested_time, 2),
        'midpoint_lux': round(lux_mid, 2),
        'notes': (
            "Midpoint exposure based on highlight/shadow geometric mean, "
            "using calibration constant and filter factor."
        ),
    }


def validate_paper_database_loge_range():
    """
    Validate that all papers in the database have logE_range defined.

    Returns:
        dict: {
            'total_papers': int,
            'papers_with_loge_range': int,
            'missing_loge_range': list,
            'all_valid': bool
        }
    """
    total = len(PAPER_DATABASE)
    valid_count = 0
    missing = []

    for paper_id, paper_data in PAPER_DATABASE.items():
        curve = paper_data.get("characteristic_curve", {})
        loge_range = curve.get("logE_range")

        if loge_range is None or loge_range <= 0:
            missing.append(paper_id)
        else:
            valid_count += 1

    result = {
        'total_papers': total,
        'papers_with_loge_range': valid_count,
        'missing_loge_range': missing,
        'all_valid': len(missing) == 0
    }

    if not result['all_valid']:
        missing_str = ', '.join(missing)
        print(
            f"WARNING: {len(missing)} paper(s) missing logE_range: {missing_str}",
            file=sys.stderr
        )

    return result
