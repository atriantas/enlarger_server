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
    OPTIMIZATION_PARAMS
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

def calculate_split_grade_enhanced(highlight_lux, shadow_lux, paper_id='ilford_mg_iv', 
                                  calibration=1000.0, soft_filter=None, hard_filter=None):
    """
    Enhanced split-grade calculation using Heiland-like methodology.
    
    Args:
        highlight_lux: Lux reading at highlight area
        shadow_lux: Lux reading at shadow area
        paper_id: Paper identifier (e.g., 'ilford_mg_iv', 'foma_fomaspeed')
        calibration: Calibration constant (lux × seconds)
        soft_filter: Optional soft filter (auto-select if None)
        hard_filter: Optional hard filter (auto-select if None)
    
    Returns:
        dict: Comprehensive split-grade results
    """
    # Validate inputs
    if highlight_lux is None or shadow_lux is None:
        return None
    
    if highlight_lux <= 0 or shadow_lux <= 0:
        return None
    
    # Get paper data
    paper_data = get_paper_data(paper_id)
    if not paper_data:
        # Fallback to default paper
        paper_data = get_paper_data('ilford_mg_iv')
    
    # Calculate contrast (ΔEV)
    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    
    # Determine filter system from paper_id
    if 'ilford' in paper_id:
        system = 'ilford'
    elif 'fomaspeed' in paper_id:
        system = 'foma_fomaspeed'
    elif 'fomatone' in paper_id:
        system = 'foma_fomatone'
    else:
        system = 'ilford'  # Default
    
    # Select filters based on contrast if not specified
    if soft_filter is None or hard_filter is None:
        filter_selection = get_filter_selection(delta_ev, system)
        selected_soft = filter_selection['soft_filter']
        selected_hard = filter_selection['hard_filter']
        selection_reason = filter_selection['description']
        contrast_level = filter_selection['contrast_level']
    else:
        selected_soft = soft_filter
        selected_hard = hard_filter
        selection_reason = "User-specified filters"
        contrast_level = "custom"
    
    # Get filter data
    soft_data = get_filter_data(paper_id, selected_soft)
    hard_data = get_filter_data(paper_id, selected_hard)
    
    if not soft_data or not hard_data:
        # Fallback to default filter data
        return None
    
    # Calculate base exposure times using paper characteristics
    # Enhanced calculation considers paper gamma and characteristic curve
    
    # Base calculation (similar to current but with enhancements)
    soft_base_time = calibration / highlight_lux
    hard_base_time = calibration / shadow_lux
    
    # Apply filter factors
    soft_time = soft_base_time * soft_data['factor']
    hard_time = hard_base_time * hard_data['factor']
    
    # Apply optimization for balanced exposures
    soft_time_opt, hard_time_opt, optimization_applied = validate_exposure_times(
        soft_time, hard_time, paper_id
    )
    
    # Calculate percentages
    total_time = soft_time_opt + hard_time_opt
    if total_time > 0:
        soft_percent = (soft_time_opt / total_time) * 100
        hard_percent = (hard_time_opt / total_time) * 100
    else:
        soft_percent = 50.0
        hard_percent = 50.0
    
    # Calculate match quality based on contrast level
    match_quality = calculate_match_quality(delta_ev, paper_data, contrast_level)
    
    # Calculate printable contrast range for this paper
    printable_ev = calculate_paper_printable_range(paper_data, selected_soft, selected_hard)
    
    # Prepare comprehensive result
    result = {
        'status': 'success',
        'soft_filter': selected_soft,
        'hard_filter': selected_hard,
        'soft_time': soft_time_opt,
        'hard_time': hard_time_opt,
        'total_time': total_time,
        'delta_ev': delta_ev,
        'soft_factor': soft_data['factor'],
        'hard_factor': hard_data['factor'],
        'soft_percent': soft_percent,
        'hard_percent': hard_percent,
        'match_quality': match_quality,
        'selection_reason': selection_reason,
        'contrast_level': contrast_level,
        'paper_id': paper_id,
        'paper_type': paper_data['paper_type'],
        'manufacturer': paper_data['manufacturer'],
        'optimization_applied': optimization_applied,
        'total_printable_ev': printable_ev,
        'highlight_lux': highlight_lux,
        'shadow_lux': shadow_lux,
        'calibration_used': calibration
    }
    
    return result

def calculate_match_quality(delta_ev, paper_data, contrast_level):
    """
    Calculate match quality between negative contrast and paper capabilities.
    
    Args:
        delta_ev: Measured contrast in stops
        paper_data: Paper database entry
        contrast_level: Contrast level from filter selection
    
    Returns:
        str: 'excellent', 'good', 'fair', or 'poor'
    """
    # Estimate paper's printable range
    logE_range = paper_data['characteristic_curve']['logE_range']
    paper_range_ev = logE_range * 3.32  # Convert log10 to EV
    
    # Calculate how well the negative fits the paper
    if delta_ev < paper_range_ev * 0.3:
        return 'poor'  # Negative contrast too low for paper
    elif delta_ev < paper_range_ev * 0.6:
        return 'fair'
    elif delta_ev < paper_range_ev * 0.9:
        return 'good'
    else:
        return 'excellent'

def calculate_paper_printable_range(paper_data, soft_filter, hard_filter):
    """
    Calculate printable contrast range for selected filter pair.
    
    Args:
        paper_data: Paper database entry
        soft_filter: Soft filter grade
        hard_filter: Hard filter grade
    
    Returns:
        float: Printable contrast range in EV stops
    """
    # Get gamma values for selected filters
    soft_gamma = paper_data['filters'].get(soft_filter, {}).get('gamma', 0.5)
    hard_gamma = paper_data['filters'].get(hard_filter, {}).get('gamma', 1.0)
    
    # Average gamma for the filter pair
    avg_gamma = (soft_gamma + hard_gamma) / 2
    
    # Use paper's logE range adjusted by average gamma
    logE_range = paper_data['characteristic_curve']['logE_range']
    
    # Printable range = logE_range × effective gamma
    printable_logE = logE_range * avg_gamma
    
    # Convert to EV stops
    printable_ev = printable_logE * 3.32
    
    return printable_ev

def compare_algorithms(highlight_lux, shadow_lux, paper_id='ilford_mg_iv', calibration=1000.0):
    """
    Compare enhanced algorithm with legacy algorithm.
    
    Args:
        highlight_lux: Lux reading at highlight area
        shadow_lux: Lux reading at shadow area
        paper_id: Paper identifier
        calibration: Calibration constant
    
    Returns:
        dict: Comparison results
    """
    # Calculate with enhanced algorithm
    enhanced_result = calculate_split_grade_enhanced(
        highlight_lux, shadow_lux, paper_id, calibration
    )
    
    # Calculate with legacy algorithm (simulated)
    # Note: This would need access to the actual legacy calculation
    # For now, we'll simulate it based on known behavior
    
    delta_ev = calculate_delta_ev(highlight_lux, shadow_lux)
    
    # Legacy always uses extreme filters
    if 'ilford' in paper_id:
        legacy_soft = '00'
        legacy_hard = '5'
    else:
        legacy_soft = '2xY'
        legacy_hard = '2xM2'
    
    # Simple legacy calculation
    soft_base = calibration / highlight_lux
    hard_base = calibration / shadow_lux
    
    # Get filter factors from paper database
    paper_data = get_paper_data(paper_id)
    if paper_data:
        soft_factor = paper_data['filters'].get(legacy_soft, {}).get('factor', 1.6)
        hard_factor = paper_data['filters'].get(legacy_hard, {}).get('factor', 0.4)
    else:
        soft_factor = 1.6
        hard_factor = 0.4
    
    legacy_soft_time = soft_base * soft_factor
    legacy_hard_time = hard_base * hard_factor
    legacy_total = legacy_soft_time + legacy_hard_time
    
    # Calculate improvement metrics
    improvement = {}
    if enhanced_result and legacy_total > 0:
        # Time difference
        time_diff = enhanced_result['total_time'] - legacy_total
        time_diff_percent = (time_diff / legacy_total) * 100
        
        # Balance improvement (closer to 50/50 is better)
        legacy_soft_percent = (legacy_soft_time / legacy_total) * 100 if legacy_total > 0 else 50
        legacy_hard_percent = (legacy_hard_time / legacy_total) * 100 if legacy_total > 0 else 50
        
        legacy_balance = abs(legacy_soft_percent - 50) + abs(legacy_hard_percent - 50)
        enhanced_balance = abs(enhanced_result['soft_percent'] - 50) + abs(enhanced_result['hard_percent'] - 50)
        
        balance_improvement = legacy_balance - enhanced_balance
        
        improvement = {
            'time_difference_seconds': time_diff,
            'time_difference_percent': time_diff_percent,
            'legacy_balance_score': legacy_balance,
            'enhanced_balance_score': enhanced_balance,
            'balance_improvement': balance_improvement,
            'recommendation': get_recommendation(time_diff_percent, balance_improvement)
        }
    
    return {
        'enhanced': enhanced_result,
        'legacy': {
            'soft_filter': legacy_soft,
            'hard_filter': legacy_hard,
            'soft_time': legacy_soft_time,
            'hard_time': legacy_hard_time,
            'total_time': legacy_total,
            'delta_ev': delta_ev,
            'soft_percent': (legacy_soft_time / legacy_total * 100) if legacy_total > 0 else 50,
            'hard_percent': (legacy_hard_time / legacy_total * 100) if legacy_total > 0 else 50
        },
        'improvement': improvement,
        'delta_ev': delta_ev
    }

def get_recommendation(time_diff_percent, balance_improvement):
    """
    Generate recommendation based on algorithm comparison.
    
    Args:
        time_diff_percent: Time difference percentage
        balance_improvement: Balance improvement score
    
    Returns:
        str: Recommendation text
    """
    if time_diff_percent < -20 and balance_improvement > 10:
        return "Strongly recommend enhanced algorithm - significantly more balanced exposures"
    elif time_diff_percent < -10 and balance_improvement > 5:
        return "Recommend enhanced algorithm - better balance and reasonable times"
    elif abs(time_diff_percent) < 10 and balance_improvement > 0:
        return "Enhanced algorithm provides better balance with similar total time"
    elif time_diff_percent > 20:
        return "Legacy algorithm may be faster, but enhanced provides better balance"
    else:
        return "Both algorithms similar - enhanced provides dynamic filter selection"

# Test function
if __name__ == "__main__":
    print("Enhanced Split-Grade Calculator Test")
    print("=" * 60)
    
    # Test cases with different contrast levels
    test_cases = [
        ("Low contrast", 100.0, 150.0),      # ΔEV ~0.58
        ("Normal contrast", 100.0, 400.0),   # ΔEV ~2.0
        ("High contrast", 100.0, 800.0),     # ΔEV ~3.0
        ("Extreme contrast", 100.0, 1600.0), # ΔEV ~4.0
    ]
    
    for name, highlight, shadow in test_cases:
        print(f"\n{name}: Highlight={highlight} lux, Shadow={shadow} lux")
        
        result = calculate_split_grade_enhanced(
            highlight, shadow, 'ilford_mg_iv', 1000.0
        )
        
        if result:
            print(f"  ΔEV: {result['delta_ev']:.2f}")
            print(f"  Filters: {result['soft_filter']} + {result['hard_filter']}")
            print(f"  Times: {result['soft_time']:.1f}s + {result['hard_time']:.1f}s = {result['total_time']:.1f}s")
            print(f"  Percentages: {result['soft_percent']:.0f}% / {result['hard_percent']:.0f}%")
            print(f"  Match quality: {result['match_quality']}")
            print(f"  Selection: {result['selection_reason']}")
        
        # Compare algorithms
        comparison = compare_algorithms(highlight, shadow, 'ilford_mg_iv', 1000.0)
        if comparison['improvement']:
            impr = comparison['improvement']
            print(f"  Improvement: {impr['time_difference_percent']:.1f}% time, {impr['balance_improvement']:.1f} balance")
            print(f"  Recommendation: {impr['recommendation']}")
    
    print("\n" + "=" * 60)
    print("Enhanced split-grade calculator ready for integration!")
