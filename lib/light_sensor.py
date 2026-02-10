"""
TSL2591X Light Sensor Driver for Waveshare TSL2591X
Raspberry Pi Pico 2 W - MicroPython v1.27.0

High-sensitivity digital light sensor for darkroom exposure metering.
Communicates via I²C protocol. Measures illuminance in lux.

Photographic Applications:
- Exposure meter: Measure enlarger light intensity
- Contrast analysis: Compare shadow/highlight luminance
- Split-grade printing: Calculate separate exposures

Technical Specifications (TSL2591):
- Two photodiodes: Visible + IR (channel 0) and IR only (channel 1)
- Dynamic range: 600M:1 (auto-gain)
- Lux range: 188 µlux to 88,000 lux
- Integration times: 100ms to 600ms
"""

import asyncio
import time
import math
from machine import Pin, I2C
from lib.paper_database import get_filter_selection, get_filter_data, validate_exposure_times


class TSL2591:
    """
    Waveshare TSL2591X light sensor interface via I²C.
    
    Attributes:
        i2c: I2C bus instance
        address: I2C device address (default: 0x29)
        gain: Current gain setting (LOW, MED, HIGH, MAX)
        integration: Integration time in ms (100-600)
        last_lux: Last successfully read lux value
        last_error: Last error message (None if OK)
    """
    
    # I²C Address
    ADDR = 0x29
    
    # Command register
    COMMAND_BIT = 0xA0
    
    # Register addresses
    REG_ENABLE = 0x00
    REG_CONTROL = 0x01
    REG_ID = 0x12
    REG_STATUS = 0x13
    REG_C0DATAL = 0x14  # Channel 0 data (visible + IR)
    REG_C0DATAH = 0x15
    REG_C1DATAL = 0x16  # Channel 1 data (IR only)
    REG_C1DATAH = 0x17
    
    # Enable register bits
    ENABLE_PON = 0x01   # Power ON
    ENABLE_AEN = 0x02   # ALS Enable
    ENABLE_AIEN = 0x10  # ALS Interrupt Enable
    ENABLE_NPIEN = 0x80 # No Persist Interrupt Enable
    
    # Gain settings
    GAIN_LOW = 0x00     # 1x gain
    GAIN_MED = 0x10     # 25x gain (medium)
    GAIN_HIGH = 0x20    # 428x gain (high)
    GAIN_MAX = 0x30     # 9876x gain (maximum)
    
    GAIN_FACTORS = {
        GAIN_LOW: 1.0,
        GAIN_MED: 25.0,
        GAIN_HIGH: 428.0,
        GAIN_MAX: 9876.0
    }
    
    # Integration time settings (register values and milliseconds)
    INTEGRATIONTIME_100MS = 0x00
    INTEGRATIONTIME_200MS = 0x01
    INTEGRATIONTIME_300MS = 0x02
    INTEGRATIONTIME_400MS = 0x03
    INTEGRATIONTIME_500MS = 0x04
    INTEGRATIONTIME_600MS = 0x05
    
    INTEGRATION_TIMES_MS = {
        INTEGRATIONTIME_100MS: 100,
        INTEGRATIONTIME_200MS: 200,
        INTEGRATIONTIME_300MS: 300,
        INTEGRATIONTIME_400MS: 400,
        INTEGRATIONTIME_500MS: 500,
        INTEGRATIONTIME_600MS: 600
    }
    
    # LUX calculation coefficients (from datasheet)
    LUX_DF = 408.0  # Device factor
    LUX_COEFF_B = 1.64
    LUX_COEFF_C = 0.59
    LUX_COEFF_D = 0.86
    
    def __init__(self, i2c=None, sda_pin=0, scl_pin=1, address=ADDR):
        """
        Initialize TSL2591 sensor.
        
        Args:
            i2c: Existing I2C bus instance (optional)
            sda_pin: SDA GPIO pin number (default: GP0)
            scl_pin: SCL GPIO pin number (default: GP1)
            address: I2C device address (default: 0x29)
        """
        self.address = address
        self.last_lux = None
        self.last_visible = None
        self.last_ir = None
        self.last_error = None
        self.connected = False
        
        # Default settings
        self._gain = self.GAIN_MED  # Start with medium gain
        self._integration = self.INTEGRATIONTIME_300MS  # 300ms integration
        
        try:
            # Use provided I2C or create new instance
            if i2c:
                self.i2c = i2c
            else:
                self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
            
            # Verify sensor presence
            if self._verify_sensor():
                self._enable()
                self._set_timing(self._gain, self._integration)
                self.connected = True
                print(f"✓ TSL2591 initialized on I2C (SDA=GP{sda_pin}, SCL=GP{scl_pin})")
            else:
                self.last_error = "TSL2591 not found on I2C bus"
                print(f"WARNING: {self.last_error}")
                
        except Exception as e:
            self.last_error = str(e)
            print(f"ERROR: Failed to initialize TSL2591: {e}")
    
    def _write_register(self, reg, value):
        """Write a byte to a register."""
        self.i2c.writeto(self.address, bytes([self.COMMAND_BIT | reg, value]))
    
    def _read_register(self, reg):
        """Read a byte from a register."""
        self.i2c.writeto(self.address, bytes([self.COMMAND_BIT | reg]))
        return self.i2c.readfrom(self.address, 1)[0]
    
    def _read_u16(self, reg):
        """Read a 16-bit value from two consecutive registers (little-endian)."""
        self.i2c.writeto(self.address, bytes([self.COMMAND_BIT | reg]))
        data = self.i2c.readfrom(self.address, 2)
        return data[0] | (data[1] << 8)
    
    def _verify_sensor(self):
        """Verify sensor is present and responding."""
        try:
            # Scan I2C bus
            devices = self.i2c.scan()
            if self.address not in devices:
                print(f"TSL2591 not found at address 0x{self.address:02X}")
                print(f"Found devices: {['0x{:02X}'.format(d) for d in devices]}")
                return False
            
            # Check device ID
            dev_id = self._read_register(self.REG_ID)
            if dev_id != 0x50:
                print(f"Unexpected device ID: 0x{dev_id:02X} (expected 0x50)")
                return False
            
            return True
            
        except Exception as e:
            print(f"Sensor verification failed: {e}")
            return False
    
    def _enable(self):
        """Enable the sensor (power on + ALS enable)."""
        self._write_register(self.REG_ENABLE, self.ENABLE_PON | self.ENABLE_AEN)
    
    def _disable(self):
        """Disable the sensor (power off)."""
        self._write_register(self.REG_ENABLE, 0x00)
    
    def _set_timing(self, gain, integration):
        """Set gain and integration time."""
        self._gain = gain
        self._integration = integration
        self._write_register(self.REG_CONTROL, gain | integration)
    
    def set_gain(self, gain):
        """
        Set sensor gain.
        
        Args:
            gain: One of GAIN_LOW (1x), GAIN_MED (25x), GAIN_HIGH (428x), GAIN_MAX (9876x)
        
        Darkroom Usage:
        - GAIN_LOW: Bright enlarger light (measuring paper white)
        - GAIN_MED: Normal conditions (good starting point)
        - GAIN_HIGH: Dim conditions, deep shadows
        - GAIN_MAX: Very dim, measuring shadow detail
        """
        self._set_timing(gain, self._integration)
    
    def set_integration_time(self, integration):
        """
        Set integration time.
        
        Args:
            integration: One of INTEGRATIONTIME_100MS to INTEGRATIONTIME_600MS
        
        Longer integration = more sensitivity, better low-light readings
        Shorter integration = faster readings, better for bright conditions
        """
        self._set_timing(self._gain, integration)
    
    def get_raw_data(self):
        """
        Read raw channel data from sensor.
        
        Returns:
            tuple: (channel0, channel1) raw ADC values
            channel0 = visible + IR light
            channel1 = IR only
        """
        if not self.connected:
            return None, None
        
        try:
            # Wait for integration to complete
            integration_ms = self.INTEGRATION_TIMES_MS[self._integration]
            time.sleep_ms(integration_ms + 10)  # Add 10ms margin
            
            # Read both channels
            ch0 = self._read_u16(self.REG_C0DATAL)
            ch1 = self._read_u16(self.REG_C1DATAL)
            
            return ch0, ch1
            
        except Exception as e:
            self.last_error = str(e)
            return None, None
    
    async def get_raw_data_async(self):
        """
        Async version of get_raw_data() - non-blocking.
        
        Returns:
            tuple: (channel0, channel1) raw ADC values
        """
        if not self.connected:
            return None, None
        
        try:
            # Wait for integration to complete (non-blocking)
            integration_ms = self.INTEGRATION_TIMES_MS[self._integration]
            await asyncio.sleep_ms(integration_ms + 10)
            
            # Read both channels
            ch0 = self._read_u16(self.REG_C0DATAL)
            ch1 = self._read_u16(self.REG_C1DATAL)
            
            return ch0, ch1
            
        except Exception as e:
            self.last_error = str(e)
            return None, None
    
    def calculate_lux(self, ch0, ch1):
        """
        Calculate lux from raw channel data.
        
        Uses the TSL2591 datasheet formula to convert raw ADC values
        to calibrated lux readings.
        
        Args:
            ch0: Channel 0 raw value (visible + IR)
            ch1: Channel 1 raw value (IR only)
        
        Returns:
            float: Illuminance in lux
        """
        if ch0 is None or ch1 is None:
            return None
        
        # Get current gain factor
        gain_factor = self.GAIN_FACTORS.get(self._gain, 25.0)
        
        # Get integration time in ms
        integration_ms = self.INTEGRATION_TIMES_MS.get(self._integration, 300)
        
        # Check for saturation
        if ch0 >= 65535 or ch1 >= 65535:
            # Sensor saturated - need lower gain or shorter integration
            self.last_error = "Sensor saturated - too bright"
            return None
        
        # Calculate counts per lux
        # CPL = (ATIME * AGAIN) / DF
        cpl = (integration_ms * gain_factor) / self.LUX_DF
        
        if cpl == 0:
            return 0.0
        
        # Calculate lux using two methods and take the max
        # This handles different spectral conditions
        
        # Method 1: Standard formula
        lux1 = (ch0 - (self.LUX_COEFF_B * ch1)) / cpl
        
        # Method 2: Alternative for IR-heavy conditions
        lux2 = ((self.LUX_COEFF_C * ch0) - (self.LUX_COEFF_D * ch1)) / cpl
        
        # Take maximum of both (both should be positive for valid readings)
        lux = max(lux1, lux2, 0.0)
        
        return lux
    
    def read_lux(self):
        """
        Read illuminance in lux (blocking).
        
        Returns:
            float: Illuminance in lux, or None on error
        """
        ch0, ch1 = self.get_raw_data()
        if ch0 is None:
            return None
        
        lux = self.calculate_lux(ch0, ch1)
        
        if lux is not None:
            self.last_lux = lux
            self.last_visible = ch0
            self.last_ir = ch1
            self.last_error = None
        
        return lux
    
    async def read_lux_async(self):
        """
        Read illuminance in lux (non-blocking).
        
        Returns:
            float: Illuminance in lux, or None on error
        """
        ch0, ch1 = await self.get_raw_data_async()
        if ch0 is None:
            return None
        
        lux = self.calculate_lux(ch0, ch1)
        
        if lux is not None:
            self.last_lux = lux
            self.last_visible = ch0
            self.last_ir = ch1
            self.last_error = None
        
        return lux
    
    async def read_averaged_lux_async(self, samples=5, delay_ms=50):
        """
        Read averaged lux value over multiple samples.
        
        For darkroom exposure metering, averaging reduces flicker effects
        from the enlarger lamp and provides more stable readings.
        
        Args:
            samples: Number of samples to average (default: 5)
            delay_ms: Delay between samples in ms (default: 50)
        
        Returns:
            dict: {
                'lux': float,           # Averaged lux value
                'min': float,           # Minimum reading
                'max': float,           # Maximum reading
                'samples': int,         # Number of valid samples
                'variance': float       # Reading variance (stability indicator)
            }
        """
        readings = []
        
        for i in range(samples):
            lux = await self.read_lux_async()
            if lux is not None:
                readings.append(lux)
            
            if i < samples - 1:
                await asyncio.sleep_ms(delay_ms)
        
        if not readings:
            return {
                'lux': None,
                'min': None,
                'max': None,
                'samples': 0,
                'variance': None,
                'error': self.last_error
            }
        
        avg_lux = sum(readings) / len(readings)
        min_lux = min(readings)
        max_lux = max(readings)
        
        # Calculate variance
        if len(readings) > 1:
            variance = sum((x - avg_lux) ** 2 for x in readings) / len(readings)
        else:
            variance = 0.0
        
        # Update cached value
        self.last_lux = avg_lux
        
        return {
            'lux': avg_lux,
            'min': min_lux,
            'max': max_lux,
            'samples': len(readings),
            'variance': variance
        }
    
    def auto_gain(self):
        """
        Automatically adjust gain for optimal sensitivity.
        
        Reads current light level and adjusts gain to maximize
        dynamic range without saturation.
        
        Returns:
            int: New gain setting
        """
        ch0, ch1 = self.get_raw_data()
        
        if ch0 is None:
            return self._gain
        
        # If saturated, decrease gain
        if ch0 >= 60000 or ch1 >= 60000:
            if self._gain == self.GAIN_MAX:
                self.set_gain(self.GAIN_HIGH)
            elif self._gain == self.GAIN_HIGH:
                self.set_gain(self.GAIN_MED)
            elif self._gain == self.GAIN_MED:
                self.set_gain(self.GAIN_LOW)
        
        # If too low, increase gain
        elif ch0 < 1000 and ch1 < 1000:
            if self._gain == self.GAIN_LOW:
                self.set_gain(self.GAIN_MED)
            elif self._gain == self.GAIN_MED:
                self.set_gain(self.GAIN_HIGH)
            elif self._gain == self.GAIN_HIGH:
                self.set_gain(self.GAIN_MAX)
        
        return self._gain
    
    def get_status(self):
        """
        Get sensor status information.
        
        Returns:
            dict: Status information including settings and last readings
        """
        gain_names = {
            self.GAIN_LOW: "LOW (1x)",
            self.GAIN_MED: "MED (25x)",
            self.GAIN_HIGH: "HIGH (428x)",
            self.GAIN_MAX: "MAX (9876x)"
        }
        
        return {
            'connected': self.connected,
            'address': f"0x{self.address:02X}",
            'gain': gain_names.get(self._gain, "Unknown"),
            'gain_value': self._gain,
            'integration_ms': self.INTEGRATION_TIMES_MS.get(self._integration, 0),
            'last_lux': self.last_lux,
            'last_visible': self.last_visible,
            'last_ir': self.last_ir,
            'last_error': self.last_error
        }


class DarkroomLightMeter:
    """
    High-level darkroom light meter using TSL2591 sensor.
    
    Provides photographic-specific functions:
    - Base exposure calculation
    - Contrast measurement (ΔEV)
    - Filter grade recommendation
    - Split-grade exposure calculation
    
    Calibration:
    The light meter needs calibration per paper type. The calibration
    constant (lux-seconds) represents the exposure needed for a proper print.
    
    Calibration Process:
    1. Set up enlarger with a typical negative
    2. Measure lux at baseboard
    3. Make test strip prints
    4. Determine correct exposure time
    5. calibration_constant = measured_lux * correct_time
    """
    
    # ISO R values define paper's exposure latitude (printable ΔEV range)
    # Higher ISO R = longer exposure range = prints more contrast
    # Enhanced with Heiland research data and paper database gamma values
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
        40: 4.0     # Grade 5 - very hard (gamma 1.0)
    }
    
    # Default calibration constant (lux × seconds)
    # This should be calibrated per paper type
    DEFAULT_CALIBRATION = 1000.0
    
    def __init__(self, sensor=None, i2c=None, sda_pin=0, scl_pin=1):
        """
        Initialize darkroom light meter.
        
        Args:
            sensor: Existing TSL2591 instance (optional)
            i2c: Existing I2C bus (optional)
            sda_pin: SDA GPIO pin (default: GP0)
            scl_pin: SCL GPIO pin (default: GP1)
        """
        if sensor:
            self.sensor = sensor
        else:
            self.sensor = TSL2591(i2c=i2c, sda_pin=sda_pin, scl_pin=scl_pin)
        
        # Calibration storage (paper_id -> calibration_constant)
        self.calibrations = {}
        self.default_calibration = self.DEFAULT_CALIBRATION
        
        # Current paper selection (server-side state)
        self.current_paper_id = 'ilford_cooltone'  # Default paper from paper_database
        
        # Legacy filter system for backward compatibility (deprecated)
        self.filter_system = 'ilford'  # 'ilford', 'foma_fomaspeed', 'foma_fomatone'
        
        # Stored readings for contrast calculation
        self.highlight_lux = None
        self.shadow_lux = None
    
    def set_current_paper(self, paper_id):
        """
        Set the current paper selection.
        
        Args:
            paper_id: Paper identifier from paper_database (e.g., 'ilford_cooltone')
        """
        from lib.paper_database import get_paper_data
        paper_data = get_paper_data(paper_id)
        if paper_data:
            self.current_paper_id = paper_id
        else:
            raise ValueError(f"Invalid paper_id: {paper_id}")
    
    def get_current_paper(self):
        """Get the current paper ID."""
        return self.current_paper_id
    
    def set_filter_system(self, system):
        """
        Set the active filter system (legacy method for backward compatibility).
        
        Args:
            system: 'ilford', 'foma_fomaspeed', or 'foma_fomatone'
        """
        valid_systems = ['ilford', 'foma_fomaspeed', 'foma_fomatone']
        if system in valid_systems:
            self.filter_system = system
        else:
            raise ValueError(f"Invalid filter system. Use: {valid_systems}")
    
    def set_calibration(self, paper_id, calibration_constant):
        """
        Set calibration constant for a paper type.
        
        Args:
            paper_id: Unique identifier for paper (e.g., 'ilford_mg4_rc')
            calibration_constant: Lux × seconds for proper exposure
        """
        self.calibrations[paper_id] = calibration_constant
    
    def get_calibration(self, paper_id=None):
        """Get calibration constant for paper type."""
        if paper_id and paper_id in self.calibrations:
            return self.calibrations[paper_id]
        return self.default_calibration
    
    async def measure_lux_async(self, samples=5):
        """
        Take an averaged light measurement.
        
        Args:
            samples: Number of samples to average (default: 5)
        
        Returns:
            dict: Measurement result with lux, variance, and status
        """
        return await self.sensor.read_averaged_lux_async(samples=samples)
    
    def calculate_exposure_time(self, lux, calibration=None, filter_grade=None, paper_id=None):
        """
        Calculate exposure time from lux reading.
        
        Formula: time = calibration_constant / lux × filter_factor
        
        Args:
            lux: Measured illuminance in lux
            calibration: Calibration constant (lux × seconds)
            filter_grade: Filter grade for factor adjustment (optional)
                         Can be '', 'none', '00', '0', '1', '2', '3', '4', '5',
                         '2xY', 'Y', 'M1', '2xM1', 'M2', '2xM2'
            paper_id: Paper identifier to use (defaults to current_paper_id)
        
        Returns:
            float: Exposure time in seconds
        """
        if lux is None or lux <= 0:
            return None
        
        cal = calibration or self.default_calibration
        
        # Base exposure time
        base_time = cal / lux
        
        # Apply filter factor if specified
        # Empty string or 'none' means no filter (factor = 1.0)
        if filter_grade is not None and filter_grade != '' and filter_grade != 'none':
            from lib.paper_database import get_filter_data
            
            # Use specified paper_id or current paper
            pid = paper_id or self.current_paper_id
            
            # Get filter data from paper database
            filter_data = get_filter_data(pid, filter_grade)
            if filter_data:
                factor = filter_data['factor']
                base_time *= factor
        
        return base_time
    
    def calculate_delta_ev(self, highlight_lux, shadow_lux):
        """
        Calculate contrast range (ΔEV) from highlight and shadow readings.
        
        ΔEV = abs(log₂(shadow_lux / highlight_lux))
        
        Note: Shadow areas receive more light than highlight areas
        because they're less dense on the negative.
        
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
        
        import math
        delta_ev = abs(math.log2(shadow_lux / highlight_lux))
        
        return delta_ev
    
    def recommend_filter_grade(
        self,
        delta_ev,
        system=None,
        paper_id=None,
    ):
        """
        Recommend filter grade based on measured contrast.
        
        ISO R METHOD: Convert measured contrast to ISO Range (R) and
        match to the closest filter ISO R value for the selected paper.
        
        Args:
            delta_ev: Measured contrast range (EV stops)
            system: Filter system (deprecated, use paper_id instead)
            paper_id: Paper identifier to use (defaults to current_paper_id)
        
        Returns:
            dict: {
                'grade': str,                # Recommended filter grade
                'iso_r': int,                # ISO R value
                'factor': float,             # Exposure factor
                'match_quality': str,        # 'exact', 'close', 'acceptable', 'approximate'
                'reasoning': str             # Why this grade was selected
            }
        """
        if delta_ev is None:
            return None
        
        from lib.paper_database import get_paper_data, get_available_filters, get_filter_data
        
        # Use specified paper_id or current paper
        pid = paper_id or self.current_paper_id
        paper_data = get_paper_data(pid)
        
        if not paper_data:
            return None

        # ISO R target: delta_ev * 0.30 (log density) * 100
        iso_r_target = abs(delta_ev) * 30.0

        best_match = None
        best_diff = float('inf')

        # Get available filters for this paper
        available_filters = get_available_filters(pid)
        
        for grade in available_filters:
            # Skip "no filter" options when recommending a filter grade
            if grade == '' or grade == 'none':
                continue

            filter_data = get_filter_data(pid, grade)
            if not filter_data:
                continue

            iso_r = filter_data.get('iso_r')
            if iso_r is None:
                continue

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

        best_match['match_quality'] = match_quality
        best_match['reasoning'] = (
            f"ISO R target {iso_r_target:.0f} matches grade {best_match['grade']} "
            f"(ISO R {best_match['iso_r']}) with a {best_diff:.0f} difference"
        )

        return best_match
    
    
    def _iso_r_to_ev(self, iso_r):
        """Interpolate EV from ISO R value."""
        # Linear interpolation between known points
        sorted_pairs = sorted(self.ISO_R_TO_EV.items(), reverse=True)
        
        for i, (r, ev) in enumerate(sorted_pairs):
            if iso_r >= r:
                if i == 0:
                    return ev
                prev_r, prev_ev = sorted_pairs[i - 1]
                # Interpolate
                ratio = (iso_r - r) / (prev_r - r)
                return ev + ratio * (prev_ev - ev)
        
        # Below minimum
        return sorted_pairs[-1][1]
    
    def calculate_split_grade(self, highlight_lux, shadow_lux, calibration=None, system=None, paper_id=None):
        """
        Calculate split-grade exposure times (legacy method - uses fixed filters).
        
        Split-grade printing uses two exposures:
        1. Soft filter (controls highlights) - based on highlight lux
        2. Hard filter (controls shadows) - based on shadow lux
        
        Args:
            highlight_lux: Lux reading at highlight area
            shadow_lux: Lux reading at shadow area
            calibration: Calibration constant (optional)
            system: Filter system (deprecated, use paper_id instead)
            paper_id: Paper identifier to use (defaults to current_paper_id)
        
        Returns:
            dict: {
                'soft_filter': str,      # Recommended soft filter
                'hard_filter': str,      # Recommended hard filter
                'soft_time': float,      # Soft exposure time (seconds)
                'hard_time': float,      # Hard exposure time (seconds)
                'total_time': float,     # Total exposure time
                'delta_ev': float,       # Measured contrast
                'soft_factor': float,    # Soft filter factor
                'hard_factor': float     # Hard filter factor
            }
        """
        if highlight_lux is None or shadow_lux is None:
            return None
        
        if highlight_lux <= 0 or shadow_lux <= 0:
            return None
        
        from lib.paper_database import get_filter_data, get_paper_data
        
        cal = calibration or self.default_calibration
        
        # Use specified paper_id or current paper
        pid = paper_id or self.current_paper_id
        paper_data = get_paper_data(pid)
        
        if not paper_data:
            return None
        
        # Determine soft and hard filters based on paper manufacturer
        manufacturer = paper_data.get('manufacturer', 'Ilford').lower()
        
        if 'ilford' in manufacturer:
            soft_filter = '00'
            hard_filter = '5'
        else:  # FOMA
            soft_filter = '2xY'
            hard_filter = '2xM2'
        
        # Get filter data from paper database
        soft_filter_data = get_filter_data(pid, soft_filter)
        hard_filter_data = get_filter_data(pid, hard_filter)
        
        if not soft_filter_data or not hard_filter_data:
            return None
        
        soft_factor = soft_filter_data['factor']
        hard_factor = hard_filter_data['factor']
        
        # Calculate base times from lux readings
        # Soft exposure: targets highlight tone (near paper white)
        # Hard exposure: targets shadow detail (max black)
        soft_base_time = cal / highlight_lux
        hard_base_time = cal / shadow_lux
        
        # Apply filter factors
        soft_time = soft_base_time * soft_factor
        hard_time = hard_base_time * hard_factor
        
        # Calculate contrast
        delta_ev = self.calculate_delta_ev(highlight_lux, shadow_lux)
        
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
            'shadow_lux': shadow_lux
        }
    
    async def measure_highlight_async(self, samples=5):
        """
        Measure and store highlight reading.
        
        Place sensor at brightest area of projected image
        (thinnest part of negative = paper highlight).
        """
        result = await self.measure_lux_async(samples)
        if result and result.get('lux'):
            self.highlight_lux = result['lux']
        return result
    
    async def measure_shadow_async(self, samples=5):
        """
        Measure and store shadow reading.
        
        Place sensor at darkest area of projected image
        (densest part of negative = paper shadow).
        """
        result = await self.measure_lux_async(samples)
        if result and result.get('lux'):
            self.shadow_lux = result['lux']
        return result
    
    def _calculate_midpoint_exposure_time(
        self,
        highlight_lux,
        shadow_lux,
        recommended_grade,
        calibration=None,
    ):
        """
        Calculate exposure time from the mid-point (gray) lux.

        The midpoint lux is the geometric mean of highlight and shadow.
        Exposure time follows the Exposure Meter formula and then applies
        the recommended filter factor.

        Args:
            highlight_lux: Measured lux at highlight area
            shadow_lux: Measured lux at shadow area
            recommended_grade: Output from recommend_filter_grade()
            calibration: Optional calibration constant (uses default if None)

        Returns:
            dict: {
                'suggested_time': float,
                'midpoint_lux': float,
                'notes': str
            }
        """
        if not highlight_lux or not shadow_lux:
            return None

        cal = calibration or self.default_calibration

        import math
        lux_mid = math.sqrt(highlight_lux * shadow_lux)
        if lux_mid <= 0:
            return None

        filter_factor = recommended_grade.get(
            'factor',
            recommended_grade.get('filter_factor', 1.0)
        )

        suggested_time = (cal / lux_mid) * filter_factor

        notes = (
            "Midpoint exposure based on highlight/shadow geometric mean, "
            "using calibration constant and filter factor."
        )

        return {
            'suggested_time': round(suggested_time, 2),
            'midpoint_lux': round(lux_mid, 1),
            'notes': notes
        }
    
    def get_contrast_analysis(
        self,
        paper_id=None,
        calibration=None,
    ):
        """
        Get contrast analysis from stored highlight/shadow readings.
        
        Args:
            paper_id: Paper identifier to use (defaults to current_paper_id)
            calibration: Optional calibration constant (uses paper-specific or default if None)
        
        Returns:
            dict: Full analysis including ΔEV, recommended grade,
                  exposure times, and split-grade calculations
        """
        if self.highlight_lux is None or self.shadow_lux is None:
            return {
                'error': 'Missing highlight or shadow reading',
                'highlight_lux': self.highlight_lux,
                'shadow_lux': self.shadow_lux
            }
        
        # Use specified paper_id or current paper
        pid = paper_id or self.current_paper_id
        
        delta_ev = self.calculate_delta_ev(self.highlight_lux, self.shadow_lux)
        recommended = self.recommend_filter_grade(
            delta_ev,
            paper_id=pid,
        )
        split_grade = self.calculate_split_grade(self.highlight_lux, self.shadow_lux, paper_id=pid)
        
        # Calculate midpoint-based exposure time
        exposure_times = None
        if recommended:
            # Use provided calibration, or fall back to paper-specific/default
            cal = calibration if calibration else self.get_calibration(pid)
            exposure_times = self._calculate_midpoint_exposure_time(
                self.highlight_lux,
                self.shadow_lux,
                recommended,
                calibration=cal,
            )
        recommended_response = None
        if recommended:
            recommended_response = {
                'grade': recommended.get('grade'),
                'match_quality': recommended.get('match_quality'),
                'reasoning': recommended.get('reasoning')
            }

        return {
            'highlight_lux': self.highlight_lux,
            'shadow_lux': self.shadow_lux,
            'delta_ev': delta_ev,
            'recommended_grade': recommended_response,
            'split_grade': split_grade,
            'exposure_times': exposure_times
        }
    
    def calculate_split_grade_enhanced(self, highlight_lux, shadow_lux, 
                                       soft_filter=None, hard_filter=None,
                                       calibration=None, system=None):
        """
        Enhanced split-grade calculator with absolute exposure times.
        
        This method calculates both the filter recommendations AND the
        absolute exposure times for soft and hard exposures.
        
        Args:
            highlight_lux: Lux reading at highlight area
            shadow_lux: Lux reading at shadow area
            soft_filter: User-selected soft filter (optional, auto-selects if None)
            hard_filter: User-selected hard filter (optional, auto-selects if None)
            calibration: Calibration constant (lux × seconds)
            system: Filter system ('ilford', 'foma_fomaspeed', 'foma_fomatone')
        
        Returns:
            dict: Complete split-grade solution with:
                - delta_ev: Measured contrast range
                - soft_filter: Selected soft filter
                - hard_filter: Selected hard filter
                - soft_time: Soft exposure time (seconds)
                - hard_time: Hard exposure time (seconds)
                - total_time: Total exposure time
                - soft_percent: Soft exposure percentage
                - hard_percent: Hard exposure percentage
                - soft_factor: Soft filter factor
                - hard_factor: Hard filter factor
                - soft_printable_ev: Soft filter's printable EV range
                - hard_printable_ev: Hard filter's printable EV range
                - total_printable_ev: Combined printable EV range
                - match_quality: How well filters match the negative contrast
        """
        if highlight_lux is None or shadow_lux is None:
            return None
        
        if highlight_lux <= 0 or shadow_lux <= 0:
            return None
        
        # 1. Calculate ΔEV
        delta_ev = self.calculate_delta_ev(highlight_lux, shadow_lux)
        
        # 2. Get filter data for selected paper system
        cal = calibration or self.default_calibration
        system = system or self.filter_system
        filter_data = self.get_filter_data(system)
        
        # 3. Determine filters (user-specified or auto)
        if soft_filter is None or hard_filter is None:
            # Auto-select based on system (fixed filters for split-grade)
            if soft_filter is None:
                soft_filter = self._get_soft_filter_for_system(system)
            if hard_filter is None:
                hard_filter = self._get_hard_filter_for_system(system)
        
        # 4. Get filter factors
        if soft_filter not in filter_data:
            soft_filter = '00' if system == 'ilford' else '2xY'
        if hard_filter not in filter_data:
            hard_filter = '5' if system == 'ilford' else '2xM2'
        
        soft_factor = filter_data[soft_filter]['factor']
        hard_factor = filter_data[hard_filter]['factor']
        
        # 5. Calculate base times from lux readings
        #    Direct lux-based calculation (most intuitive)
        soft_base = cal / highlight_lux
        hard_base = cal / shadow_lux
        
        # 6. Apply filter factors
        soft_time = soft_base * soft_factor
        hard_time = hard_base * hard_factor
        
        # 7. Calculate proportions
        total_time = soft_time + hard_time
        soft_percent = (soft_time / total_time) * 100
        hard_percent = (hard_time / total_time) * 100
        
        # 8. Calculate expected paper contrast
        soft_printable_ev = self._iso_r_to_ev(filter_data[soft_filter]['iso_r'])
        hard_printable_ev = self._iso_r_to_ev(filter_data[hard_filter]['iso_r'])
        total_printable_ev = soft_printable_ev + hard_printable_ev
        
        # 9. Evaluate match quality
        match_quality = self._evaluate_split_match(delta_ev, total_printable_ev)
        
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
            'highlight_lux': highlight_lux,
            'shadow_lux': shadow_lux
        }
    
    def _get_soft_filter_for_system(self, system):
        """
        Get the soft filter for split-grade printing.
        
        Soft filter controls highlights (brighter areas).
        For split-grade, we use the softest filter available.
        
        Args:
            system: Filter system
        
        Returns:
            str: Soft filter identifier
        """
        if system == 'ilford':
            return '00'
        elif system.startswith('foma'):
            return '2xY'
        return '00'
    
    def _get_hard_filter_for_system(self, system):
        """
        Get the hard filter for split-grade printing.
        
        Hard filter controls shadows (darker areas).
        For split-grade, we use the hardest filter available.
        
        Args:
            system: Filter system
        
        Returns:
            str: Hard filter identifier
        """
        if system == 'ilford':
            return '5'
        elif system.startswith('foma'):
            return '2xM2'
        return '5'
    
    def _evaluate_split_match(self, delta_ev, total_printable_ev):
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
    
    def calculate_split_grade_heiland(
        self,
        highlight_lux,
        shadow_lux,
        calibration=None,
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
            calibration: Calibration constant (optional)
            system: Filter system (optional)
        
        Returns:
            dict: Enhanced split-grade results with Heiland-like features
        """
        if highlight_lux is None or shadow_lux is None:
            return None
        
        if highlight_lux <= 0 or shadow_lux <= 0:
            return None
        
        cal = calibration or self.default_calibration
        system = system or self.filter_system
        
        # Calculate contrast (ΔEV)
        delta_ev = self.calculate_delta_ev(highlight_lux, shadow_lux)
        
        # Use unified filter selection logic from paper_database.py
        # This ensures consistency with the enhanced algorithm
        from lib.paper_database import get_paper_data, get_available_filters
        
        filter_selection = get_filter_selection(delta_ev, system)
        soft_filter = filter_selection['soft_filter']
        hard_filter = filter_selection['hard_filter']
        selection_reason = filter_selection['description']
        contrast_level = filter_selection['contrast_level']
        
        # Get filter data from paper_database (not a method, it's a module function)
        paper_data = get_paper_data(system)
        if not paper_data:
            return None
        
        filter_data = paper_data.get('filters', {})
        
        # Check if filters exist in the system data
        if soft_filter not in filter_data:
            # Fallback to default filters for the system
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
        
        # Calculate base times
        soft_base_time = cal / highlight_lux
        hard_base_time = cal / shadow_lux
        
        # Apply filter factors
        soft_time = soft_base_time * soft_factor
        hard_time = hard_base_time * hard_factor
        
        # Apply unified optimization using validate_exposure_times
        # This ensures consistency with the enhanced algorithm
        soft_time_opt, hard_time_opt, optimization_applied = validate_exposure_times(
            soft_time, hard_time, None  # paper_id not needed for basic optimization
        )

        # Calculate percentages
        total_time = soft_time_opt + hard_time_opt
        if total_time > 0:
            soft_percent = (soft_time_opt / total_time) * 100
            hard_percent = (hard_time_opt / total_time) * 100
        else:
            soft_percent = 50.0
            hard_percent = 50.0
        
        # Calculate match quality using unified method
        soft_iso_r = filter_data[soft_filter]['iso_r']
        hard_iso_r = filter_data[hard_filter]['iso_r']
        soft_printable_ev = self._iso_r_to_ev(soft_iso_r)
        hard_printable_ev = self._iso_r_to_ev(hard_iso_r)
        total_printable_ev = soft_printable_ev + hard_printable_ev
        match_quality = self._evaluate_split_match(delta_ev, total_printable_ev)
        
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
            'system': system
        }
    
    def clear_readings(self):
        """Clear stored highlight and shadow readings."""
        self.highlight_lux = None
        self.shadow_lux = None
    
    def get_status(self):
        """Get light meter status including sensor status."""
        sensor_status = self.sensor.get_status()
        
        return {
            'sensor': sensor_status,
            'filter_system': self.filter_system,
            'calibration': self.default_calibration,
            'highlight_lux': self.highlight_lux,
            'shadow_lux': self.shadow_lux,
            'calibrations_stored': len(self.calibrations)
        }

