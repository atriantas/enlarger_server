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
# Ilford Multigrade Cooltone - Based on Ilford documentation
    'ilford_cooltone': {
        'manufacturer': 'Ilford',
        'paper_type': 'Multigrade RC Cooltone',
        'base_iso_p': 500,  # Speed without filter 
        'dmin': 0.05,       # Cool base tone 
        'dmax': 2.10,       # Plateau observed on characteristic curves 
        'exposure_latitude': 1.5,
        'filters': {
            '00': {
                'factor': 2.5,  # Speed is 200 for filters 00-3 [cite: 265, 358]
                'iso_r': 180,   # From ISO Range table [cite: 258]
                'gamma': 0.45,  # Derived from curve slope 
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.95, # Softer shoulder on low grades 
                'description': 'Very soft - cool highlights'
            },
            '0': {
                'factor': 2.5,
                'iso_r': 160,   # [cite: 258]
                'gamma': 0.55,
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 2.00,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.5,
                'iso_r': 120,   # [cite: 258]
                'gamma': 0.65,
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.5,  # Reference speed for filters 00-3 
                'iso_r': 100,   # [cite: 258]
                'gamma': 0.80,
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.10,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.5,
                'iso_r': 80,    # [cite: 258]
                'gamma': 1.00,
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.10,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 5.0,  # Speed drops from 200 to 100 [cite: 265, 358]
                'iso_r': 60,    # [cite: 258]
                'gamma': 1.30,
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.10,
                'description': 'Hard'
            },
            '5': {
                'factor': 5.0,  # Speed drops from 200 to 100 [cite: 265, 358]
                'iso_r': 50,    # [cite: 258]
                'gamma': 1.60,  # Steepest curve slope 
                'contrast_index': 1.5,
                'dmin_effect': 0.10,
                'dmax_effect': 2.10,
                'description': 'Very hard - cool shadows'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.30,       # Transition region 
            'straight_slope': 0.80,  # Grade 2 midtone slope 
            'shoulder_slope': 0.18,  # Compression near Dmax 
            'logE_range': 1.8,       # Maximum range for Grade 00 [cite: 258]
            'speed_point': 0.6       # Standard speed measurement point [cite: 262]
        }
    },

    # Ilford Multigrade IV RC Portfolio - Based on Ilford documentation
    'ilford_iv_rc_portfolio': {
        'manufacturer': 'Ilford',
        'paper_type': 'Multigrade IV RC Portfolio (Discontinued)',
        'base_iso_p': 500,  # Speed without filter 
        'dmin': 0.05,       # Cool/Neutral base tone 
        'dmax': 2.10,       # Plateau observed on shared curves with Deluxe 
        'exposure_latitude': 1.5, # Calculated from Grade 2 linear region 
        'filters': {
            '00': {
                'factor': 2.5,  # Speed 200 for filters 00-3.5 [cite: 43, 136]
                'iso_r': 180,   # From ISO Range table [cite: 36]
                'gamma': 0.45,  # Derived from curve slope 
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.95,
                'description': 'Extra Soft'
            },
            '0': {
                'factor': 2.5,  # [cite: 43, 136]
                'iso_r': 160,   # [cite: 36]
                'gamma': 0.55,  # 
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 2.00,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.5,  # [cite: 43, 136]
                'iso_r': 130,   # [cite: 36]
                'gamma': 0.65,  # 
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.5,  # Reference speed [cite: 43, 136]
                'iso_r': 110,   # [cite: 36]
                'gamma': 0.80,  # Standard contrast slope 
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.10,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.5,  # [cite: 43, 136]
                'iso_r': 90,    # [cite: 36]
                'gamma': 1.00,  # 
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.10,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 5.0,  # Speed drops from 200 to 100 [cite: 43, 136]
                'iso_r': 60,    # [cite: 36]
                'gamma': 1.30,  # 
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.10,
                'description': 'Hard'
            },
            '5': {
                'factor': 5.0,  # Speed drops from 200 to 100 [cite: 43, 136]
                'iso_r': 40,    # [cite: 36]
                'gamma': 1.60,  # Steepest curve slope 
                'contrast_index': 1.5,
                'dmin_effect': 0.10,
                'dmax_effect': 2.10,
                'description': 'Very Hard'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.30,       # Initial transition region 
            'straight_slope': 0.80,  # Grade 2 midtone slope 
            'shoulder_slope': 0.18,  # Compression near Dmax 
            'logE_range': 1.8,       # Max range for Grade 00 based on ISO R [cite: 36]
            'speed_point': 0.6       # Standard industry speed point
        }
    },

    # Ilford MULTIGRADE RC DELUXE (NEW) - Based on Ilford documentation
    'ilford_multigrade_rc_deluxe_new': {
        'manufacturer': 'Ilford',
        'paper_type': 'MULTIGRADE RC DELUXE (NEW)', # [cite: 10]
        'base_iso_p': 500,  # Speed without filter 
        'dmin': 0.05,       # Neutral base tone 
        'dmax': 2.10,       # Observed plateau on NEW characteristic curves 
        'exposure_latitude': 1.6, # Calculated from Grade 2 linear region 
        'filters': {
            '00': {
                'factor': 2.08,  # Speed remains 240 for grades 00-3 
                'iso_r': 160,   # From ISO Range table [cite: 36]
                'gamma': 0.48,  # Derived from visual slope of 'NEW' curve 00 [cite: 98]
                'contrast_index': 0.8, # [cite: 36, 98]
                'dmin_effect': 0.05,
                'dmax_effect': 1.95,
                'description': 'Very soft - neutral highlights'
            },
            '0': {
                'factor': 2.08,  # 
                'iso_r': 130,   # [cite: 36]
                'gamma': 0.58,  # [cite: 98]
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 2.00,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.08,  # 
                'iso_r': 110,   # [cite: 36]
                'gamma': 0.68,  # [cite: 98]
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.08,  # Reference speed for filters 00-3 
                'iso_r': 90,    # [cite: 36]
                'gamma': 0.85,  # Standard neutral contrast slope [cite: 98]
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.10,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.08,  # 
                'iso_r': 70,    # [cite: 36]
                'gamma': 1.05,  # [cite: 98]
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.10,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 2.27,  # Minor speed adjustment (ISO 240 to 220) 
                'iso_r': 60,    # [cite: 36]
                'gamma': 1.35,  # [cite: 98]
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.10,
                'description': 'Hard'
            },
            '5': {
                'factor': 2.27,  # 
                'iso_r': 50,    # [cite: 36]
                'gamma': 1.65,  # Steepest slope on NEW curves [cite: 98]
                'contrast_index': 1.5,
                'dmin_effect': 0.10,
                'dmax_effect': 2.10,
                'description': 'Very hard - neutral shadows'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.32,       # Observed transition on NEW curves [cite: 98]
            'straight_slope': 0.85,  # Grade 2 midtone slope [cite: 98]
            'shoulder_slope': 0.15,  # Highlight compression near Dmax [cite: 98]
            'logE_range': 1.6,       # Max range for Grade 00 [cite: 36]
            'speed_point': 0.6       # Standard speed measurement point [cite: 40, 53]
        }
    },

    # Ilford MULTIGRADE RC PORTFOLIO (NEW) - Based on Ilford documentation
    'ilford_multigrade_rc_portfolio_new': {
        'manufacturer': 'Ilford',
        'paper_type': 'MULTIGRADE RC PORTFOLIO (NEW)',
        'base_iso_p': 500,  # Speed without filter 
        'dmin': 0.05,       # Neutral base tone 
        'dmax': 2.10,       # Observed plateau on NEW characteristic curves 
        'exposure_latitude': 1.6, # Calculated from Grade 2 linear region [cite: 116, 122]
        'filters': {
            '00': {
                'factor': 2.08,  # Speed remains 240 for grades 00-3 
                'iso_r': 160,   # From ISO Range table [cite: 36]
                'gamma': 0.48,  # Derived from visual slope of 'NEW' curve 00 [cite: 98, 101]
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.95, # Lower grades show slightly softer shoulder approaching Dmax
                'description': 'Very soft - neutral highlights'
            },
            '0': {
                'factor': 2.08,  # 
                'iso_r': 130,   # [cite: 36]
                'gamma': 0.58,  # [cite: 98, 107]
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 2.00,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.08,  # 
                'iso_r': 110,   # [cite: 36]
                'gamma': 0.68,  # [cite: 98, 108]
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.08,  # Reference speed for filters 00-3 
                'iso_r': 90,    # [cite: 36]
                'gamma': 0.85,  # Standard neutral contrast slope [cite: 98, 109]
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.10,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.08,  # 
                'iso_r': 70,    # [cite: 36]
                'gamma': 1.05,  # [cite: 98, 110]
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.10,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 2.27,  # Minor adjustment (ISO 240 to 220) 
                'iso_r': 60,    # [cite: 36]
                'gamma': 1.35,  # [cite: 98, 104]
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.10,
                'description': 'Hard'
            },
            '5': {
                'factor': 2.27,  # 
                'iso_r': 50,    # [cite: 36]
                'gamma': 1.65,  # Steepest slope on NEW curves [cite: 98, 105]
                'contrast_index': 1.5,
                'dmin_effect': 0.10,
                'dmax_effect': 2.10,
                'description': 'Very hard - neutral shadows'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.32,       # Observed transition on NEW curves 
            'straight_slope': 0.85,  # Grade 2 midtone slope [cite: 109, 122]
            'shoulder_slope': 0.15,  # Highlight compression near Dmax [cite: 122, 131]
            'logE_range': 1.6,       # Max range for Grade 00 [cite: 36]
            'speed_point': 0.6       # Standard speed measurement point [cite: 40]
        }
    },

    # Ilford Multigrade FB Classic - Based on Ilford documentation
    'ilford_fb_classic': {
        'manufacturer': 'Ilford', #[cite: 616]
        'paper_type': 'Multigrade FB Classic', #[cite: 618, 619]
        'base_iso_p': 500,  # Speed without filter 
        'dmin': 0.05,       # White base tint 
        'dmax': 2.10,       # Plateau observed on characteristic curves 
        'exposure_latitude': 1.5, # Derived from Grade 2 linear region 
        'filters': {
            '00': {
                'factor': 2.17,  # Reference speed 230 for filters 00-3 
                'iso_r': 170,   # From ISO Range table [cite: 659]
                'gamma': 0.45,  # Calculated slope for Grade 00 [cite: 669]
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.95, # Slight compression in lower grades [cite: 669]
                'description': 'Very soft'
            },
            '0': {
                'factor': 2.17,  # 
                'iso_r': 140,   # [cite: 659]
                'gamma': 0.55,  # [cite: 669]
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 2.00,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.17,  # 
                'iso_r': 110,   # [cite: 659]
                'gamma': 0.65,  # [cite: 669]
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.17,  # 
                'iso_r': 95,    # [cite: 659]
                'gamma': 0.80,  # Standard contrast slope [cite: 669]
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.10,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.17,  # 
                'iso_r': 80,    # [cite: 659]
                'gamma': 1.05,  # [cite: 669]
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.10,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 2.38,  # Speed adjustment (ISO 230 to 210) 
                'iso_r': 60,    # [cite: 659]
                'gamma': 1.35,  # [cite: 669]
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.10,
                'description': 'Hard'
            },
            '5': {
                'factor': 2.38,  # 
                'iso_r': 50,    # [cite: 659]
                'gamma': 1.65,  # Steepest curve slope [cite: 669]
                'contrast_index': 1.6,
                'dmin_effect': 0.10,
                'dmax_effect': 2.10,
                'description': 'Very hard'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.32,       # Observed transition on curves [cite: 669]
            'straight_slope': 0.80,  # Grade 2 midtone slope [cite: 669]
            'shoulder_slope': 0.15,  # Compression near Dmax [cite: 669]
            'logE_range': 1.7,       # Max range for Grade 00 based on ISO R [cite: 659]
            'speed_point': 0.6       # Standard industry speed point
        }
    },

    # Ilford Multigrade FB Warmtone - Based on Ilford documentation
    'ilford_fb_warmtone': {
        'manufacturer': 'Ilford',
        'paper_type': 'Multigrade FB Warmtone',
        'base_iso_p': 200,  # Speed without filter 
        'dmin': 0.06,       # Warm white base 
        'dmax': 2.20,       # Plateau observed on characteristic curves [cite: 959]
        'exposure_latitude': 1.7, # Derived from Grade 2 linear region [cite: 971]
        'filters': {
            '00': {
                'factor': 2.0,  # Speed is 100 for filters 00-3 [cite: 944, 958]
                'iso_r': 170,   # From ISO Range table 
                'gamma': 0.42,  # Calculated slope for Grade 00 [cite: 959]
                'contrast_index': 0.8,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05, # Softer shoulder on lower grades [cite: 959]
                'description': 'Very soft - warm highlights'
            },
            '0': {
                'factor': 2.0,
                'iso_r': 160,   # 
                'gamma': 0.52,
                'contrast_index': 0.9,
                'dmin_effect': 0.06,
                'dmax_effect': 2.10,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.0,
                'iso_r': 130,   # 
                'gamma': 0.65,
                'contrast_index': 1.0,
                'dmin_effect': 0.07,
                'dmax_effect': 2.15,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.0,  # Reference speed 100 
                'iso_r': 110,   # [cite: 939, 944]
                'gamma': 0.82,  # Standard warm contrast slope [cite: 959]
                'contrast_index': 1.1,
                'dmin_effect': 0.08,
                'dmax_effect': 2.20,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.0,  # [cite: 944, 958]
                'iso_r': 90,    # 
                'gamma': 1.05,
                'contrast_index': 1.2,
                'dmin_effect': 0.09,
                'dmax_effect': 2.20,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 4.0,  # Speed drops from 100 to 50 [cite: 944, 958]
                'iso_r': 70,    # 
                'gamma': 1.30,
                'contrast_index': 1.4,
                'dmin_effect': 0.10,
                'dmax_effect': 2.20,
                'description': 'Hard'
            },
            '5': {
                'factor': 4.0,  # [cite: 944, 958]
                'iso_r': 50,    # 
                'gamma': 1.60,  # Steepest slope [cite: 959]
                'contrast_index': 1.6,
                'dmin_effect': 0.11,
                'dmax_effect': 2.20,
                'description': 'Very hard - warm shadows'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.30,       # Initial transition region [cite: 959]
            'straight_slope': 0.82,  # Grade 2 midtone slope [cite: 959]
            'shoulder_slope': 0.18,  # Compression near Dmax [cite: 959]
            'logE_range': 1.8,       # Max range for Grade 00 based on ISO R 
            'speed_point': 0.6       # Standard industry speed point
        }
    },

    # Ilford Multigrade FB Cooltone - Based on Ilford documentation
    'ilford_fb_cooltone': {
        'manufacturer': 'Ilford', # [cite: 130]
        'paper_type': 'Multigrade FB Cooltone', # [cite: 133]
        'base_iso_p': 590,  # Speed without filter 
        'dmin': 0.05,       # Cool white base tint 
        'dmax': 2.05,       # Plateau observed on characteristic curves 
        'exposure_latitude': 1.4, # Calculated from Grade 2 linear region 
        'filters': {
            '00': {
                'factor': 2.36,  # Reference speed 250 for filters 00-3 
                'iso_r': 130,   # From ISO Range table [cite: 175]
                'gamma': 0.45,  # Calculated slope for Grade 00 
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.95, # Observed slight compression in lower grades 
                'description': 'Very soft - cool highlights'
            },
            '0': {
                'factor': 2.36,
                'iso_r': 115,   # [cite: 175]
                'gamma': 0.55,
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 2.00,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.36,
                'iso_r': 100,   # [cite: 175]
                'gamma': 0.65,
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.05,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.36,  # Reference speed 250 
                'iso_r': 85,    # [cite: 175]
                'gamma': 0.85,  # Standard cool contrast slope 
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.05,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.36,
                'iso_r': 70,    # [cite: 175]
                'gamma': 1.10,
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.05,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 2.62,  # Speed adjustment (ISO 250 to 225) 
                'iso_r': 55,    # [cite: 175]
                'gamma': 1.40,  # 
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.05,
                'description': 'Hard'
            },
            '5': {
                'factor': 2.62,  # 
                'iso_r': 50,    # [cite: 175]
                'gamma': 1.70,  # Steepest curve slope 
                'contrast_index': 1.6,
                'dmin_effect': 0.10,
                'dmax_effect': 2.05,
                'description': 'Very hard - cool shadows'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.35,       # Observed transition on curves 
            'straight_slope': 0.85,  # Grade 2 midtone slope 
            'shoulder_slope': 0.12,  # Compression near Dmax 
            'logE_range': 1.3,       # Max range for Grade 00 based on ISO R [cite: 175]
            'speed_point': 0.6       # Standard speed measurement point
        }
    },
    
# FOMA FOMASPEED Variant - Updated from Technical Datasheet
    'foma_fomaspeed': {
        'manufacturer': 'FOMA', #[cite: 1]
        'paper_type': 'FOMASPEED VARIANT', #[cite: 3]
        'base_iso_p': 500, #[cite: 63, 65]
        'dmin': 0.06, #[cite: 72, 80]
        'dmax': 2.1, #[cite: 73, 81]
        'exposure_latitude': 1.7, #[cite: 70, 80]
        'filters': {
            '2xY': {
                'factor': 1.6, #[cite: 65]
                'iso_r': 135, #[cite: 65]
                'gamma': 0.45, #[cite: 70, 74]
                'contrast_index': 0.8, #[cite: 63]
                'dmin_effect': 0.06, #[cite: 70]
                'dmax_effect': 1.85, #[cite: 70, 82]
                'description': '2×Y (Extra soft)' #[cite: 65]
            },
            'Y': {
                'factor': 1.4, #[cite: 65]
                'iso_r': 120, #[cite: 65]
                'gamma': 0.55, #[cite: 70, 74]
                'contrast_index': 0.9, #[cite: 63]
                'dmin_effect': 0.06, #[cite: 70]
                'dmax_effect': 1.95, #[cite: 70]
                'description': 'Y (Soft)' #[cite: 65]
            },
            'M1': {
                'factor': 1.4, #[cite: 65]
                'iso_r': 90, #[cite: 65]
                'gamma': 0.85, #[cite: 70, 75]
                'contrast_index': 1.1, #[cite: 63]
                'dmin_effect': 0.07, #[cite: 70]
                'dmax_effect': 2.05, #[cite: 70]
                'description': 'M1 (Special)' #[cite: 65]
            },
            '2xM1': {
                'factor': 2.1, #[cite: 65]
                'iso_r': 80, #[cite: 65]
                'gamma': 0.95, #[cite: 70, 75]
                'contrast_index': 1.2, #[cite: 63]
                'dmin_effect': 0.08, #[cite: 70]
                'dmax_effect': 2.10, #[cite: 70, 73]
                'description': '2×M1 (Normal)' #[cite: 65]
            },
            'M2': {
                'factor': 2.6, #[cite: 65]
                'iso_r': 65, #[cite: 65]
                'gamma': 1.15, #[cite: 70, 76]
                'contrast_index': 1.4, #[cite: 63]
                'dmin_effect': 0.09, #[cite: 70]
                'dmax_effect': 2.10, #[cite: 70, 73]
                'description': 'M2 (Hard)' #[cite: 65]
            },
            '2xM2': {
                'factor': 4.6, #[cite: 65]
                'iso_r': 55, #[cite: 65]
                'gamma': 1.45, #[cite: 70, 77]
                'contrast_index': 1.6, #[cite: 63]
                'dmin_effect': 0.10, #[cite: 70]
                'dmax_effect': 2.10, #[cite: 70, 73]
                'description': '2×M2 (Ultra hard)' #[cite: 65]
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.28, #[cite: 70, 80]
            'straight_slope': 0.90, #[cite: 70, 75]
            'shoulder_slope': 0.18, #[cite: 70, 73]
            'logE_range': 1.7, #[cite: 80]
            'speed_point': 0.6 #[cite: 11, 71]
        }
    },
    
# FOMA FOMABROM Variant - Based on Technical Datasheet for Baryta (FB) Paper
    'foma_fomabrom': {
        'manufacturer': 'FOMA',
        'paper_type': 'FOMABROM VARIANT',
        'base_iso_p': 500,
        'dmin': 0.05, # Baryta base typically yields a slightly cleaner white [cite: 100]
        'dmax': 2.0,  # Explicitly stated for glossy surface 
        'exposure_latitude': 1.6, # Derived from Log rel. exposure curves [cite: 167]
        'filters': {
            '2xY': {
                'factor': 1.6,
                'iso_r': 135,
                'gamma': 0.42,
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.75,
                'description': '2×Y (Extra soft)'
            },
            'Y': {
                'factor': 1.4,
                'iso_r': 120,
                'gamma': 0.52,
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 1.85,
                'description': 'Y (Soft)'
            },
            'M1': {
                'factor': 1.4,
                'iso_r': 90,
                'gamma': 0.82,
                'contrast_index': 1.1,
                'dmin_effect': 0.06,
                'dmax_effect': 1.95,
                'description': 'M1 (Special)'
            },
            '2xM1': {
                'factor': 2.1,
                'iso_r': 80,
                'gamma': 0.92,
                'contrast_index': 1.2,
                'dmin_effect': 0.07,
                'dmax_effect': 2.0,
                'description': '2×M1 (Normal)'
            },
            'M2': {
                'factor': 2.6,
                'iso_r': 65,
                'gamma': 1.10,
                'contrast_index': 1.4,
                'dmin_effect': 0.08,
                'dmax_effect': 2.0,
                'description': 'M2 (Hard)'
            },
            '2xM2': {
                'factor': 4.6,
                'iso_r': 55,
                'gamma': 1.40,
                'contrast_index': 1.6,
                'dmin_effect': 0.09,
                'dmax_effect': 2.0,
                'description': '2×M2 (Ultra hard)'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.22,      # Calculated from visual curves [cite: 154]
            'straight_slope': 0.85, # Average gradient for grade 2-3 [cite: 154]
            'shoulder_slope': 0.20, # Transition to Dmax 2.0 [cite: 154, 158]
            'logE_range': 1.6,      # Horizontal range of the curves [cite: 167]
            'speed_point': 0.6      # Standard density point for speed [cite: 154]
        }
    },
    
# FOMAPASTEL MG - Verified Technical Data Script
# Based on Foma Technical Information 04/25
'foma_fomapastel_mg': {
    'manufacturer': 'Foma',
    'paper_type': 'FOMAPASTEL MG (Special FB Colored Base)',
    'base_iso_p': 200,          # Verified for Special/No Filter grade 
    'dmin': 0.20,               # Variable depending on base color (CMY/RGB) 
    'dmax': 2.00,               # Deep black characteristic 
    'exposure_latitude': 1.4,   # Based on ISO R range 140 to 45 
    'filters': {
        '2xY': {
            'factor': 1.5,      # Lengthening factor (be) 
            'iso_p': 130,       # Speed 
            'iso_r': 135,       # Grade: Extra Soft 
            'description': 'Extra soft - Foma Variant 2xY'
        },
        'Y': {
            'factor': 1.4,
            'iso_p': 120,
            'iso_r': 140,       # Grade: Soft 
            'description': 'Soft - Foma Variant Y'
        },
        'None': {
            'factor': 1.0,      # Baseline 
            'iso_p': 200,
            'iso_r': 100,       # Grade: Special 
            'description': 'Special - No filtration'
        },
        'M1': {
            'factor': 1.4,
            'iso_p': 90,
            'iso_r': 140,       # Grade: Special 
            'description': 'Special - Foma Variant M1'
        },
        '2xM1': {
            'factor': 2.0,
            'iso_p': 100,
            'iso_r': 80,        # Grade: Normal 
            'description': 'Normal - Foma Variant 2xM1'
        },
        'M2': {
            'factor': 2.5,
            'iso_p': 80,
            'iso_r': 65,        # Grade: Hard 
            'description': 'Hard - Foma Variant M2'
        },
        '2xM2': {
            'factor': 4.5,
            'iso_p': 55,
            'iso_r': 45,        # Grade: Ultra Hard 
            'description': 'Ultra hard - Foma Variant 2xM2'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.20,
        'straight_slope': 1.10, # Higher default contrast recommended [cite: 721]
        'shoulder_slope': 0.15,
        'logE_range': 1.0,      # ISO R 100 (Special) 
        'speed_point': 0.6
    }
},

# FOMATONE MG Classic - Updated with Foma Variant Filter Data
'fomatone_mg_classic_variant': {
    'manufacturer': 'Foma',
    'paper_type': 'FOMATONE MG Classic (Warm Tone)',
    'base_iso_p': 20,           # Low speed, primarily for contact/long exposure
    'dmin': 0.10,               # Cream-colored base tone
    'dmax': 2.00,               # For glossy surface (1.6 for matt)
    'exposure_latitude': 1.2,   # Narrower range than standard RC
    'filters': {
        '2xY': {
            'factor': 2.0,      # Lengthening factor (t_rel)
            'iso_r': 120,       # Grade: Extra Soft
            'gamma': 0.65,      # Estimated slope
            'description': 'Extra soft - Foma Variant 2xY'
        },
        'Y': {
            'factor': 1.5,
            'iso_r': 105,       # Grade: Soft
            'gamma': 0.75,
            'description': 'Soft - Foma Variant Y'
        },
        'None': {
            'factor': 1.0,      # Baseline (Special Grade)
            'iso_r': 90,        # Grade: Special
            'gamma': 0.95,
            'description': 'Special - No filtration (Grade 2)'
        },
        'M1': {
            'factor': 1.5,
            'iso_r': 80,        # Grade: Special (Harder)
            'gamma': 1.10,
            'description': 'Special Hard - Foma Variant M1'
        },
        '2xM1': {
            'factor': 1.8,
            'iso_r': 75,        # Grade: Normal
            'gamma': 1.20,
            'description': 'Normal - Foma Variant 2xM1'
        },
        'M2': {
            'factor': 2.0,
            'iso_r': 65,        # Grade: Hard
            'gamma': 1.45,
            'description': 'Hard - Foma Variant M2'
        },
        '2xM2': {
            'factor': 3.0,
            'iso_r': 55,        # Grade: Ultra Hard
            'gamma': 1.75,
            'description': 'Ultra hard - Foma Variant 2xM2'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.15,      # Characteristic long "warm" toe
        'straight_slope': 0.95, # For Grade 2 (Special)
        'shoulder_slope': 0.10,
        'logE_range': 0.9,      # ISO R 90 = 0.9 log units
        'speed_point': 0.6
    }
},
    

}

# Filter selection rules based on contrast (ΔEV) measurements
# Based on Heiland methodology research
FILTER_SELECTION_RULES = {
    # Ilford papers (standard Ilford filter system)
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
    # Ilford Cooltone RC
    'ilford_cooltone': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # Ilford Portfolio (discontinued)
    'ilford_iv_rc_portfolio': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # Ilford Multigrade RC Deluxe (NEW)
    'ilford_multigrade_rc_deluxe_new': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # Ilford Multigrade RC Portfolio (NEW)
    'ilford_multigrade_rc_portfolio_new': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # Ilford FB Classic
    'ilford_fb_classic': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # Ilford FB Warmtone
    'ilford_fb_warmtone': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # Ilford FB Cooltone
    'ilford_fb_cooltone': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': '1', 'hard': '2', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '00', 'hard': '5', 'description': 'Extreme contrast'}
    },
    # FOMA papers
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
    'foma_fomabrom': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': 'Y', 'hard': 'M1', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '2xY', 'hard': 'M1', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '2xY', 'hard': '2xM1', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '2xY', 'hard': '2xM1', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '2xY', 'hard': 'M2', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '2xY', 'hard': '2xM2', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Extreme contrast'}
    },
    # Note: foma_fomapastel_mg uses different filter naming (includes 'None' filter)
    # For backward compatibility, we'll use the same rules as other FOMA papers
    'foma_fomapastel_mg': {
        'very_low': {'min': 0.0, 'max': 1.0, 'soft': 'Y', 'hard': 'M1', 'description': 'Very low contrast - use close filters'},
        'low': {'min': 1.0, 'max': 1.5, 'soft': '2xY', 'hard': 'M1', 'description': 'Low contrast'},
        'medium_low': {'min': 1.5, 'max': 2.0, 'soft': '2xY', 'hard': '2xM1', 'description': 'Medium-low contrast'},
        'normal': {'min': 2.0, 'max': 2.5, 'soft': '2xY', 'hard': '2xM1', 'description': 'Normal contrast'},
        'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '2xY', 'hard': 'M2', 'description': 'Medium-high contrast'},
        'high': {'min': 3.0, 'max': 3.5, 'soft': '2xY', 'hard': '2xM2', 'description': 'High contrast'},
        'very_high': {'min': 3.5, 'max': 4.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Very high contrast'},
        'extreme': {'min': 4.0, 'max': 10.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Extreme contrast'}
    },
    
    'fomatone_mg_classic_variant': {
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
