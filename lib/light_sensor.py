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
from machine import Pin, I2C


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
    ISO_R_TO_EV = {
        180: 8.0,   # Grade 00 - very soft
        160: 7.5,   # Grade 0
        130: 6.8,   # Grade 1
        110: 6.2,   # Grade 2 (normal)
        90: 5.6,    # Grade 3
        60: 4.8,    # Grade 4
        40: 4.0     # Grade 5 - very hard
    }
    
    # Ilford Multigrade filter data
    ILFORD_FILTERS = {
        '00': {'iso_r': 180, 'factor': 1.6},
        '0':  {'iso_r': 160, 'factor': 1.4},
        '1':  {'iso_r': 130, 'factor': 1.3},
        '2':  {'iso_r': 110, 'factor': 1.1},
        '3':  {'iso_r': 90,  'factor': 0.9},
        '4':  {'iso_r': 60,  'factor': 0.6},
        '5':  {'iso_r': 40,  'factor': 0.4},
        'none': {'iso_r': 110, 'factor': 1.0}
    }
    
    # FOMA filter data - FOMASPEED / FOMABROM Variant III
    FOMA_FOMASPEED_FILTERS = {
        '2xY':  {'iso_r': 135, 'factor': 1.6},
        'Y':    {'iso_r': 120, 'factor': 1.4},
        'none': {'iso_r': 105, 'factor': 1.0},
        'M1':   {'iso_r': 90,  'factor': 1.4},
        '2xM1': {'iso_r': 80,  'factor': 2.1},
        'M2':   {'iso_r': 65,  'factor': 2.6},
        '2xM2': {'iso_r': 55,  'factor': 4.6}
    }
    
    # FOMA filter data - FOMATONE MG / MG Classic
    FOMA_FOMATONE_FILTERS = {
        '2xY':  {'iso_r': 120, 'factor': 2.0},
        'Y':    {'iso_r': 105, 'factor': 1.5},
        'none': {'iso_r': 90,  'factor': 1.0},
        'M1':   {'iso_r': 80,  'factor': 1.5},
        '2xM1': {'iso_r': 75,  'factor': 1.8},
        'M2':   {'iso_r': 65,  'factor': 2.0},
        '2xM2': {'iso_r': 55,  'factor': 3.0}
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
        
        # Filter system selection
        self.filter_system = 'ilford'  # 'ilford', 'foma_fomaspeed', 'foma_fomatone'
        
        # Stored readings for contrast calculation
        self.highlight_lux = None
        self.shadow_lux = None
    
    def set_filter_system(self, system):
        """
        Set the active filter system.
        
        Args:
            system: 'ilford', 'foma_fomaspeed', or 'foma_fomatone'
        """
        valid_systems = ['ilford', 'foma_fomaspeed', 'foma_fomatone']
        if system in valid_systems:
            self.filter_system = system
        else:
            raise ValueError(f"Invalid filter system. Use: {valid_systems}")
    
    def get_filter_data(self, system=None):
        """Get filter data for current or specified system."""
        system = system or self.filter_system
        
        if system == 'ilford':
            return self.ILFORD_FILTERS
        elif system == 'foma_fomaspeed':
            return self.FOMA_FOMASPEED_FILTERS
        elif system == 'foma_fomatone':
            return self.FOMA_FOMATONE_FILTERS
        else:
            return self.ILFORD_FILTERS
    
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
    
    def calculate_exposure_time(self, lux, calibration=None, filter_grade=None):
        """
        Calculate exposure time from lux reading.
        
        Formula: time = calibration_constant / lux
        
        Args:
            lux: Measured illuminance in lux
            calibration: Calibration constant (lux × seconds)
            filter_grade: Filter grade for factor adjustment (optional)
        
        Returns:
            float: Exposure time in seconds
        """
        if lux is None or lux <= 0:
            return None
        
        cal = calibration or self.default_calibration
        
        # Base exposure time
        base_time = cal / lux
        
        # Apply filter factor if specified
        if filter_grade:
            filter_data = self.get_filter_data()
            if filter_grade in filter_data:
                factor = filter_data[filter_grade]['factor']
                base_time *= factor
        
        return base_time
    
    def calculate_delta_ev(self, highlight_lux, shadow_lux):
        """
        Calculate contrast range (ΔEV) from highlight and shadow readings.
        
        ΔEV = log₂(shadow_lux / highlight_lux)
        
        Note: Shadow areas receive more light than highlight areas
        because they're less dense on the negative.
        
        Args:
            highlight_lux: Lux reading at paper highlight area
            shadow_lux: Lux reading at paper shadow area
        
        Returns:
            float: Contrast range in EV stops
        """
        if highlight_lux is None or shadow_lux is None:
            return None
        
        if highlight_lux <= 0 or shadow_lux <= 0:
            return None
        
        import math
        delta_ev = math.log2(shadow_lux / highlight_lux)
        
        return delta_ev
    
    def recommend_filter_grade(self, delta_ev, system=None):
        """
        Recommend filter grade based on measured contrast.
        
        Matches the negative's contrast range to a filter grade
        whose ISO R provides appropriate paper exposure latitude.
        
        Args:
            delta_ev: Measured contrast range (EV stops)
            system: Filter system ('ilford', 'foma_fomaspeed', 'foma_fomatone')
        
        Returns:
            dict: {
                'grade': str,           # Recommended filter grade
                'iso_r': int,           # ISO R value
                'factor': float,        # Exposure factor
                'printable_ev': float,  # Paper's exposure range
                'match_quality': str    # 'exact', 'close', 'approximate'
            }
        """
        if delta_ev is None:
            return None
        
        filter_data = self.get_filter_data(system)
        
        best_match = None
        best_diff = float('inf')
        
        for grade, data in filter_data.items():
            iso_r = data['iso_r']
            
            # Find closest ISO R value in our EV mapping
            printable_ev = None
            for r, ev in self.ISO_R_TO_EV.items():
                if abs(r - iso_r) < abs(r - best_diff):
                    printable_ev = ev
                    break
            
            if printable_ev is None:
                # Interpolate EV from ISO R
                printable_ev = self._iso_r_to_ev(iso_r)
            
            diff = abs(printable_ev - abs(delta_ev))
            
            if diff < best_diff:
                best_diff = diff
                best_match = {
                    'grade': grade,
                    'iso_r': iso_r,
                    'factor': data['factor'],
                    'printable_ev': printable_ev
                }
        
        if best_match:
            # Determine match quality
            if best_diff < 0.2:
                best_match['match_quality'] = 'exact'
            elif best_diff < 0.5:
                best_match['match_quality'] = 'close'
            else:
                best_match['match_quality'] = 'approximate'
        
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
    
    def calculate_split_grade(self, highlight_lux, shadow_lux, calibration=None, system=None):
        """
        Calculate split-grade exposure times.
        
        Split-grade printing uses two exposures:
        1. Soft filter (controls highlights) - based on highlight lux
        2. Hard filter (controls shadows) - based on shadow lux
        
        Args:
            highlight_lux: Lux reading at highlight area
            shadow_lux: Lux reading at shadow area
            calibration: Calibration constant (optional)
            system: Filter system (optional)
        
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
        
        cal = calibration or self.default_calibration
        system = system or self.filter_system
        filter_data = self.get_filter_data(system)
        
        # Determine soft and hard filters based on system
        if system == 'ilford':
            soft_filter = '00'
            hard_filter = '5'
        elif system == 'foma_fomaspeed':
            soft_filter = '2xY'
            hard_filter = '2xM2'
        else:  # foma_fomatone
            soft_filter = '2xY'
            hard_filter = '2xM2'
        
        soft_factor = filter_data[soft_filter]['factor']
        hard_factor = filter_data[hard_filter]['factor']
        
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
    
    def get_contrast_analysis(self):
        """
        Get contrast analysis from stored highlight/shadow readings.
        
        Returns:
            dict: Full analysis including ΔEV, recommended grade,
                  and split-grade calculations
        """
        if self.highlight_lux is None or self.shadow_lux is None:
            return {
                'error': 'Missing highlight or shadow reading',
                'highlight_lux': self.highlight_lux,
                'shadow_lux': self.shadow_lux
            }
        
        delta_ev = self.calculate_delta_ev(self.highlight_lux, self.shadow_lux)
        recommended = self.recommend_filter_grade(delta_ev)
        split_grade = self.calculate_split_grade(self.highlight_lux, self.shadow_lux)
        
        return {
            'highlight_lux': self.highlight_lux,
            'shadow_lux': self.shadow_lux,
            'delta_ev': delta_ev,
            'recommended_grade': recommended,
            'split_grade': split_grade
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
