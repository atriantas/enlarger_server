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
# Ilford MULTIGRADE RC DELUXE (NEW) - Based on Ilford documentation
    'ilford_multigrade_rc_deluxe_new': {
    'manufacturer': 'Ilford',
    'paper_type': 'MULTIGRADE RC DELUXE (NEW)',
    'dmin': 0.05,       # Estimated; base described as "Neutral" in datasheet
    'dmax': 2.15,       # Published value (vs. 2.05 for MGIVRC) — comparison sheet
    'filters': {
        '00': {
            'factor': 2.08,      # Speed ratio 500/240 (None vs. filter 00)
            'iso_r': 160,        # From ISO Range (R) table
            'gamma': 0.48,       # Derived from visual slope of NEW curve
            'dmin_effect': 0.05,
            'dmax_effect': 2.00,
            'description': 'Very soft - neutral highlights'
        },
        '0': {
            'factor': 2.08,      # Speed is 240 for grades 00-3
            'iso_r': 130,
            'gamma': 0.58,       # Slightly harder midtones than MGIVRC
            'dmin_effect': 0.05,
            'dmax_effect': 2.05,
            'description': 'Soft'
        },
        '1': {
            'factor': 2.08,
            'iso_r': 110,
            'gamma': 0.68,
            'dmin_effect': 0.06,
            'dmax_effect': 2.10,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.08,      # Reference speed 240 for filters 00-3
            'iso_r': 90,
            'gamma': 0.85,       # Harder mid-grade contrast slope
            'dmin_effect': 0.07,
            'dmax_effect': 2.15,
            'description': 'Normal'
        },
        '3': {
            'factor': 2.08,
            'iso_r': 70,
            'gamma': 1.05,
            'dmin_effect': 0.08,
            'dmax_effect': 2.15,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 2.27,      # Speed drops from 500 to 220
            'iso_r': 60,
            'gamma': 1.35,
            'dmin_effect': 0.09,
            'dmax_effect': 2.15,
            'description': 'Hard'
        },
        '5': {
            'factor': 2.27,      # Speed is 220 for grades 4-5
            'iso_r': 50,
            'gamma': 1.65,       # Most uniform response in high grades
            'dmin_effect': 0.10,
            'dmax_effect': 2.15,
            'description': 'Very hard - neutral shadows'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.32,       # Defined transition on NEW curves
        'straight_slope': 0.85,  # Straighter midtone slope vs. MGIVRC
        'shoulder_slope': 0.15,  # Slightly faster compression near Dmax
        'logE_range': 1.6,       # Max range for Grade 00 (ISO R 160 / 100)
    }
    },

# Ilford MULTIGRADE RC PORTFOLIO (NEW) - Based on Ilford documentation
    'ilford_multigrade_rc_portfolio_new': {
    'manufacturer': 'Ilford',
    'paper_type': 'MULTIGRADE RC PORTFOLIO (NEW)',
    'dmin': 0.05,       # Estimated; base described as "Neutral" in datasheet
    'dmax': 2.15,       # Same emulsion as Deluxe NEW (datasheet groups them)
    'filters': {
        '00': {
            'factor': 2.08,      # Speed ratio 500/240 (None vs. filter 00)
            'iso_r': 160,        # From ISO Range (R) table
            'gamma': 0.48,       # Derived from visual slope of NEW curve 00
            'dmin_effect': 0.05,
            'dmax_effect': 2.05, # Higher Dmax allows deeper blacks even on soft grades
            'description': 'Very soft - neutral highlights'
        },
        '0': {
            'factor': 2.08,      # Speed is 240 for grades 00-3
            'iso_r': 130,
            'gamma': 0.58,
            'dmin_effect': 0.05,
            'dmax_effect': 2.10,
            'description': 'Soft'
        },
        '1': {
            'factor': 2.08,
            'iso_r': 110,
            'gamma': 0.68,
            'dmin_effect': 0.06,
            'dmax_effect': 2.15,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.08,      # Reference speed 240 for filters 00-3
            'iso_r': 90,
            'gamma': 0.85,       # "Straighter" curve slope for mid-grades
            'dmin_effect': 0.07,
            'dmax_effect': 2.15,
            'description': 'Normal'
        },
        '3': {
            'factor': 2.08,
            'iso_r': 70,
            'gamma': 1.05,
            'dmin_effect': 0.08,
            'dmax_effect': 2.15,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 2.27,      # Speed drops from 500 to 220 for filters 4-5
            'iso_r': 60,
            'gamma': 1.35,
            'dmin_effect': 0.09,
            'dmax_effect': 2.15,
            'description': 'Hard'
        },
        '5': {
            'factor': 2.27,      # Speed is 220 for grades 4-5
            'iso_r': 50,
            'gamma': 1.65,       # Steepest slope on NEW curves
            'dmin_effect': 0.10,
            'dmax_effect': 2.15,
            'description': 'Very hard - neutral shadows'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.32,       # More defined transition on NEW emulsion
        'straight_slope': 0.85,  # Grade 2 midtone slope
        'shoulder_slope': 0.15,  # Faster compression near higher Dmax
        'logE_range': 1.6,       # Max range for Grade 00 (160/100)
    }
},

# Ilford Multigrade Cooltone - Based on Ilford documentation
'ilford_cooltone': {
    'manufacturer': 'Ilford',
    'paper_type': 'Multigrade RC Cooltone',
    'dmin': 0.05,       # Estimated; base described as "Cool" in datasheet
    'dmax': 2.10,       # Estimated from plateau on characteristic curves
    'filters': {
        '00': {
            'factor': 2.5,       # Speed ratio 500/200 (None vs. filter 00)
            'iso_r': 180,        # From ISO Range (R) table
            'gamma': 0.45,       # Derived from curve slope
            'dmin_effect': 0.05,
            'dmax_effect': 1.95, # Softer shoulder on low grades
            'description': 'Very soft - cool highlights'
        },
        '0': {
            'factor': 2.5,       # Speed is 200 for grades 00-3
            'iso_r': 160,
            'gamma': 0.55,
            'dmin_effect': 0.05,
            'dmax_effect': 2.00,
            'description': 'Soft'
        },
        '1': {
            'factor': 2.5,
            'iso_r': 120,
            'gamma': 0.65,
            'dmin_effect': 0.06,
            'dmax_effect': 2.05,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.5,       # Reference speed 200 for filters 00-3
            'iso_r': 100,
            'gamma': 0.80,
            'dmin_effect': 0.07,
            'dmax_effect': 2.10,
            'description': 'Normal'
        },
        '3': {
            'factor': 2.5,
            'iso_r': 80,
            'gamma': 1.00,
            'dmin_effect': 0.08,
            'dmax_effect': 2.10,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 5.0,       # Speed drops from 500 to 100 for filters 4-5
            'iso_r': 60,
            'gamma': 1.30,
            'dmin_effect': 0.09,
            'dmax_effect': 2.10,
            'description': 'Hard'
        },
        '5': {
            'factor': 5.0,       # Speed is 100 for grades 4-5
            'iso_r': 50,
            'gamma': 1.60,       # Steepest curve slope
            'dmin_effect': 0.10,
            'dmax_effect': 2.10,
            'description': 'Very hard - cool shadows'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.30,       # Transition region
        'straight_slope': 0.80,  # Grade 2 midtone slope
        'shoulder_slope': 0.18,  # Compression near Dmax
        'logE_range': 1.8,       # Max range for Grade 00 (180/100)
    }
},

'ilford_warmtone': {
    'manufacturer': 'Ilford',
    'paper_type': 'Multigrade RC Warmtone',
    'dmin': 0.05,       # Estimated; base described as "Warm" in datasheet
    'dmax': 2.10,       # Estimated from plateau on characteristic curves
    'filters': {
        '00': {
            'factor': 2.0,       # Speed ratio 200/100 (None vs. filter 00)
            'iso_r': 190,        # From ISO Range (R) table — widest range in MG lineup
            'gamma': 0.42,       # Derived from curve slope — soft toe
            'dmin_effect': 0.05,
            'dmax_effect': 1.95, # Softer shoulder on low grades
            'description': 'Very soft - warm highlights'
        },
        '0': {
            'factor': 2.0,       # Speed is 100 for grades 00-3
            'iso_r': 160,
            'gamma': 0.52,
            'dmin_effect': 0.05,
            'dmax_effect': 2.00,
            'description': 'Soft - warm tones'
        },
        '1': {
            'factor': 2.0,
            'iso_r': 130,
            'gamma': 0.62,
            'dmin_effect': 0.06,
            'dmax_effect': 2.05,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.0,       # Reference speed 100 for filters 00-3
            'iso_r': 110,
            'gamma': 0.78,       # Grade 2 midtone slope
            'dmin_effect': 0.07,
            'dmax_effect': 2.10,
            'description': 'Normal - warm tones'
        },
        '3': {
            'factor': 2.0,
            'iso_r': 90,
            'gamma': 0.98,
            'dmin_effect': 0.08,
            'dmax_effect': 2.10,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 4.0,       # Speed drops from 200 to 50 for filters 4-5
            'iso_r': 70,
            'gamma': 1.28,
            'dmin_effect': 0.09,
            'dmax_effect': 2.10,
            'description': 'Hard'
        },
        '5': {
            'factor': 4.0,       # Speed is 50 for grades 4-5
            'iso_r': 50,
            'gamma': 1.58,       # Steepest curve slope
            'dmin_effect': 0.10,
            'dmax_effect': 2.10,
            'description': 'Very hard - warm shadows'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.28,       # Gradual toe characteristic of warmtone emulsions
        'straight_slope': 0.78,  # Grade 2 midtone slope
        'shoulder_slope': 0.18,  # Compression near Dmax
        'logE_range': 1.9,       # Max range for Grade 00 (190/100) — widest in MG lineup
    }
},

# Ilford Multigrade FB Classic - Based on Ilford documentation
'ilford_fb_classic': {
    'manufacturer': 'Ilford',
    'paper_type': 'Multigrade FB Classic',
    'dmin': 0.05,       # Estimated; described as "white base tint" with "deep blacks"
    'dmax': 2.20,       # Estimated from curve plateau — fibre base reaches higher Dmax than RC
    'filters': {
        '00': {
            'factor': 2.17,      # Speed ratio 500/230 (None vs. filter 00)
            'iso_r': 170,        # From ISO Range (R) table
            'gamma': 0.45,       # Calculated slope for Grade 00
            'dmin_effect': 0.05,
            'dmax_effect': 2.00, # Slight compression in lower grades
            'description': 'Very soft'
        },
        '0': {
            'factor': 2.17,      # Speed is 230 for grades 00-3
            'iso_r': 140,
            'gamma': 0.55,
            'dmin_effect': 0.05,
            'dmax_effect': 2.05,
            'description': 'Soft'
        },
        '1': {
            'factor': 2.17,
            'iso_r': 110,
            'gamma': 0.65,
            'dmin_effect': 0.06,
            'dmax_effect': 2.10,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.17,      # Reference speed 230 for filters 00-3
            'iso_r': 95,
            'gamma': 0.80,       # Standard contrast slope
            'dmin_effect': 0.07,
            'dmax_effect': 2.20,
            'description': 'Normal'
        },
        '3': {
            'factor': 2.17,
            'iso_r': 80,
            'gamma': 1.05,
            'dmin_effect': 0.08,
            'dmax_effect': 2.20,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 2.38,      # Speed drops from 500 to 210 for filters 4-5
            'iso_r': 60,
            'gamma': 1.35,
            'dmin_effect': 0.09,
            'dmax_effect': 2.20,
            'description': 'Hard'
        },
        '5': {
            'factor': 2.38,      # Speed is 210 for grades 4-5
            'iso_r': 50,
            'gamma': 1.65,       # Steepest curve slope
            'dmin_effect': 0.10,
            'dmax_effect': 2.20,
            'description': 'Very hard'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.32,       # Observed transition on curves
        'straight_slope': 0.80,  # Grade 2 midtone slope
        'shoulder_slope': 0.15,  # Compression near Dmax
        'logE_range': 1.7,       # Max range for Grade 00 (170/100)
    }
},

# Ilford Multigrade FB Cooltone - Based on Ilford documentation
'ilford_fb_cooltone': {
    'manufacturer': 'Ilford',
    'paper_type': 'Multigrade FB Cooltone',
    'dmin': 0.05,       # Estimated; described as "cool white base tint"
    'dmax': 2.15,       # Estimated from curve plateau — fibre base, "good blacks"
    'filters': {
        '00': {
            'factor': 2.36,      # Speed ratio 590/250 (None vs. filter 00)
            'iso_r': 130,        # From ISO Range (R) table
            'gamma': 0.45,       # Calculated slope for Grade 00
            'dmin_effect': 0.05,
            'dmax_effect': 1.95, # Slight compression in lower grades
            'description': 'Very soft - cool highlights'
        },
        '0': {
            'factor': 2.36,      # Speed is 250 for grades 00-3
            'iso_r': 115,
            'gamma': 0.55,
            'dmin_effect': 0.05,
            'dmax_effect': 2.00,
            'description': 'Soft'
        },
        '1': {
            'factor': 2.36,
            'iso_r': 100,
            'gamma': 0.65,
            'dmin_effect': 0.06,
            'dmax_effect': 2.05,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.36,      # Reference speed 250 for filters 00-3
            'iso_r': 85,
            'gamma': 0.85,       # Standard cool contrast slope
            'dmin_effect': 0.07,
            'dmax_effect': 2.15,
            'description': 'Normal'
        },
        '3': {
            'factor': 2.36,
            'iso_r': 70,
            'gamma': 1.10,
            'dmin_effect': 0.08,
            'dmax_effect': 2.15,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 2.62,      # Speed drops from 590 to 225 for filters 4-5
            'iso_r': 55,
            'gamma': 1.40,
            'dmin_effect': 0.09,
            'dmax_effect': 2.15,
            'description': 'Hard'
        },
        '5': {
            'factor': 2.62,      # Speed is 225 for grades 4-5
            'iso_r': 50,
            'gamma': 1.70,       # Steepest curve slope
            'dmin_effect': 0.10,
            'dmax_effect': 2.15,
            'description': 'Very hard - cool shadows'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.35,       # Observed transition on curves
        'straight_slope': 0.85,  # Grade 2 midtone slope
        'shoulder_slope': 0.12,  # Compression near Dmax
        'logE_range': 1.3,       # Max range for Grade 00 (130/100)
    }
},

# Ilford Multigrade FB Warmtone - Based on Ilford documentation
'ilford_fb_warmtone': {
    'manufacturer': 'Ilford',
    'paper_type': 'Multigrade FB Warmtone',
    'dmin': 0.06,       # Estimated; described as "warm white base"
    'dmax': 2.20,       # Estimated from curve plateau — fibre base, deep warm blacks
    'filters': {
        '00': {
            'factor': 2.0,       # Speed ratio 200/100 (None vs. filter 00)
            'iso_r': 170,        # From ISO Range (R) table
            'gamma': 0.42,       # Calculated slope for Grade 00
            'dmin_effect': 0.06,
            'dmax_effect': 2.05, # Softer shoulder on lower grades
            'description': 'Very soft - warm highlights'
        },
        '0': {
            'factor': 2.0,       # Speed is 100 for grades 00-3
            'iso_r': 160,
            'gamma': 0.52,
            'dmin_effect': 0.06,
            'dmax_effect': 2.10,
            'description': 'Soft'
        },
        '1': {
            'factor': 2.0,
            'iso_r': 130,
            'gamma': 0.65,
            'dmin_effect': 0.07,
            'dmax_effect': 2.15,
            'description': 'Normal-soft'
        },
        '2': {
            'factor': 2.0,       # Reference speed 100 for filters 00-3
            'iso_r': 110,
            'gamma': 0.82,       # Standard warm contrast slope
            'dmin_effect': 0.08,
            'dmax_effect': 2.20,
            'description': 'Normal'
        },
        '3': {
            'factor': 2.0,
            'iso_r': 90,
            'gamma': 1.05,
            'dmin_effect': 0.09,
            'dmax_effect': 2.20,
            'description': 'Normal-hard'
        },
        '4': {
            'factor': 4.0,       # Speed drops from 200 to 50 for filters 4-5
            'iso_r': 70,
            'gamma': 1.30,
            'dmin_effect': 0.10,
            'dmax_effect': 2.20,
            'description': 'Hard'
        },
        '5': {
            'factor': 4.0,       # Speed is 50 for grades 4-5
            'iso_r': 50,
            'gamma': 1.60,       # Steepest slope
            'dmin_effect': 0.11,
            'dmax_effect': 2.20,
            'description': 'Very hard - warm shadows'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.30,       # Initial transition region
        'straight_slope': 0.82,  # Grade 2 midtone slope
        'shoulder_slope': 0.18,  # Compression near Dmax
        'logE_range': 1.8,       # Max range for Grade 00 (170/100)
    }
},

# Ilford Multigrade IV RC Portfolio - Based on Ilford documentation
    'ilford_iv_rc_portfolio': {
        'manufacturer': 'Ilford',
        'paper_type': 'Multigrade IV RC Portfolio (Discontinued)',
        'base_iso_p': 500,  # Speed without filter 
        'dmin': 0.05,       # Cool/Neutral base tone 
        'dmax': 2.05,       # Plateau observed at approx 2.0 on curves [cite: 54]
        'exposure_latitude': 1.5, # Standard industry estimate for RC papers
        'filters': {
            '00': {
                'factor': 2.5,  # Speed 200 vs Base 500 [cite: 43, 136]
                'iso_r': 180,   # From ISO Range table 
                'gamma': 0.45,  # Derived from low-contrast curve slope
                'contrast_index': 0.8,
                'dmin_effect': 0.05,
                'dmax_effect': 1.95, # Visible compression on lower grades
                'description': 'Extra Soft'
            },
            '0': {
                'factor': 2.5,  # [cite: 43, 136]
                'iso_r': 160,   # 
                'gamma': 0.55,
                'contrast_index': 0.9,
                'dmin_effect': 0.05,
                'dmax_effect': 1.98,
                'description': 'Soft'
            },
            '1': {
                'factor': 2.5,  # [cite: 43, 136]
                'iso_r': 130,   # 
                'gamma': 0.65,
                'contrast_index': 1.0,
                'dmin_effect': 0.06,
                'dmax_effect': 2.00,
                'description': 'Normal-soft'
            },
            '2': {
                'factor': 2.5,  # Reference speed for filters 0-3 [cite: 43, 136]
                'iso_r': 110,   # 
                'gamma': 0.80,  # Standard contrast slope for mid-grades
                'contrast_index': 1.1,
                'dmin_effect': 0.07,
                'dmax_effect': 2.05,
                'description': 'Normal'
            },
            '3': {
                'factor': 2.5,  # [cite: 43, 136]
                'iso_r': 90,    # 
                'gamma': 1.00,
                'contrast_index': 1.2,
                'dmin_effect': 0.08,
                'dmax_effect': 2.05,
                'description': 'Normal-hard'
            },
            '4': {
                'factor': 5.0,  # Speed drops to 100 [cite: 43, 136]
                'iso_r': 60,    # 
                'gamma': 1.30,
                'contrast_index': 1.4,
                'dmin_effect': 0.09,
                'dmax_effect': 2.05,
                'description': 'Hard'
            },
            '5': {
                'factor': 5.0,  # Speed drops to 100 [cite: 43, 136]
                'iso_r': 40,    # 
                'gamma': 1.60,  # Steepest curve slope observed
                'contrast_index': 1.5,
                'dmin_effect': 0.10,
                'dmax_effect': 2.05,
                'description': 'Very Hard'
            }
        },
        'characteristic_curve': {
            'toe_slope': 0.30,       # Initial transition region
            'straight_slope': 0.80,  # Grade 2 midtone slope
            'shoulder_slope': 0.18,  # Compression near Dmax plateau
            'logE_range': 1.8,       # Max range for Grade 00 (180/100) 
        }
    },
    
# FOMA FOMASPEED Variant - Updated from Technical Datasheet
'foma_fomaspeed': {
    'manufacturer': 'FOMA',
    'paper_type': 'FOMASPEED VARIANT',
    'dmin': 0.06,       # Estimated; described as "shining white paper base"
    'dmax': 2.10,       # PUBLISHED on sensitometric curves (Dmax = 2.1)
    'filters': {
        '2xY': {
            'factor': 1.6,       # Lengthening factor from Foma filter table (500/310)
            'iso_r': 135,        # From ISO Range table — Extra soft
            'gamma': 0.45,       # Very gentle slope for extra soft
            'dmin_effect': 0.06,
            'dmax_effect': 1.85, # Visible shoulder compression on 2xY curve
            'description': '2xY (Extra soft)'
        },
        'Y': {
            'factor': 1.4,       # 500/360
            'iso_r': 120,        # Soft
            'gamma': 0.55,
            'dmin_effect': 0.06,
            'dmax_effect': 1.95,
            'description': 'Y (Soft)'
        },
        'None': {
            'factor': 1.0,       # Baseline (no filter) — ISO P 500
            'iso_r': 100,        # Special (unfiltered)
            'gamma': 0.75,
            'dmin_effect': 0.07,
            'dmax_effect': 2.00,
            'description': 'Special - No filtration'
        },
        'M1': {
            'factor': 1.4,       # 500/360 — same factor as Y but tighter range
            'iso_r': 90,         # Special
            'gamma': 0.85,
            'dmin_effect': 0.07,
            'dmax_effect': 2.05,
            'description': 'M1 (Special)'
        },
        '2xM1': {
            'factor': 2.1,       # 500/240
            'iso_r': 80,         # Normal
            'gamma': 0.95,       # Standard Normal slope
            'dmin_effect': 0.08,
            'dmax_effect': 2.10,
            'description': '2xM1 (Normal)'
        },
        'M2': {
            'factor': 2.6,       # 500/190
            'iso_r': 65,         # Hard
            'gamma': 1.15,
            'dmin_effect': 0.09,
            'dmax_effect': 2.10,
            'description': 'M2 (Hard)'
        },
        '2xM2': {
            'factor': 4.6,       # 500/110 — significant exposure jump for ultra hard
            'iso_r': 55,         # Ultra hard
            'gamma': 1.45,       # Very steep slope
            'dmin_effect': 0.10,
            'dmax_effect': 2.10,
            'description': '2xM2 (Ultra hard)'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.28,       # Slightly more pronounced toe than Ilford
        'straight_slope': 0.90,  # Grade 2/Normal midtone slope
        'shoulder_slope': 0.18,  # Typical RC shoulder compression
        'logE_range': 1.7,       # Full curve span for softest grade (incl. toe/shoulder)
    }
},
    
# FOMA FOMABROM Variant - Based on Technical Datasheet for Baryta (FB) Paper
'foma_fomabrom': {
    'manufacturer': 'FOMA',
    'paper_type': 'FOMABROM VARIANT (Fiber Base)',
    'dmin': 0.05,       # Estimated; described as "shining white paper base"
    'dmax': 2.00,       # PUBLISHED on sensitometric curves (Dmax = 2.0, glossy surface)
    'filters': {
        '2xY': {
            'factor': 1.6,       # Lengthening factor from Foma table (500/310)
            'iso_r': 135,        # Extra soft
            'gamma': 0.42,
            'dmin_effect': 0.05,
            'dmax_effect': 1.75,
            'description': '2xY (Extra soft)'
        },
        'Y': {
            'factor': 1.4,       # 500/360
            'iso_r': 120,        # Soft
            'gamma': 0.52,
            'dmin_effect': 0.05,
            'dmax_effect': 1.85,
            'description': 'Y (Soft)'
        },
        'None': {
            'factor': 1.0,       # Baseline (no filter) — ISO P 500
            'iso_r': 100,        # Special (unfiltered)
            'gamma': 0.75,
            'dmin_effect': 0.07,
            'dmax_effect': 2.00,
            'description': 'Special - No filtration'
        },
        'M1': {
            'factor': 1.4,       # 500/360
            'iso_r': 90,         # Special
            'gamma': 0.82,
            'dmin_effect': 0.06,
            'dmax_effect': 1.95,
            'description': 'M1 (Special)'
        },
        '2xM1': {
            'factor': 2.1,       # 500/240
            'iso_r': 80,         # Normal
            'gamma': 0.92,
            'dmin_effect': 0.07,
            'dmax_effect': 2.00,
            'description': '2xM1 (Normal)'
        },
        'M2': {
            'factor': 2.6,       # 500/190
            'iso_r': 65,         # Hard
            'gamma': 1.10,
            'dmin_effect': 0.08,
            'dmax_effect': 2.00,
            'description': 'M2 (Hard)'
        },
        '2xM2': {
            'factor': 4.6,       # 500/110 — significant exposure jump for ultra hard
            'iso_r': 55,         # Ultra hard
            'gamma': 1.40,
            'dmin_effect': 0.09,
            'dmax_effect': 2.00,
            'description': '2xM2 (Ultra hard)'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.22,       # Long, gradual toe transition typical of FB
        'straight_slope': 0.85,  # Grade 2-3 midtone average
        'shoulder_slope': 0.20,  # Gentle transition to Dmax 2.0
        'logE_range': 1.6,       # Horizontal range of the curves
    }
},
    
# FOMAPASTEL MG - Verified Technical Data Script
# Based on Foma Technical Information 04/25
'foma_fomapastel_mg': {
    'manufacturer': 'FOMA',
    'paper_type': 'FOMAPASTEL MG (Special FB Colored Base)',
    'dmin': 0.20,       # High due to colored base (varies by CMY/RGB choice)
    'dmax': 1.70,       # Estimated from curve plateau — significantly lower than standard papers
    'filters': {
        '2xY': {
            'factor': 1.5,       # 200/130
            'iso_r': 135,        # Extra soft
            'gamma': 0.50,       # Gentle slope, but crosses other grades in toe
            'dmin_effect': 0.20,
            'dmax_effect': 1.65, # Plateaus below max
            'description': '2xY (Extra soft)'
        },
        'Y': {
            'factor': 1.4,       # 200/140
            'iso_r': 120,        # Soft
            'gamma': 0.60,
            'dmin_effect': 0.20,
            'dmax_effect': 1.68,
            'description': 'Y (Soft)'
        },
        'None': {
            'factor': 1.0,       # Baseline (no filter) — ISO P 200
            'iso_r': 100,        # Special (unfiltered)
            'gamma': 0.85,
            'dmin_effect': 0.20,
            'dmax_effect': 1.70,
            'description': 'Special - No filtration'
        },
        'M1': {
            'factor': 1.4,       # 200/140
            'iso_r': 90,         # Special
            'gamma': 0.95,
            'dmin_effect': 0.21,
            'dmax_effect': 1.70,
            'description': 'M1 (Special)'
        },
        '2xM1': {
            'factor': 2.0,       # 200/100
            'iso_r': 80,         # Normal
            'gamma': 1.10,       # Manufacturer recommends higher contrast grades
            'dmin_effect': 0.22,
            'dmax_effect': 1.55, # Hard grades plateau lower on this paper
            'description': '2xM1 (Normal)'
        },
        'M2': {
            'factor': 2.5,       # 200/80
            'iso_r': 65,         # Hard
            'gamma': 1.30,
            'dmin_effect': 0.23,
            'dmax_effect': 1.45,
            'description': 'M2 (Hard)'
        },
        '2xM2': {
            'factor': 4.5,       # 200/45 — large exposure jump for ultra hard
            'iso_r': 55,         # Ultra hard
            'gamma': 1.55,       # Steep slope but limited Dmax
            'dmin_effect': 0.25,
            'dmax_effect': 1.30, # Significantly compressed Dmax on hardest grade
            'description': '2xM2 (Ultra hard)'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.25,       # Unusual crossing behavior in toe region
        'straight_slope': 1.10,  # Higher contrast recommended by manufacturer
        'shoulder_slope': 0.10,  # Compressed, especially on hard grades
        'logE_range': 1.35,      # Max range for 2xY (135/100)
    }
},

# FOMATONE MG Classic - Updated with Foma Variant Filter Data
'fomatone_mg_classic_variant': {
    'manufacturer': 'FOMA',
    'paper_type': 'FOMATONE MG Classic (Warm Tone)',
    'dmin': 0.10,       # Estimated; cream-colored base tone
    'dmax': 2.00,       # PUBLISHED in table for all grades (glossy); 1.6 for matt
    'filters': {
        '2xY': {
            'factor': 2.0,       # Lengthening factor from Foma table (t_rel)
            'iso_r': 120,        # Extra soft
            'gamma': 0.65,
            'dmin_effect': 0.10,
            'dmax_effect': 1.70, # Curves plateau below table value
            'description': '2xY (Extra soft)'
        },
        'Y': {
            'factor': 1.5,
            'iso_r': 105,        # Soft
            'gamma': 0.75,
            'dmin_effect': 0.10,
            'dmax_effect': 1.85, # Reaches gridline
            'description': 'Y (Soft)'
        },
        'None': {
            'factor': 1.0,       # Baseline (no filter) — Grade 2 (Special)
            'iso_r': 90,         # Special (unfiltered) - default contrast = grade 2
            'gamma': 0.95,
            'dmin_effect': 0.10,
            'dmax_effect': 1.85,
            'description': 'Special - No filtration (Grade 2)'
        },
        'M1': {
            'factor': 1.5,
            'iso_r': 80,         # Special (harder)
            'gamma': 1.10,
            'dmin_effect': 0.11,
            'dmax_effect': 1.85,
            'description': 'M1 (Special)'
        },
        '2xM1': {
            'factor': 1.8,
            'iso_r': 75,         # Normal
            'gamma': 1.20,
            'dmin_effect': 0.11,
            'dmax_effect': 1.75, # Grade 3 plateau slightly lower on curves
            'description': '2xM1 (Normal)'
        },
        'M2': {
            'factor': 2.0,
            'iso_r': 65,         # Hard
            'gamma': 1.45,
            'dmin_effect': 0.12,
            'dmax_effect': 1.85, # Grade 4 reaches gridline
            'description': 'M2 (Hard)'
        },
        '2xM2': {
            'factor': 3.0,
            'iso_r': 55,         # Ultra hard
            'gamma': 1.75,
            'dmin_effect': 0.12,
            'dmax_effect': 1.80, # Grade 5 not plotted; estimated
            'description': '2xM2 (Ultra hard)'
        }
    },
    'characteristic_curve': {
        'toe_slope': 0.15,       # Characteristic long warm toe
        'straight_slope': 0.95,  # For Grade 2 (Special, unfiltered)
        'shoulder_slope': 0.10,
        'logE_range': 1.2,       # Max range for 2xY (120/100); curves span ~2.5 log E total
    }
},
    

}

# Explicit paper order for UI lists
PAPER_ORDER = [
    'ilford_multigrade_rc_deluxe_new',
    'ilford_multigrade_rc_portfolio_new',
    'ilford_cooltone',
    'ilford_warmtone',
    'ilford_fb_classic',
    'ilford_fb_cooltone',
    'ilford_fb_warmtone',
    'ilford_iv_rc_portfolio',
    'foma_fomaspeed',
    'foma_fomabrom',
    'foma_fomapastel_mg',
    'fomatone_mg_classic_variant'
]

# Filter selection rules based on contrast (ΔEV) measurements
# Based on Heiland methodology research
# ── Filter selection rule templates (shared by all papers in the same system) ──
_ILFORD_RULES = {
    'very_low':    {'min': 0.0, 'max': 1.0, 'soft': '1',  'hard': '2', 'description': 'Very low contrast - use close filters'},
    'low':         {'min': 1.0, 'max': 1.5, 'soft': '00', 'hard': '2', 'description': 'Low contrast'},
    'medium_low':  {'min': 1.5, 'max': 2.0, 'soft': '00', 'hard': '3', 'description': 'Medium-low contrast'},
    'normal':      {'min': 2.0, 'max': 2.5, 'soft': '00', 'hard': '3', 'description': 'Normal contrast'},
    'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '00', 'hard': '4', 'description': 'Medium-high contrast'},
    'high':        {'min': 3.0, 'max': 3.5, 'soft': '00', 'hard': '4', 'description': 'High contrast'},
    'very_high':   {'min': 3.5, 'max': 4.0, 'soft': '00', 'hard': '5', 'description': 'Very high contrast'},
    'extreme':     {'min': 4.0, 'max': 10.0,'soft': '00', 'hard': '5', 'description': 'Extreme contrast'},
}

_FOMA_RULES = {
    'very_low':    {'min': 0.0, 'max': 1.0, 'soft': 'Y',   'hard': 'M1',   'description': 'Very low contrast - use close filters'},
    'low':         {'min': 1.0, 'max': 1.5, 'soft': '2xY', 'hard': 'M1',   'description': 'Low contrast'},
    'medium_low':  {'min': 1.5, 'max': 2.0, 'soft': '2xY', 'hard': '2xM1', 'description': 'Medium-low contrast'},
    'normal':      {'min': 2.0, 'max': 2.5, 'soft': '2xY', 'hard': '2xM1', 'description': 'Normal contrast'},
    'medium_high': {'min': 2.5, 'max': 3.0, 'soft': '2xY', 'hard': 'M2',   'description': 'Medium-high contrast'},
    'high':        {'min': 3.0, 'max': 3.5, 'soft': '2xY', 'hard': '2xM2', 'description': 'High contrast'},
    'very_high':   {'min': 3.5, 'max': 4.0, 'soft': '2xY', 'hard': '2xM2', 'description': 'Very high contrast'},
    'extreme':     {'min': 4.0, 'max': 10.0,'soft': '2xY', 'hard': '2xM2', 'description': 'Extreme contrast'},
}

FILTER_SELECTION_RULES = {
    # Ilford papers – all share the same Ilford multigrade filter rules
    'ilford':                           _ILFORD_RULES,
    'ilford_multigrade_rc_deluxe_new':  _ILFORD_RULES,
    'ilford_multigrade_rc_portfolio_new': _ILFORD_RULES,
    'ilford_cooltone':                  _ILFORD_RULES,
    'ilford_warmtone':                  _ILFORD_RULES,
    'ilford_fb_classic':                _ILFORD_RULES,
    'ilford_fb_warmtone':               _ILFORD_RULES,
    'ilford_fb_cooltone':               _ILFORD_RULES,
    'ilford_iv_rc_portfolio':           _ILFORD_RULES,
    # FOMA papers – all share the same FOMA colour-filter rules
    'foma_fomaspeed':                   _FOMA_RULES,
    'foma_fomabrom':                    _FOMA_RULES,
    'foma_fomapastel_mg':               _FOMA_RULES,
    'fomatone_mg_classic_variant':      _FOMA_RULES,
}

# Optimization parameters for Heiland-like algorithm
OPTIMIZATION_PARAMS = {
    'target_highlight_density': 0.04,  # Dmin + 0.04 for highlights
    'target_shadow_density': 0.10,     # Dmax - 0.10 for shadows
    'density_tolerance': 0.02,         # Acceptable density error
    'min_exposure_time': 2.0,          # Minimum exposure in seconds
    'max_exposure_time': 120.0,        # Maximum exposure in seconds
    'max_exposure_ratio': 10.0,        # Max ratio between soft/hard exposures
    'prefer_balanced_exposures': False  # Raw ratios match Heiland behavior
}

def get_paper_data(paper_id):
    """
    Retrieve paper data from database.
    
    Args:
        paper_id: Paper identifier (e.g., 'ilford_multigrade_rc_deluxe_new', 'foma_fomaspeed')
    
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
                'system': system,
                'bin_min': rule['min'],
                'bin_max': rule['max'],
            }
    
    # Fallback for extreme values
    return {
        'soft_filter': rules['extreme']['soft'],
        'hard_filter': rules['extreme']['hard'],
        'contrast_level': 'extreme',
        'description': rules['extreme']['description'],
        'delta_ev': delta_ev,
        'system': system,
        'bin_min': rules['extreme']['min'],
        'bin_max': rules['extreme']['max'],
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
    orig_soft = soft_time
    orig_hard = hard_time
    
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
        if min(soft_time, hard_time) > 0 and max(soft_time, hard_time) / min(soft_time, hard_time) > 3:
            avg_time = (soft_time + hard_time) / 2
            # Bring them closer together (weighted average)
            soft_time = (soft_time * 0.7) + (avg_time * 0.3)
            hard_time = (hard_time * 0.7) + (avg_time * 0.3)
    
    adjusted = abs(soft_time - orig_soft) > 0.01 or abs(hard_time - orig_hard) > 0.01
    return soft_time, hard_time, adjusted

def get_paper_list():
    """
    Get list of available papers.
    
    Returns:
        list: List of paper identifiers
    """
    ordered = [paper_id for paper_id in PAPER_ORDER if paper_id in PAPER_DATABASE]
    for paper_id in PAPER_DATABASE.keys():
        if paper_id not in ordered:
            ordered.append(paper_id)
    return ordered

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

def get_splitgrade_config(paper_id):
    """
    Return RH-Designs-style split-grade configuration for a paper.

    Provides the soft/hard filter pair (always the extremes for the paper's
    filter system) and reciprocity coefficients used by
    splitgrade_enhanced.calculate_split_grade_heiland.

    Args:
        paper_id: Paper identifier

    Returns:
        dict or None: {
            'soft_filter': str,         # '00' for Ilford, '2xY' for FOMA
            'hard_filter': str,         # '5' for Ilford, '2xM2' for FOMA
            'reciprocity_p': float,     # Schwarzschild exponent (RC ~0.07, FB ~0.10)
            'reciprocity_t_ref': float, # Reference time in seconds (10.0)
        }
    """
    paper_data = get_paper_data(paper_id)
    if not paper_data:
        return None

    manufacturer = paper_data.get('manufacturer', '').lower()
    paper_type = paper_data.get('paper_type', '').upper()
    filters = paper_data.get('filters', {})

    if 'foma' in manufacturer:
        soft_filter, hard_filter = '2xY', '2xM2'
    else:
        soft_filter, hard_filter = '00', '5'

    if soft_filter not in filters or hard_filter not in filters:
        return None

    is_fb = (
        'FB' in paper_type
        or 'FIBER' in paper_type
        or 'FOMABROM' in paper_type
        or 'FOMAPASTEL' in paper_type
        or 'FOMATONE' in paper_type
    )
    reciprocity_p = 0.10 if is_fb else 0.07

    return {
        'soft_filter': soft_filter,
        'hard_filter': hard_filter,
        'reciprocity_p': reciprocity_p,
        'reciprocity_t_ref': 10.0,
    }


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
    paper = get_paper_data('ilford_multigrade_rc_deluxe_new')
    print(f"Ilford MG RC Deluxe: {paper['manufacturer']} {paper['paper_type']}")
    
    # Test filter selection
    for delta_ev in [0.5, 1.2, 2.0, 3.0, 4.5]:
        selection = get_filter_selection(delta_ev, 'ilford')
        print(f"ΔEV {delta_ev:.1f}: {selection['soft_filter']} + {selection['hard_filter']} ({selection['description']})")
    
    # Test exposure validation
    soft, hard, adjusted = validate_exposure_times(1.0, 50.0)
    print(f"\nExposure validation: {soft:.1f}s + {hard:.1f}s (adjusted: {adjusted})")
    
    print("\nPaper Database loaded successfully!")
