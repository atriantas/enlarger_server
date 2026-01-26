"""
Enhanced Paper Database for Split-Grade Analyzer

This module provides an enhanced paper database structure with manufacturer data
for Ilford and FOMA papers, supporting Heiland-like split-grade calculations.

Based on research into Heiland Splitgrade Controller methodology and
manufacturer documentation from Ilford and FOMA.
"""

# Enhanced paper database structure with manufacturer data
# Note: Some values are estimated based on current implementation and will be
# updated with actual manufacturer data from documentation

PAPER_DATABASE = {
    # Ilford Multigrade IV RC - Based on current implementation
    'ilford_mg_iv': {
        'manufacturer': 'Ilford',
        'paper_type': 'Multigrade IV RC',
        'base_iso_p': 100,  # Estimated ISO P value
        'dmin': 0.05,       # Base + fog density
        'dmax': 2.10,       # Maximum density
        'exposure_latitude': 1.8,  # Stops
        'filters': {
            '00': {
                'factor': 1.6,
                'iso_r': 180,
                'gamma': 0.4,      # Estimated gamma value
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.8,
                'description': 'Very soft - highlights only'
            },
            '0': {
                'factor': 1.4,
                'iso_r': 160,
                'gamma': 0.5,
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 1.9,
                'description': 'Soft'
            },
            '1': {
                'factor': 1.3,
                'iso_r': 130,
                'gamma': 0.6,
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.0,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 1.1,
                'iso_r': 110,
                'gamma': 0.7,
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.05,
                'description': 'Normal'
            },
            '3': {
                'factor': 0.9,
                'iso_r': 90,
                'gamma': 0.8,
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.08,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 0.6,
                'iso_r': 60,
                'gamma': 0.9,
                'contrast_index': 1.3,
                'dmin_effect': 0.09,
                'dmax_effect': 2.09,
                'description': 'Hard'
            },
            '5': {
                'factor': 0.4,
                'iso_r': 40,
                'gamma': 1.0,
                'contrast_index': 1.4,
                'dmin_effect': 0.10,
                'dmax_effect': 2.10,
                'description': 'Very hard - shadows only'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.2,
            'straight_slope': 0.7,
            'shoulder_slope': 0.1,
            'logE_range': 1.8,
            'speed_point': 0.6  # Density above Dmin for speed measurement
        }
    },
    
    # FOMA FOMASPEED Variant III - Based on current implementation
    'foma_fomaspeed': {
        'manufacturer': 'FOMA',
        'paper_type': 'FOMASPEED Variant III',
        'base_iso_p': 80,
        'dmin': 0.06,
        'dmax': 2.05,
        'exposure_latitude': 1.7,
        'filters': {
            '2xY': {
                'factor': 1.6,
                'iso_r': 135,
                'gamma': 0.4,
                'contrast_index': 0.8,
                'dmin_effect': 0.06,
                'dmax_effect': 1.8,
                'description': '2×Y (Very soft)'
            },
            'Y': {
                'factor': 1.4,
                'iso_r': 120,
                'gamma': 0.5,
                'contrast_index': 0.9,
                'dmin_effect': 0.06,
                'dmax_effect': 1.9,
                'description': 'Y (Soft)'
            },
            'M1': {
                'factor': 1.4,
                'iso_r': 90,
                'gamma': 0.8,
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.0,
                'description': 'M1 (Normal-hard)'
            },
            '2xM1': {
                'factor': 2.1,
                'iso_r': 80,
                'gamma': 0.9,
                'contrast_index': 1.3,
                'dmin_effect': 0.09,
                'dmax_effect': 2.03,
                'description': '2×M1 (Hard)'
            },
            'M2': {
                'factor': 2.6,
                'iso_r': 65,
                'gamma': 1.0,
                'contrast_index': 1.4,
                'dmin_effect': 0.10,
                'dmax_effect': 2.05,
                'description': 'M2 (Very hard)'
            },
            '2xM2': {
                'factor': 4.6,
                'iso_r': 55,
                'gamma': 1.1,
                'contrast_index': 1.5,
                'dmin_effect': 0.11,
                'dmax_effect': 2.05,
                'description': '2×M2 (Extreme)'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.25,
            'straight_slope': 0.65,
            'shoulder_slope': 0.15,
            'logE_range': 1.7,
            'speed_point': 0.6
        }
    },
    
    # FOMA FOMATONE MG - Based on current implementation
    'foma_fomatone': {
        'manufacturer': 'FOMA',
        'paper_type': 'FOMATONE MG',
        'base_iso_p': 70,
        'dmin': 0.07,
        'dmax': 2.0,
        'exposure_latitude': 1.6,
        'filters': {
            '2xY': {
                'factor': 2.0,
                'iso_r': 120,
                'gamma': 0.4,
                'contrast_index': 0.8,
                'dmin_effect': 0.07,
                'dmax_effect': 1.7,
                'description': '2×Y (Very soft)'
            },
            'Y': {
                'factor': 1.5,
                'iso_r': 105,
                'gamma': 0.5,
                'contrast_index': 0.9,
                'dmin_effect': 0.07,
                'dmax_effect': 1.8,
                'description': 'Y (Soft)'
            },
            'M1': {
                'factor': 1.5,
                'iso_r': 80,
                'gamma': 0.8,
                'contrast_index': 1.2,
                'dmin_effect': 0.09,
                'dmax_effect': 1.9,
                'description': 'M1 (Normal-hard)'
            },
            '2xM1': {
                'factor': 1.8,
                'iso_r': 75,
                'gamma': 0.9,
                'contrast_index': 1.3,
                'dmin_effect': 0.10,
                'dmax_effect': 1.95,
                'description': '2×M1 (Hard)'
            },
            'M2': {
                'factor': 2.0,
                'iso_r': 65,
                'gamma': 1.0,
                'contrast_index': 1.4,
                'dmin_effect': 0.11,
                'dmax_effect': 2.0,
                'description': 'M2 (Very hard)'
            },
            '2xM2': {
                'factor': 3.0,
                'iso_r': 55,
                'gamma': 1.1,
                'contrast_index': 1.5,
                'dmin_effect': 0.12,
                'dmax_effect': 2.0,
                'description': '2×M2 (Extreme)'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.3,
            'straight_slope': 0.6,
            'shoulder_slope': 0.2,
            'logE_range': 1.6,
            'speed_point': 0.6
        }
    }
}

# Filter selection rules based on contrast (ΔEV) measurements
# Based on Heiland methodology research
FILTER_SELECTION_RULES = {
    'ilford': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    'foma_fomaspeed': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': 'Y', 'hard': 'M1', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '2xY', 'hard': 'M1', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '2xY', 'hard': '2xM1', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '2xY', 'hard': '2xM1', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '2xY', 'hard': 'M2', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '2xY', 'hard': '2xM2', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Extreme contrast'}
    },
    'foma_fomatone': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': 'Y', 'hard': 'M1', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '2xY', 'hard': 'M1', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '2xY', 'hard': '2xM1', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '2xY', 'hard': '2xM1', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '2xY', 'hard': 'M2', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '2xY', 'hard': '2xM2', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Extreme contrast'}
    }
}

# Optimization parameters for Heiland-like algorithm
OPTIMIZATION_PARAMS = {
    'target_highlight_density': 0.04,  # Dmin + 0.04 for highlights
    'target_shadow_density': 0.10,     # Dmax - 0.10 for shadows
    'density_tolerance': 0.02,         # Acceptable density error
    'min_exposure_time': 2.0,          # Minimum exposure in seconds
    'max_exposure_time': 120.0,        # Maximum exposure in seconds
    'max_exposure_ratio': 10.0,        # Max ratio between soft/hard exposures
    'prefer_balanced_exposures': True  # Prefer similar exposure times
}

def get_paper_data(paper_id):
    """
    Retrieve paper data from database.
    
    Args:
        paper_id: Paper identifier (e.g., 'ilford_mg_iv', 'foma_fomaspeed')
    
    Returns:
        dict: Paper data or None if not found
    """
    return PAPER_DATABASE.get(paper_id)

def get_filter_selection(delta_ev, system='ilford'):
    """
    Select optimal filter pair based on measured contrast (ΔEV).
    
    Args:
        delta_ev: Measured contrast in stops (0-10 typical)
        system: Filter system ('ilford', 'foma_fomaspeed', 'foma_fomatone')
    
    Returns:
        dict: {
            'soft_filter': str,
            'hard_filter': str,
            'contrast_level': str,
            'description': str,
            'delta_ev': float
        }
    """
    if system not in FILTER_SELECTION_RULES:
        system = 'ilford'  # Default to Ilford
    
    rules = FILTER_SELECTION_RULES[system]
    
    # Find the appropriate rule for the given ΔEV
    for level, rule in rules.items():
        if rule['min'] <= delta_ev < rule['max']:
            return {
                'soft_filter': rule['soft'],
                'hard_filter': rule['hard'],
                'contrast_level': level,
                'description': rule['description'],
                'delta_ev': delta_ev,
                'system': system
            }
    
    # Fallback for extreme values
    return {
        'soft_filter': rules['extreme']['soft'],
        'hard_filter': rules['extreme']['hard'],
        'contrast_level': 'extreme',
        'description': rules['extreme']['description'],
        'delta_ev': delta_ev,
        'system': system
    }

def get_filter_data(paper_id, filter_grade):
    """
    Get detailed filter data for a specific paper and filter grade.
    
    Args:
        paper_id: Paper identifier
        filter_grade: Filter grade (e.g., '00', '5', '2xY', '2xM2')
    
    Returns:
        dict: Filter data or None if not found
    """
    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return None
    
    return paper_data['filters'].get(filter_grade)

def validate_exposure_times(soft_time, hard_time, paper_id=None):
    """
    Validate and optimize exposure times based on Heiland principles.
    
    Args:
        soft_time: Calculated soft exposure time
        hard_time: Calculated hard exposure time
        paper_id: Optional paper identifier for paper-specific limits
    
    Returns:
        tuple: (optimized_soft_time, optimized_hard_time, adjustments_applied)
    """
    params = OPTIMIZATION_PARAMS
    
    # Apply minimum exposure time
    soft_time = max(soft_time, params['min_exposure_time'])
    hard_time = max(hard_time, params['min_exposure_time'])
    
    # Apply maximum exposure time
    soft_time = min(soft_time, params['max_exposure_time'])
    hard_time = min(hard_time, params['max_exposure_time'])
    
    # Check exposure ratio
    if soft_time > 0 and hard_time > 0:
        ratio = max(soft_time, hard_time) / min(soft_time, hard_time)
        if ratio > params['max_exposure_ratio']:
            # Balance exposures by adjusting the longer one
            if soft_time > hard_time:
                soft_time = hard_time * params['max_exposure_ratio']
            else:
                hard_time = soft_time * params['max_exposure_ratio']
    
    # If prefer_balanced_exposures is True, try to balance them more
    if params['prefer_balanced_exposures']:
        avg_time = (soft_time + hard_time) / 2
        if max(soft_time, hard_time) / min(soft_time, hard_time) > 3:
            # Bring them closer together (weighted average)
            soft_time = (soft_time * 0.7) + (avg_time * 0.3)
            hard_time = (hard_time * 0.7) + (avg_time * 0.3)
    
    return soft_time, hard_time, True

def get_paper_list():
    """
    Get list of available papers.
    
    Returns:
        list: List of paper identifiers
    """
    return list(PAPER_DATABASE.keys())

def get_paper_display_name(paper_id):
    """
    Get display name for paper.
    
    Args:
        paper_id: Paper identifier
    
    Returns:
        str: Display name or paper_id if not found
    """
    paper_data = get_paper_data(paper_id)
    if paper_data:
        return f"{paper_data['manufacturer']} {paper_data['paper_type']}"
    return paper_id

def get_available_filters(paper_id):
    """
    Get list of available filters for a paper.
    
    Args:
        paper_id: Paper identifier
    
    Returns:
        list: List of filter grades
    """
    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return []
    
    return list(paper_data['filters'].keys())

def calculate_paper_contrast_range(paper_id):
    """
    Calculate printable contrast range for a paper.
    
    Args:
        paper_id: Paper identifier
    
    Returns:
        float: Printable contrast range in stops
    """
    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return 0.0
    
    # Estimate based on logE range and gamma values
    logE_range = paper_data['characteristic_curve']['logE_range']
    avg_gamma = 0.7  # Average gamma
    
    # Convert logE range to EV stops
    # log10(E) range to EV: EV = log10(E) * 3.32 (approx)
    ev_range = logE_range * 3.32
    
    return ev_range

# Test the module
if __name__ == "__main__":
    print("Paper Database Test")
    print("=" * 50)
    
    # Test get_paper_data
    paper = get_paper_data('ilford_mg_iv')
    print(f"Ilford MG IV: {paper['manufacturer']} {paper['paper_type']}")
    
    # Test filter selection
    for delta_ev in [0.5, 1.2, 2.0, 3.0, 4.5]:
        selection = get_filter_selection(delta_ev, 'ilford')
        print(f"ΔEV {delta_ev:.1f}: {selection['soft_filter']} + {selection['hard_filter']} ({selection['description']})")
    
    # Test exposure validation
    soft, hard, adjusted = validate_exposure_times(1.0, 50.0)
    print(f"\nExposure validation: {soft:.1f}s + {hard:.1f}s (adjusted: {adjusted})")
    
    print("\nPaper Database loaded successfully!")
