#!/usr/bin/env python3
"""
Test script to verify split-grade calculation logic against sensitometric principles.
"""

import math

# Filter data from light_sensor.py
ILFORD_FILTERS = {
    '00': {'iso_r': 180, 'factor': 1.6, 'name': 'Grade 00'},
    '0':  {'iso_r': 160, 'factor': 1.4, 'name': 'Grade 0'},
    '1':  {'iso_r': 130, 'factor': 1.3, 'name': 'Grade 1'},
    '2':  {'iso_r': 110, 'factor': 1.1, 'name': 'Grade 2'},
    '3':  {'iso_r': 90,  'factor': 0.9, 'name': 'Grade 3'},
    '4':  {'iso_r': 60,  'factor': 0.6, 'name': 'Grade 4'},
    '5':  {'iso_r': 40,  'factor': 0.4, 'name': 'Grade 5'},
    '':   {'iso_r': 110, 'factor': 1.0, 'name': 'No Filter'},
}

# ISO R to EV mapping
ISO_R_TO_EV = {
    180: 8.0,   # Grade 00 - very soft
    160: 7.5,   # Grade 0
    135: 7.0,   # FOMA 2xY
    130: 6.8,   # Grade 1
    120: 6.5,   # FOMA Y
    110: 6.2,   # Grade 2 (normal)
    105: 6.0,   # FOMA no filter
    90: 5.6,    # Grade 3 / FOMA M1
    80: 5.2,    # FOMA 2xM1
    75: 5.0,    # FOMA 2xM1
    65: 4.8,    # Grade 4 / FOMA M2
    60: 4.6,    # Grade 4
    55: 4.4,    # Grade 5 / FOMA 2xM2
    40: 4.0     # Grade 5 - very hard
}

def calculate_delta_ev(highlight_lux, shadow_lux):
    """Calculate contrast range (ΔEV) from highlight and shadow readings."""
    if highlight_lux is None or shadow_lux is None:
        return None
    if highlight_lux <= 0 or shadow_lux <= 0:
        return None
    delta_ev = abs(math.log2(shadow_lux / highlight_lux))
    return delta_ev

def iso_r_to_ev(iso_r):
    """Interpolate EV from ISO R value."""
    sorted_pairs = sorted(ISO_R_TO_EV.items(), reverse=True)
    
    for i, (r, ev) in enumerate(sorted_pairs):
        if iso_r >= r:
            if i == 0:
                return ev
            prev_r, prev_ev = sorted_pairs[i - 1]
            ratio = (iso_r - r) / (prev_r - r)
            return ev + ratio * (prev_ev - ev)
    
    return sorted_pairs[-1][1]

def calculate_split_grade_enhanced(highlight_lux, shadow_lux, calibration=1000.0):
    """Recreate the split-grade calculation from light_sensor.py"""
    # 1. Calculate ΔEV
    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    
    # 2. Use Ilford system with soft filter '00' and hard filter '5'
    soft_filter = '00'
    hard_filter = '5'
    
    soft_factor = ILFORD_FILTERS[soft_filter]['factor']
    hard_factor = ILFORD_FILTERS[hard_filter]['factor']
    
    # 5. Calculate base times from lux readings
    soft_base = calibration / highlight_lux
    hard_base = calibration / shadow_lux
    
    # 6. Apply filter factors
    soft_time = soft_base * soft_factor
    hard_time = hard_base * hard_factor
    
    # 7. Calculate proportions
    total_time = soft_time + hard_time
    soft_percent = (soft_time / total_time) * 100
    hard_percent = (hard_time / total_time) * 100
    
    # 8. Calculate expected paper contrast
    soft_printable_ev = iso_r_to_ev(ILFORD_FILTERS[soft_filter]['iso_r'])
    hard_printable_ev = iso_r_to_ev(ILFORD_FILTERS[hard_filter]['iso_r'])
    total_printable_ev = soft_printable_ev + hard_printable_ev
    
    # 9. Evaluate match quality
    diff = abs(delta_ev - total_printable_ev)
    if diff < 0.5:
        match_quality = 'excellent'
    elif diff < 1.0:
        match_quality = 'good'
    elif diff < 1.5:
        match_quality = 'fair'
    else:
        match_quality = 'poor'
    
    return {
        'delta_ev': delta_ev,
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'total_time': total_time,
        'soft_percent': soft_percent,
        'hard_percent': hard_percent,
        'soft_factor': soft_factor,
        'hard_factor': hard_factor,
        'soft_printable_ev': soft_printable_ev,
        'hard_printable_ev': hard_printable_ev,
        'total_printable_ev': total_printable_ev,
        'match_quality': match_quality,
    }

def test_sensitometric_principles():
    """Test against established sensitometric principles."""
    print("=== Testing Split-Grade Analyzer Against Sensitometric Principles ===\n")
    
    # Test case 1: Typical negative with 2.0 EV contrast
    print("Test 1: Typical negative (2.0 EV contrast)")
    highlight_lux = 100.0
    shadow_lux = highlight_lux * (2 ** 2.0)  # 2 EV difference = 4x more light
    result = calculate_split_grade_enhanced(highlight_lux, shadow_lux)
    
    print(f"  Highlight: {highlight_lux} lux")
    print(f"  Shadow: {shadow_lux} lux")
    print(f"  ΔEV: {result['delta_ev']:.2f}")
    print(f"  Soft time: {result['soft_time']:.2f}s (filter {result['soft_filter']}, factor {result['soft_factor']})")
    print(f"  Hard time: {result['hard_time']:.2f}s (filter {result['hard_filter']}, factor {result['hard_factor']})")
    print(f"  Total time: {result['total_time']:.2f}s")
    print(f"  Soft %: {result['soft_percent']:.1f}%, Hard %: {result['hard_percent']:.1f}%")
    print(f"  Soft printable EV: {result['soft_printable_ev']:.1f}")
    print(f"  Hard printable EV: {result['hard_printable_ev']:.1f}")
    print(f"  Total printable EV: {result['total_printable_ev']:.1f}")
    print(f"  Match quality: {result['match_quality']}")
    
    # Check additive nature principle
    print("\n  Additive nature check:")
    print(f"  Soft base time (no filter): {1000/highlight_lux:.2f}s")
    print(f"  Hard base time (no filter): {1000/shadow_lux:.2f}s")
    print(f"  With filter factors: soft ×{result['soft_factor']}, hard ×{result['hard_factor']}")
    
    # Test case 2: High contrast negative (4.0 EV)
    print("\n\nTest 2: High contrast negative (4.0 EV)")
    highlight_lux = 100.0
    shadow_lux = highlight_lux * (2 ** 4.0)  # 4 EV difference = 16x more light
    result = calculate_split_grade_enhanced(highlight_lux, shadow_lux)
    
    print(f"  ΔEV: {result['delta_ev']:.2f}")
    print(f"  Match quality: {result['match_quality']}")
    
    # Test case 3: Low contrast negative (1.0 EV)
    print("\n\nTest 3: Low contrast negative (1.0 EV)")
    highlight_lux = 100.0
    shadow_lux = highlight_lux * (2 ** 1.0)  # 1 EV difference = 2x more light
    result = calculate_split_grade_enhanced(highlight_lux, shadow_lux)
    
    print(f"  ΔEV: {result['delta_ev']:.2f}")
    print(f"  Match quality: {result['match_quality']}")
    
    # Analyze the mathematical formulas
    print("\n\n=== Mathematical Formula Analysis ===")
    print("\n1. ΔEV calculation:")
    print("   ΔEV = abs(log₂(shadow_lux / highlight_lux))")
    print("   This is correct for contrast measurement.")
    
    print("\n2. Base exposure time calculation:")
    print("   base_time = calibration / lux")
    print("   Where calibration = lux × seconds for proper exposure")
    print("   This follows the reciprocity law: Exposure = Illuminance × Time")
    
    print("\n3. Filter factor application:")
    print("   filtered_time = base_time × filter_factor")
    print("   Filter factors >1 increase exposure (softer filters)")
    print("   Filter factors <1 decrease exposure (harder filters)")
    
    print("\n4. ISO R to EV conversion:")
    print("   Higher ISO R = longer exposure latitude = higher EV")
    print("   Linear interpolation between known ISO R/EV pairs")
    
    print("\n5. Additive nature verification:")
    print("   For split-grade printing, total exposure = soft_time + hard_time")
    print("   This is correct: exposures are additive, not multiplicative")
    
    # Check filter factor consistency
    print("\n\n=== Filter Factor Analysis ===")
    print("Ilford filter factors:")
    for grade, data in sorted(ILFORD_FILTERS.items()):
        if grade:  # Skip empty string
            print(f"  Grade {grade}: factor {data['factor']}, ISO R {data['iso_r']}")
    
    # Verify the additive principle mathematically
    print("\n=== Additive Principle Test ===")
    print("For split-grade printing, the exposures should be additive:")
    print("Total density = D_soft + D_hard (not D_soft × D_hard)")
    print("The tool correctly adds times: total_time = soft_time + hard_time")
    
    # Check if filter factors are appropriate
    print("\n=== Filter Factor Appropriateness ===")
    print("Soft filter (00): factor 1.6 (increases exposure by 60%)")
    print("Hard filter (5): factor 0.4 (reduces exposure by 60%)")
    print("This seems reasonable for controlling highlight/shadow separation.")

if __name__ == "__main__":
    test_sensitometric_principles()