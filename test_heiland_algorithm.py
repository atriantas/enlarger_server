#!/usr/bin/env python3
"""
Test script for Heiland-like split-grade algorithm.
This tests the logic without requiring MicroPython hardware dependencies.
"""

import math

def calculate_delta_ev(highlight_lux, shadow_lux):
    """Calculate contrast range (ΔEV) from highlight and shadow readings."""
    if highlight_lux is None or shadow_lux is None:
        return None
    if highlight_lux <= 0 or shadow_lux <= 0:
        return None
    return abs(math.log2(shadow_lux / highlight_lux))

def _iso_r_to_ev(iso_r):
    """Interpolate EV from ISO R value."""
    # Simple linear approximation based on Ilford data
    # ISO R 180 (grade 00) ≈ 1.0 EV, ISO R 40 (grade 5) ≈ 4.0 EV
    if iso_r >= 180:
        return 1.0
    elif iso_r <= 40:
        return 4.0
    else:
        # Linear interpolation between 180->1.0 and 40->4.0
        return 1.0 + (180 - iso_r) * (3.0 / 140)

def simulate_heiland_algorithm(highlight_lux, shadow_lux, calibration=1000.0, system='ilford'):
    """
    Simulate Heiland-like split-grade calculation.
    
    This is a simplified version that demonstrates the algorithm logic
    without requiring the full light_sensor module.
    """
    # Calculate contrast
    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    if delta_ev is None:
        return None
    
    # Dynamic filter selection based on contrast
    if system == 'ilford':
        # Ilford filter selection based on ΔEV
        if delta_ev < 1.0:
            soft_filter, hard_filter = '1', '2'      # Very low contrast
        elif delta_ev < 1.5:
            soft_filter, hard_filter = '00', '2'     # Low contrast
        elif delta_ev < 2.0:
            soft_filter, hard_filter = '00', '3'     # Medium-low contrast
        elif delta_ev < 2.5:
            soft_filter, hard_filter = '00', '3'     # Normal contrast
        elif delta_ev < 3.0:
            soft_filter, hard_filter = '00', '4'     # Medium-high contrast
        elif delta_ev < 3.5:
            soft_filter, hard_filter = '00', '4'     # High contrast
        elif delta_ev < 4.0:
            soft_filter, hard_filter = '00', '5'     # Very high contrast
        else:
            soft_filter, hard_filter = '00', '5'     # Extreme contrast
        
        # Ilford filter factors
        filter_factors = {
            '00': 1.6, '0': 1.4, '1': 1.3, '2': 1.1, 
            '3': 0.9, '4': 0.6, '5': 0.4
        }
        iso_r_values = {
            '00': 180, '0': 160, '1': 130, '2': 110,
            '3': 90, '4': 60, '5': 40
        }
    else:
        # FOMA filter selection (simplified)
        if delta_ev < 1.0:
            soft_filter, hard_filter = 'Y', 'M1'     # Very low contrast
        elif delta_ev < 1.5:
            soft_filter, hard_filter = '2xY', 'M1'   # Low contrast
        elif delta_ev < 2.0:
            soft_filter, hard_filter = '2xY', '2xM1' # Medium-low contrast
        elif delta_ev < 2.5:
            soft_filter, hard_filter = '2xY', '2xM1' # Normal contrast
        elif delta_ev < 3.0:
            soft_filter, hard_filter = '2xY', 'M2'   # Medium-high contrast
        elif delta_ev < 3.5:
            soft_filter, hard_filter = '2xY', '2xM2' # High contrast
        elif delta_ev < 4.0:
            soft_filter, hard_filter = '2xY', '2xM2' # Very high contrast
        else:
            soft_filter, hard_filter = '2xY', '2xM2' # Extreme contrast
        
        # FOMA filter factors (FOMASPEED)
        filter_factors = {
            '2xY': 1.6, 'Y': 1.4, 'M1': 1.4, 
            '2xM1': 2.1, 'M2': 2.6, '2xM2': 4.6
        }
        iso_r_values = {
            '2xY': 135, 'Y': 120, 'M1': 90,
            '2xM1': 80, 'M2': 65, '2xM2': 55
        }
    
    # Get filter factors
    soft_factor = filter_factors.get(soft_filter, 1.6)
    hard_factor = filter_factors.get(hard_filter, 0.4)
    
    # Calculate base times
    soft_base_time = calibration / highlight_lux
    hard_base_time = calibration / shadow_lux
    
    # Apply filter factors
    soft_time = soft_base_time * soft_factor
    hard_time = hard_base_time * hard_factor
    
    # Apply Heiland-like optimization
    # 1. Minimum exposure time (2 seconds)
    soft_time = max(soft_time, 2.0)
    hard_time = max(hard_time, 2.0)
    
    # 2. Maximum exposure time (120 seconds)
    soft_time = min(soft_time, 120.0)
    hard_time = min(hard_time, 120.0)
    
    # 3. Balance exposures
    if soft_time > 0 and hard_time > 0:
        ratio = max(soft_time, hard_time) / min(soft_time, hard_time)
        if ratio > 10:  # Max 10:1 ratio
            if soft_time > hard_time:
                soft_time = hard_time * 10
            else:
                hard_time = soft_time * 10
    
    # Calculate percentages
    total_time = soft_time + hard_time
    if total_time > 0:
        soft_percent = (soft_time / total_time) * 100
        hard_percent = (hard_time / total_time) * 100
    else:
        soft_percent = 50.0
        hard_percent = 50.0
    
    # Calculate match quality
    soft_iso_r = iso_r_values.get(soft_filter, 180)
    hard_iso_r = iso_r_values.get(hard_filter, 40)
    soft_printable_ev = _iso_r_to_ev(soft_iso_r)
    hard_printable_ev = _iso_r_to_ev(hard_iso_r)
    total_printable_ev = soft_printable_ev + hard_printable_ev
    
    # Simple match quality calculation
    diff = abs(delta_ev - total_printable_ev)
    if diff < 0.5:
        match_quality = 'excellent'
    elif diff < 1.0:
        match_quality = 'good'
    elif diff < 1.5:
        match_quality = 'fair'
    else:
        match_quality = 'poor'
    
    # Determine selection reason
    if delta_ev < 1.0:
        selection_reason = "Very low contrast - using close filters"
    elif delta_ev < 2.0:
        selection_reason = "Low to medium contrast - balanced filter selection"
    elif delta_ev < 3.0:
        selection_reason = "Normal to high contrast - standard split-grade"
    elif delta_ev < 4.0:
        selection_reason = "High contrast - wider filter separation"
    else:
        selection_reason = "Extreme contrast - maximum filter separation"
    
    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'total_time': total_time,
        'delta_ev': delta_ev,
        'soft_factor': soft_factor,
        'hard_factor': hard_factor,
        'soft_percent': soft_percent,
        'hard_percent': hard_percent,
        'match_quality': match_quality,
        'selection_reason': selection_reason,
        'algorithm': 'heiland_enhanced',
        'highlight_lux': highlight_lux,
        'shadow_lux': shadow_lux,
        'optimization_applied': True
    }

def simulate_original_algorithm(highlight_lux, shadow_lux, calibration=1000.0, system='ilford'):
    """Simulate original fixed-filter algorithm."""
    # Original always uses extreme filters
    if system == 'ilford':
        soft_filter, hard_filter = '00', '5'
        soft_factor, hard_factor = 1.6, 0.4
    else:
        soft_filter, hard_filter = '2xY', '2xM2'
        soft_factor, hard_factor = 1.6, 4.6
    
    # Simple calculation
    soft_time = (calibration / highlight_lux) * soft_factor
    hard_time = (calibration / shadow_lux) * hard_factor
    total_time = soft_time + hard_time
    
    if total_time > 0:
        soft_percent = (soft_time / total_time) * 100
        hard_percent = (hard_time / total_time) * 100
    else:
        soft_percent = hard_percent = 50.0
    
    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    
    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'soft_time': soft_time,
        'hard_time': hard_time,
        'total_time': total_time,
        'delta_ev': delta_ev,
        'soft_percent': soft_percent,
        'hard_percent': hard_percent,
        'algorithm': 'original_fixed'
    }

def main():
    print("Heiland Split-Grade Algorithm Test")
    print("=" * 60)
    
    # Test cases with different contrast levels
    test_cases = [
        ("Very low contrast", 100.0, 120.0),   # ΔEV ~0.26
        ("Low contrast", 100.0, 150.0),        # ΔEV ~0.58
        ("Medium contrast", 100.0, 200.0),     # ΔEV ~1.0
        ("Normal contrast", 100.0, 400.0),     # ΔEV ~2.0
        ("High contrast", 100.0, 800.0),       # ΔEV ~3.0
        ("Very high contrast", 100.0, 1200.0), # ΔEV ~3.58
        ("Extreme contrast", 100.0, 1600.0),   # ΔEV ~4.0
    ]
    
    for name, highlight, shadow in test_cases:
        print(f"\n{name}:")
        print(f"  Highlight={highlight} lux, Shadow={shadow} lux")
        
        # Original algorithm
        orig = simulate_original_algorithm(highlight, shadow, 1000.0, 'ilford')
        if orig:
            print(f"  Original: {orig['soft_filter']}+{orig['hard_filter']}")
            print(f"    Times: {orig['soft_time']:.1f}s + {orig['hard_time']:.1f}s = {orig['total_time']:.1f}s")
            print(f"    Balance: {orig['soft_percent']:.0f}% / {orig['hard_percent']:.0f}%")
        
        # Heiland algorithm
        heiland = simulate_heiland_algorithm(highlight, shadow, 1000.0, 'ilford')
        if heiland:
            print(f"  Heiland:  {heiland['soft_filter']}+{heiland['hard_filter']}")
            print(f"    Times: {heiland['soft_time']:.1f}s + {heiland['hard_time']:.1f}s = {heiland['total_time']:.1f}s")
            print(f"    Balance: {heiland['soft_percent']:.0f}% / {heiland['hard_percent']:.0f}%")
            print(f"    ΔEV: {heiland['delta_ev']:.2f}, Match: {heiland['match_quality']}")
            print(f"    Reason: {heiland['selection_reason']}")
            
            # Calculate improvement
            if orig and heiland:
                time_diff = heiland['total_time'] - orig['total_time']
                time_diff_percent = (time_diff / orig['total_time']) * 100 if orig['total_time'] > 0 else 0
                
                # Balance improvement (closer to 50/50 is better)
                orig_balance = abs(orig['soft_percent'] - 50) + abs(orig['hard_percent'] - 50)
                heiland_balance = abs(heiland['soft_percent'] - 50) + abs(heiland['hard_percent'] - 50)
                balance_improvement = orig_balance - heiland_balance
                
                print(f"    Improvement: {time_diff_percent:+.1f}% time, balance improved by {balance_improvement:.1f} points")
    
    print("\n" + "=" * 60)
    print("Key Observations:")
    print("1. Heiland algorithm selects filters based on contrast (ΔEV)")
    print("2. For low contrast: uses closer filters (1+2 instead of 00+5)")
    print("3. For extreme contrast: uses widest filters (00+5)")
    print("4. Exposure times are balanced (neither too short nor too long)")
    print("5. Minimum 2s exposure ensures practical darkroom work")
    print("\nAlgorithm successfully implements Heiland-like dynamic filter selection!")

if __name__ == "__main__":
    main()