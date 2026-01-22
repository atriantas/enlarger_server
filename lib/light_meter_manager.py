"""
Light Meter Manager for Darkroom Exposure and Contrast Analysis
Raspberry Pi Pico 2 W - MicroPython

Provides:
- Multi-point averaging for shadow/highlight readings
- NDR (Negative Density Range) calculation
- Contrast grade recommendation with interpolation
- Exposure time calculation using ISO-P paper speed
- Split-grade optimization
- Dual calibration (Absolute ISO / Perfect Print)
- Paper profile management
"""

import json
import math
import time
import os


class LightMeterManager:
    """
    Light Meter Manager for darkroom exposure and contrast analysis.
    
    Features:
    - Multi-point averaging for accurate readings
    - NDR calculation from shadow/highlight measurements
    - Grade recommendation with interpolation between grades
    - Exposure calculation using paper ISO-P speed
    - Split-grade optimization for soft/hard filter times
    - Dual calibration: Absolute (ISO) and Perfect Print (reference)
    - Paper profile storage and management
    """
    
    # Default paper profiles file
    PROFILES_FILE = "paper_profiles.json"
    CALIBRATION_FILE = "meter_calibration.json"
    
    # Grade to NDR mapping (from ISO 6846 and manufacturer data)
    # NDR ranges: [min_ndr, max_ndr] for each grade
    GRADE_NDR_RANGES = {
        "00": (1.60, 1.90),
        "0": (1.40, 1.60),
        "0.5": (1.30, 1.40),
        "1": (1.20, 1.40),
        "1.5": (1.10, 1.20),
        "2": (1.00, 1.20),
        "2.5": (0.90, 1.00),
        "3": (0.80, 1.00),
        "3.5": (0.70, 0.80),
        "4": (0.60, 0.80),
        "4.5": (0.50, 0.60),
        "5": (0.40, 0.60)
    }
    
    # Grade order for interpolation
    GRADE_ORDER = ["00", "0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"]
    
    def __init__(self, light_sensor=None):
        """
        Initialize the Light Meter Manager.
        
        Args:
            light_sensor: LightSensor instance for hardware readings
        """
        self.light_sensor = light_sensor
        
        # Multi-point averaging buffers
        self.shadow_readings = []
        self.highlight_readings = []
        
        # Captured values (finalized from averages)
        self.shadow_lux = None
        self.highlight_lux = None
        self.shadow_ev = None
        self.highlight_ev = None
        
        # Calculated values
        self.ndr = None
        self.recommended_grade = None
        self.calculated_exposure = None
        
        # Settings
        self.flare_compensation = 0.10  # 10% default
        self.enlarger_type = "diffuser"  # "diffuser" or "condenser"
        
        # Calibration data
        self.calibration = {
            "method": "absolute",  # "absolute" or "perfect_print"
            "iso_p": 200,          # Paper speed for absolute
            "reference_lux": None, # Reference lux for perfect print
            "reference_time": None # Reference time for perfect print
        }
        
        # Paper profiles
        self.profiles = []
        self.current_profile = None
        
        # Load saved data
        self._load_profiles()
        self._load_calibration()
    
    def _load_profiles(self):
        """Load paper profiles from JSON file."""
        try:
            with open(self.PROFILES_FILE, 'r') as f:
                data = json.load(f)
                self.profiles = data.get("profiles", [])
                
                # Set default profile if available
                if self.profiles:
                    self.current_profile = self.profiles[0]
                    
                print(f"✅ Light Meter: Loaded {len(self.profiles)} paper profiles")
        except OSError:
            print("📄 Light Meter: No profiles file, using defaults")
            self._create_default_profiles()
        except Exception as e:
            print(f"⚠️ Light Meter: Error loading profiles: {e}")
            self._create_default_profiles()
    
    def _save_profiles(self):
        """Save paper profiles to JSON file."""
        try:
            with open(self.PROFILES_FILE, 'w') as f:
                json.dump({"profiles": self.profiles}, f)
            return True
        except Exception as e:
            print(f"❌ Light Meter: Error saving profiles: {e}")
            return False
    
    def _create_default_profiles(self):
        """Create default paper profiles."""
        self.profiles = [
            {
                "name": "Ilford MGIV RC",
                "brand": "Ilford",
                "iso_p": 200,
                "iso_p_high_grades": 100,
                "speed_matched_to": 3.5,
                "factors": {
                    "00": 1.0, "0": 1.0, "0.5": 1.0, "1": 1.0, "1.5": 1.0,
                    "2": 1.0, "2.5": 1.0, "3": 1.0, "3.5": 1.0,
                    "4": 1.2, "4.5": 1.35, "5": 1.5
                },
                "notes": "Speed-matched Grade 00-3.5, 2x exposure for Grade 4-5"
            },
            {
                "name": "Ilford MGV FB",
                "brand": "Ilford",
                "iso_p": 160,
                "iso_p_high_grades": 80,
                "speed_matched_to": 3.5,
                "factors": {
                    "00": 1.0, "0": 1.0, "0.5": 1.0, "1": 1.0, "1.5": 1.0,
                    "2": 1.0, "2.5": 1.0, "3": 1.0, "3.5": 1.0,
                    "4": 1.2, "4.5": 1.35, "5": 1.5
                },
                "notes": "Fiber base, warm tone, speed-matched to Grade 3.5"
            },
            {
                "name": "Foma Variant III",
                "brand": "FOMA",
                "iso_p": 200,
                "iso_p_high_grades": 100,
                "speed_matched_to": 1,
                "factors": {
                    "00": 1.6, "0": 1.4, "0.5": 1.2, "1": 1.0, "1.5": 1.2,
                    "2": 1.4, "2.5": 1.75, "3": 2.1, "3.5": 2.35,
                    "4": 2.6, "4.5": 3.6, "5": 4.6
                },
                "notes": "Variable contrast, requires filter factor adjustment"
            },
            {
                "name": "Fomatone MG",
                "brand": "FOMA",
                "iso_p": 160,
                "iso_p_high_grades": 80,
                "speed_matched_to": 1,
                "factors": {
                    "00": 2.0, "0": 1.5, "0.5": 1.25, "1": 1.0, "1.5": 1.25,
                    "2": 1.5, "2.5": 1.65, "3": 1.8, "3.5": 1.9,
                    "4": 2.0, "4.5": 2.5, "5": 3.0
                },
                "notes": "Warm tone fiber base"
            },
            {
                "name": "Custom",
                "brand": "Custom",
                "iso_p": 200,
                "iso_p_high_grades": 200,
                "speed_matched_to": 2,
                "factors": {
                    "00": 1.0, "0": 1.0, "0.5": 1.0, "1": 1.0, "1.5": 1.0,
                    "2": 1.0, "2.5": 1.0, "3": 1.0, "3.5": 1.0,
                    "4": 1.0, "4.5": 1.0, "5": 1.0
                },
                "notes": "User-calibrated profile",
                "user_calibrated": True
            }
        ]
        
        if self.profiles:
            self.current_profile = self.profiles[0]
        
        self._save_profiles()
    
    def _load_calibration(self):
        """Load calibration data from file."""
        try:
            with open(self.CALIBRATION_FILE, 'r') as f:
                self.calibration = json.load(f)
                print(f"✅ Light Meter: Calibration loaded ({self.calibration['method']})")
        except OSError:
            print("📄 Light Meter: No calibration file, using defaults")
        except Exception as e:
            print(f"⚠️ Light Meter: Error loading calibration: {e}")
    
    def _save_calibration(self):
        """Save calibration data to file."""
        try:
            with open(self.CALIBRATION_FILE, 'w') as f:
                json.dump(self.calibration, f)
            return True
        except Exception as e:
            print(f"❌ Light Meter: Error saving calibration: {e}")
            return False
    
    # ===== READING METHODS =====
    
    def read_lux(self):
        """
        Take a single lux reading from the sensor.
        
        Returns:
            dict: Reading data or error
        """
        if not self.light_sensor:
            return {"status": "error", "error": "No light sensor configured"}
        
        return self.light_sensor.read_lux_sync()
    
    async def read_lux_async(self):
        """
        Take an async lux reading from the sensor.
        
        Returns:
            dict: Reading data or error
        """
        if not self.light_sensor:
            return {"status": "error", "error": "No light sensor configured"}
        
        return await self.light_sensor.read_lux_async()
    
    # ===== MULTI-POINT AVERAGING =====
    
    def add_reading(self, reading_type):
        """
        Add a reading to the multi-point average buffer.
        
        Args:
            reading_type: "shadow" or "highlight"
            
        Returns:
            dict: Status with current average and count
        """
        reading = self.read_lux()
        
        if reading.get("status") != "success":
            return reading
        
        lux = reading["lux"]
        ev = reading["ev"]
        
        if reading_type == "shadow":
            self.shadow_readings.append({"lux": lux, "ev": ev})
            count = len(self.shadow_readings)
            avg_lux = sum(r["lux"] for r in self.shadow_readings) / count
            avg_ev = sum(r["ev"] for r in self.shadow_readings) / count
            
            return {
                "status": "success",
                "type": "shadow",
                "reading": {"lux": lux, "ev": ev},
                "count": count,
                "average_lux": round(avg_lux, 2),
                "average_ev": round(avg_ev, 2)
            }
        
        elif reading_type == "highlight":
            self.highlight_readings.append({"lux": lux, "ev": ev})
            count = len(self.highlight_readings)
            avg_lux = sum(r["lux"] for r in self.highlight_readings) / count
            avg_ev = sum(r["ev"] for r in self.highlight_readings) / count
            
            return {
                "status": "success",
                "type": "highlight",
                "reading": {"lux": lux, "ev": ev},
                "count": count,
                "average_lux": round(avg_lux, 2),
                "average_ev": round(avg_ev, 2)
            }
        
        return {"status": "error", "error": f"Invalid reading type: {reading_type}"}
    
    def get_average(self, reading_type):
        """
        Get the current average for a reading type.
        
        Args:
            reading_type: "shadow" or "highlight"
            
        Returns:
            dict: Average data
        """
        if reading_type == "shadow":
            readings = self.shadow_readings
        elif reading_type == "highlight":
            readings = self.highlight_readings
        else:
            return {"status": "error", "error": f"Invalid reading type: {reading_type}"}
        
        if not readings:
            return {
                "status": "success",
                "type": reading_type,
                "count": 0,
                "average_lux": None,
                "average_ev": None
            }
        
        count = len(readings)
        avg_lux = sum(r["lux"] for r in readings) / count
        avg_ev = sum(r["ev"] for r in readings) / count
        
        return {
            "status": "success",
            "type": reading_type,
            "count": count,
            "average_lux": round(avg_lux, 2),
            "average_ev": round(avg_ev, 2),
            "readings": readings
        }
    
    def capture(self, reading_type):
        """
        Finalize a capture using the averaged readings.
        
        Args:
            reading_type: "shadow" or "highlight"
            
        Returns:
            dict: Captured value
        """
        avg = self.get_average(reading_type)
        
        if avg.get("count", 0) == 0:
            # No averaged readings, take a single reading
            reading = self.read_lux()
            if reading.get("status") != "success":
                return reading
            
            lux = reading["lux"]
            ev = reading["ev"]
        else:
            lux = avg["average_lux"]
            ev = avg["average_ev"]
        
        if reading_type == "shadow":
            self.shadow_lux = lux
            self.shadow_ev = ev
            self.shadow_readings = []  # Clear buffer after capture
            
            return {
                "status": "success",
                "type": "shadow",
                "lux": lux,
                "ev": ev,
                "samples_used": avg.get("count", 1)
            }
        
        elif reading_type == "highlight":
            self.highlight_lux = lux
            self.highlight_ev = ev
            self.highlight_readings = []  # Clear buffer after capture
            
            return {
                "status": "success",
                "type": "highlight",
                "lux": lux,
                "ev": ev,
                "samples_used": avg.get("count", 1)
            }
        
        return {"status": "error", "error": f"Invalid reading type: {reading_type}"}
    
    def clear_readings(self, reading_type="all"):
        """
        Clear reading buffers and/or captured values.
        
        Args:
            reading_type: "shadow", "highlight", or "all"
        """
        if reading_type in ("shadow", "all"):
            self.shadow_readings = []
            self.shadow_lux = None
            self.shadow_ev = None
        
        if reading_type in ("highlight", "all"):
            self.highlight_readings = []
            self.highlight_lux = None
            self.highlight_ev = None
        
        if reading_type == "all":
            self.ndr = None
            self.recommended_grade = None
            self.calculated_exposure = None
        
        return {"status": "success", "cleared": reading_type}
    
    # ===== NDR AND GRADE CALCULATION =====
    
    def calculate_ndr(self):
        """
        Calculate Negative Density Range from captured shadow/highlight.
        
        NDR = log10(shadow_lux) - log10(highlight_lux)
        
        Returns:
            dict: NDR calculation result
        """
        if self.shadow_lux is None or self.highlight_lux is None:
            return {
                "status": "error",
                "error": "Both shadow and highlight must be captured first"
            }
        
        if self.shadow_lux <= 0 or self.highlight_lux <= 0:
            return {
                "status": "error",
                "error": "Invalid lux values (must be positive)"
            }
        
        # Calculate raw NDR
        # Shadow = thin negative area = bright on easel = high lux
        # Highlight = dense negative area = dark on easel = low lux
        raw_ndr = math.log10(self.shadow_lux) - math.log10(self.highlight_lux)
        
        # Apply flare compensation (reduces effective NDR)
        flare_factor = 1.0 - self.flare_compensation
        compensated_ndr = raw_ndr * flare_factor
        
        # Apply enlarger type adjustment
        # Condenser enlargers increase effective contrast by ~1 grade
        if self.enlarger_type == "condenser":
            # Reduce NDR to account for increased contrast
            compensated_ndr *= 0.85  # Approximately 1 grade harder
        
        self.ndr = compensated_ndr
        
        return {
            "status": "success",
            "ndr_raw": round(raw_ndr, 3),
            "ndr_compensated": round(compensated_ndr, 3),
            "shadow_lux": self.shadow_lux,
            "highlight_lux": self.highlight_lux,
            "flare_compensation": self.flare_compensation,
            "enlarger_type": self.enlarger_type
        }
    
    def recommend_grade(self):
        """
        Recommend contrast grade based on NDR with interpolation.
        
        Returns:
            dict: Grade recommendation with interpolation details
        """
        if self.ndr is None:
            ndr_result = self.calculate_ndr()
            if ndr_result.get("status") != "success":
                return ndr_result
        
        ndr = self.ndr
        
        # Find matching grade range
        lower_grade = None
        upper_grade = None
        exact_match = None
        
        for grade in self.GRADE_ORDER:
            min_ndr, max_ndr = self.GRADE_NDR_RANGES[grade]
            
            if min_ndr <= ndr <= max_ndr:
                exact_match = grade
                break
            
            if ndr > max_ndr:
                lower_grade = grade  # Softer grade (higher NDR)
            elif ndr < min_ndr and upper_grade is None:
                upper_grade = grade  # Harder grade (lower NDR)
        
        # Build recommendation
        if exact_match:
            recommendation = {
                "status": "success",
                "ndr": round(ndr, 3),
                "exact_grade": exact_match,
                "interpolated": False,
                "recommendation": f"Grade {exact_match}",
                "recommendation_text": f"Grade {exact_match} is an exact match for your negative's density range."
            }
        elif lower_grade and upper_grade:
            # Interpolation needed
            lower_min, lower_max = self.GRADE_NDR_RANGES[lower_grade]
            upper_min, upper_max = self.GRADE_NDR_RANGES[upper_grade]
            
            # Calculate position between grades
            range_span = lower_min - upper_max
            position = (lower_min - ndr) / range_span if range_span > 0 else 0.5
            
            # Determine which grade to recommend
            if position < 0.5:
                primary_grade = lower_grade
                secondary_grade = upper_grade
                primary_text = f"Grade {lower_grade} recommended (preserves highlight detail)"
                secondary_text = f"Grade {upper_grade} alternative (deeper blacks, compressed highlights)"
            else:
                primary_grade = upper_grade
                secondary_grade = lower_grade
                primary_text = f"Grade {upper_grade} recommended (deeper blacks)"
                secondary_text = f"Grade {lower_grade} alternative (preserves highlights, lighter shadows)"
            
            recommendation = {
                "status": "success",
                "ndr": round(ndr, 3),
                "interpolated": True,
                "lower_grade": lower_grade,
                "upper_grade": upper_grade,
                "position": round(position, 2),
                "primary_grade": primary_grade,
                "secondary_grade": secondary_grade,
                "recommendation": primary_grade,
                "recommendation_text": primary_text,
                "alternative_text": secondary_text
            }
        elif lower_grade:
            # NDR is very high (very flat negative)
            recommendation = {
                "status": "success",
                "ndr": round(ndr, 3),
                "exact_grade": lower_grade,
                "interpolated": False,
                "recommendation": lower_grade,
                "recommendation_text": f"Grade {lower_grade} (softest available). Negative is very flat.",
                "warning": "Negative density range exceeds paper capability. Consider higher contrast development."
            }
        elif upper_grade:
            # NDR is very low (very contrasty negative)
            recommendation = {
                "status": "success",
                "ndr": round(ndr, 3),
                "exact_grade": upper_grade,
                "interpolated": False,
                "recommendation": upper_grade,
                "recommendation_text": f"Grade {upper_grade} (hardest available). Negative is very contrasty.",
                "warning": "Negative density range is below paper capability. Consider lower contrast development."
            }
        else:
            recommendation = {
                "status": "error",
                "ndr": round(ndr, 3),
                "error": "Could not determine grade recommendation"
            }
        
        self.recommended_grade = recommendation.get("recommendation")
        return recommendation
    
    # ===== EXPOSURE CALCULATION =====
    
    def calculate_exposure(self, target_lux=None, grade=None):
        """
        Calculate exposure time based on paper speed and lux.
        
        Formula: t = 1000 / (ISO_P × lux) × filter_factor
        
        Args:
            target_lux: Lux value to use (default: shadow_lux for shadow detail)
            grade: Grade for filter factor (default: recommended_grade)
            
        Returns:
            dict: Exposure calculation result
        """
        if not self.current_profile:
            return {"status": "error", "error": "No paper profile selected"}
        
        # Use shadow lux by default (ensures shadow detail)
        if target_lux is None:
            if self.shadow_lux is None:
                return {"status": "error", "error": "No shadow reading captured"}
            target_lux = self.shadow_lux
        
        # Use recommended grade if not specified
        if grade is None:
            if self.recommended_grade is None:
                grade_result = self.recommend_grade()
                if grade_result.get("status") != "success":
                    return grade_result
            grade = self.recommended_grade
        
        # Get paper speed
        profile = self.current_profile
        
        # Check if grade requires different ISO-P
        grade_num = float(grade) if grade not in ("00",) else -0.5
        speed_matched_to = profile.get("speed_matched_to", 3.5)
        
        if grade_num > speed_matched_to:
            iso_p = profile.get("iso_p_high_grades", profile["iso_p"])
        else:
            iso_p = profile["iso_p"]
        
        # Get filter factor
        factors = profile.get("factors", {})
        filter_factor = factors.get(str(grade), factors.get(grade, 1.0))
        
        # Calculate base exposure
        if self.calibration["method"] == "perfect_print":
            # Use reference-based calculation
            ref_lux = self.calibration.get("reference_lux")
            ref_time = self.calibration.get("reference_time")
            
            if ref_lux and ref_time:
                # Scale from reference
                base_time = ref_time * (ref_lux / target_lux)
            else:
                # Fall back to ISO calculation
                base_time = 1000.0 / (iso_p * target_lux)
        else:
            # Absolute ISO-P calculation
            base_time = 1000.0 / (iso_p * target_lux)
        
        # Apply filter factor
        final_time = base_time * filter_factor
        
        # Calculate f-stop equivalent from base
        if base_time > 0:
            stops_from_base = math.log2(final_time / base_time)
        else:
            stops_from_base = 0
        
        self.calculated_exposure = final_time
        
        return {
            "status": "success",
            "exposure_time": round(final_time, 2),
            "base_time": round(base_time, 2),
            "filter_factor": filter_factor,
            "stops_adjustment": round(stops_from_base, 2),
            "grade": grade,
            "iso_p": iso_p,
            "target_lux": target_lux,
            "profile": profile["name"],
            "calibration_method": self.calibration["method"]
        }
    
    # ===== SPLIT-GRADE OPTIMIZATION =====
    
    def calculate_split_grade(self):
        """
        Calculate optimal split-grade exposure times.
        
        Uses NDR to determine soft/hard filter balance and calculates
        individual exposure times for each filter.
        
        Returns:
            dict: Split-grade calculation result
        """
        if not self.current_profile:
            return {"status": "error", "error": "No paper profile selected"}
        
        if self.shadow_lux is None or self.highlight_lux is None:
            return {"status": "error", "error": "Both shadow and highlight must be captured"}
        
        # Calculate NDR if not done
        if self.ndr is None:
            ndr_result = self.calculate_ndr()
            if ndr_result.get("status") != "success":
                return ndr_result
        
        # Get grade recommendation
        grade_result = self.recommend_grade()
        if grade_result.get("status") != "success":
            return grade_result
        
        ndr = self.ndr
        profile = self.current_profile
        factors = profile.get("factors", {})
        
        # Determine soft and hard filters based on NDR
        # Higher NDR (flat negative) = more hard filter
        # Lower NDR (contrasty negative) = more soft filter
        
        # Standard split: Grade 00 (soft) and Grade 5 (hard)
        soft_filter = "00"
        hard_filter = "5"
        
        # Calculate burn percentage based on NDR
        # NDR 1.0 (Grade 2) = 50/50 split
        # Higher NDR = more hard filter (increase burn%)
        # Lower NDR = more soft filter (decrease burn%)
        
        # Map NDR to burn percentage
        # NDR 1.4 (Grade 0) → 30% hard
        # NDR 1.0 (Grade 2) → 50% hard
        # NDR 0.6 (Grade 4) → 70% hard
        
        burn_percent = 50 + (1.0 - ndr) * 50
        burn_percent = max(20, min(80, burn_percent))  # Clamp to 20-80%
        
        # Calculate base exposure (neutral time)
        # Use geometric mean of shadow and highlight for neutral
        neutral_lux = math.sqrt(self.shadow_lux * self.highlight_lux)
        
        iso_p = profile["iso_p"]
        
        if self.calibration["method"] == "perfect_print":
            ref_lux = self.calibration.get("reference_lux")
            ref_time = self.calibration.get("reference_time")
            if ref_lux and ref_time:
                neutral_time = ref_time * (ref_lux / neutral_lux)
            else:
                neutral_time = 1000.0 / (iso_p * neutral_lux)
        else:
            neutral_time = 1000.0 / (iso_p * neutral_lux)
        
        # Calculate split times
        highlights_base = neutral_time * (100 - burn_percent) / 100
        shadows_base = neutral_time * burn_percent / 100
        
        # Apply filter factors
        soft_factor = factors.get(soft_filter, 1.0)
        hard_factor = factors.get(hard_filter, 1.0)
        
        soft_time = highlights_base * soft_factor
        hard_time = shadows_base * hard_factor
        total_time = soft_time + hard_time
        
        return {
            "status": "success",
            "neutral_time": round(neutral_time, 2),
            "soft_filter": soft_filter,
            "hard_filter": hard_filter,
            "soft_time": round(soft_time, 2),
            "hard_time": round(hard_time, 2),
            "total_time": round(total_time, 2),
            "burn_percent": round(burn_percent, 1),
            "highlights_base": round(highlights_base, 2),
            "shadows_base": round(shadows_base, 2),
            "soft_factor": soft_factor,
            "hard_factor": hard_factor,
            "ndr": round(ndr, 3),
            "recommended_grade": self.recommended_grade,
            "profile": profile["name"],
            "paper_brand": profile["brand"]
        }
    
    # ===== MAIN CALCULATE METHOD =====
    
    def calculate(self, mode="exposure"):
        """
        Main calculation method supporting all three modes.
        
        Args:
            mode: "exposure", "grade", or "split"
            
        Returns:
            dict: Calculation result based on mode
        """
        if mode == "exposure":
            return self.calculate_exposure()
        elif mode == "grade":
            return self.recommend_grade()
        elif mode == "split":
            return self.calculate_split_grade()
        else:
            return {"status": "error", "error": f"Invalid mode: {mode}"}
    
    # ===== CALIBRATION =====
    
    def calibrate_absolute(self, iso_p):
        """
        Set absolute calibration using ISO-P paper speed.
        
        Args:
            iso_p: Paper speed (typically 100-400)
        """
        self.calibration["method"] = "absolute"
        self.calibration["iso_p"] = iso_p
        self._save_calibration()
        
        return {
            "status": "success",
            "method": "absolute",
            "iso_p": iso_p
        }
    
    def calibrate_perfect_print(self, reference_lux, reference_time):
        """
        Set perfect print calibration using a reference exposure.
        
        Args:
            reference_lux: Lux reading from a perfect print
            reference_time: Exposure time that produced the perfect print
        """
        self.calibration["method"] = "perfect_print"
        self.calibration["reference_lux"] = reference_lux
        self.calibration["reference_time"] = reference_time
        self._save_calibration()
        
        return {
            "status": "success",
            "method": "perfect_print",
            "reference_lux": reference_lux,
            "reference_time": reference_time
        }
    
    def get_calibration(self):
        """Get current calibration settings."""
        return {
            "status": "success",
            "calibration": self.calibration
        }
    
    # ===== SETTINGS =====
    
    def set_settings(self, flare=None, enlarger=None):
        """
        Update meter settings.
        
        Args:
            flare: Flare compensation (0.05 to 0.15)
            enlarger: Enlarger type ("diffuser" or "condenser")
        """
        if flare is not None:
            self.flare_compensation = max(0.05, min(0.15, flare))
        
        if enlarger is not None:
            if enlarger in ("diffuser", "condenser"):
                self.enlarger_type = enlarger
        
        return {
            "status": "success",
            "flare_compensation": self.flare_compensation,
            "enlarger_type": self.enlarger_type
        }
    
    def get_settings(self):
        """Get current meter settings."""
        return {
            "status": "success",
            "flare_compensation": self.flare_compensation,
            "enlarger_type": self.enlarger_type
        }
    
    # ===== PROFILE MANAGEMENT =====
    
    def get_profiles(self):
        """Get list of all paper profiles."""
        return {
            "status": "success",
            "profiles": [{"name": p["name"], "brand": p["brand"]} for p in self.profiles],
            "current": self.current_profile["name"] if self.current_profile else None
        }
    
    def get_profile(self, name):
        """Get a specific paper profile by name."""
        for profile in self.profiles:
            if profile["name"] == name:
                return {"status": "success", "profile": profile}
        
        return {"status": "error", "error": f"Profile not found: {name}"}
    
    def set_current_profile(self, name):
        """Set the current paper profile."""
        for profile in self.profiles:
            if profile["name"] == name:
                self.current_profile = profile
                return {"status": "success", "profile": profile}
        
        return {"status": "error", "error": f"Profile not found: {name}"}
    
    def save_profile(self, profile_data):
        """
        Save or update a paper profile.
        
        Args:
            profile_data: Profile dictionary with name, brand, iso_p, factors, etc.
        """
        name = profile_data.get("name")
        if not name:
            return {"status": "error", "error": "Profile name required"}
        
        # Find existing profile
        for i, profile in enumerate(self.profiles):
            if profile["name"] == name:
                self.profiles[i] = profile_data
                self._save_profiles()
                return {"status": "success", "action": "updated", "profile": profile_data}
        
        # Add new profile
        self.profiles.append(profile_data)
        self._save_profiles()
        return {"status": "success", "action": "created", "profile": profile_data}
    
    def delete_profile(self, name):
        """Delete a paper profile."""
        for i, profile in enumerate(self.profiles):
            if profile["name"] == name:
                if profile.get("user_calibrated") or name == "Custom":
                    del self.profiles[i]
                    self._save_profiles()
                    return {"status": "success", "deleted": name}
                else:
                    return {"status": "error", "error": "Cannot delete built-in profiles"}
        
        return {"status": "error", "error": f"Profile not found: {name}"}
    
    # ===== STATUS =====
    
    def get_status(self):
        """Get complete meter status."""
        sensor_status = self.light_sensor.get_status() if self.light_sensor else {"is_connected": False}
        
        return {
            "status": "success",
            "sensor": sensor_status,
            "shadow": {
                "captured_lux": self.shadow_lux,
                "captured_ev": self.shadow_ev,
                "pending_samples": len(self.shadow_readings)
            },
            "highlight": {
                "captured_lux": self.highlight_lux,
                "captured_ev": self.highlight_ev,
                "pending_samples": len(self.highlight_readings)
            },
            "ndr": self.ndr,
            "recommended_grade": self.recommended_grade,
            "calculated_exposure": self.calculated_exposure,
            "current_profile": self.current_profile["name"] if self.current_profile else None,
            "calibration": self.calibration,
            "settings": {
                "flare_compensation": self.flare_compensation,
                "enlarger_type": self.enlarger_type
            }
        }
