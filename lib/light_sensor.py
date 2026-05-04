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
import json
import time
import math
from machine import Pin, I2C
from lib.paper_database import get_paper_data
from lib.splitgrade_enhanced import (
    calculate_delta_ev as _calculate_delta_ev,
    calculate_split_grade_legacy as _calculate_split_grade_legacy,
    calculate_split_grade_heiland as _calculate_split_grade_heiland,
)
from lib.exposure_calc import (
    calculate_exposure_time as _calculate_exposure_time,
    calculate_virtual_proof_sample as _calculate_virtual_proof_sample,
    recommend_filter_grade as _recommend_filter_grade,
    calculate_midpoint_exposure_time as _calculate_midpoint_exposure_time,
    validate_paper_database_loge_range as _validate_paper_database_loge_range,
)


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
    REG_STATUS = 0x13   # Status register (AVALID in bit 0)
    REG_C0DATAL = 0x14  # Channel 0 data (visible + IR)
    REG_C1DATAL = 0x16  # Channel 1 data (IR only)

    # Enable register bits
    ENABLE_PON = 0x01   # Power ON
    ENABLE_AEN = 0x02   # ALS Enable

    # Status register bits
    STATUS_AVALID = 0x01   # ALS data valid (new integration completed)
    
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
    
    # LUX calculation coefficients
    # LUX_DF is the TSL2591 device factor (from datasheet / community).
    # The TSL2591 datasheet does NOT publish B/C/D piecewise coefficients
    # (those belong to the TSL2561); the accepted TSL2591 formula is
    # lux = (ch0 - ch1) * (1 - ch1/ch0) / cpl.
    LUX_DF = 408.0
    
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
        self._needs_settle = False  # True right after a gain/integration change

        # Dark-offset subtraction: { (gain_reg, int_reg): (ch0_offset, ch1_offset) }
        # Populated by calibrate_dark_offset() and loaded from persistent storage.
        self._dark_offsets = {}

        # Per-device gain factor overrides (keyed by gain register value).
        # Empty = use GAIN_FACTORS defaults. Populated by calibrate_gain_factors().
        self._gain_factors_override = {}

        # Hysteresis state for auto_gain (last ch0 used to decide direction)
        self._last_auto_gain_ch0 = None
        
        try:
            # Use provided I2C or create new instance
            if i2c:
                self.i2c = i2c
            else:
                self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
            
            # Verify sensor presence
            if self._verify_sensor():
                # Datasheet power-up sequence: PON first, wait >=2.7ms, then PON|AEN.
                self._write_register(self.REG_ENABLE, self.ENABLE_PON)
                time.sleep_ms(3)
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
        # The ADC may be part-way through an integration with the old
        # settings; mark the next read as "stale" so callers can discard it.
        self._needs_settle = True
    
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
    
    def _is_avalid(self):
        """Check status register AVALID bit (new integration completed)."""
        try:
            return bool(self._read_register(self.REG_STATUS) & self.STATUS_AVALID)
        except Exception:
            return False

    def _apply_dark_offset(self, ch0, ch1):
        """Subtract stored dark offsets for the current gain/integration."""
        key = (self._gain, self._integration)
        offsets = self._dark_offsets.get(key)
        if offsets is None:
            return ch0, ch1
        off0, off1 = offsets
        adj0 = ch0 - off0
        adj1 = ch1 - off1
        if adj0 < 0:
            adj0 = 0
        if adj1 < 0:
            adj1 = 0
        return adj0, adj1

    def get_raw_data(self):
        """
        Read raw channel data from sensor. Polls AVALID for fresh data.

        Returns:
            tuple: (channel0, channel1) ADC values with dark offset applied
        """
        if not self.connected:
            return None, None

        try:
            integration_ms = self.INTEGRATION_TIMES_MS[self._integration]
            # Poll AVALID; give up after 2x integration as a hard timeout.
            deadline = time.ticks_add(time.ticks_ms(), integration_ms * 2 + 20)
            while not self._is_avalid():
                if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                    self.last_error = "AVALID timeout"
                    return None, None
                time.sleep_ms(5)

            ch0 = self._read_u16(self.REG_C0DATAL)
            ch1 = self._read_u16(self.REG_C1DATAL)
            return self._apply_dark_offset(ch0, ch1)

        except Exception as e:
            self.last_error = str(e)
            return None, None

    async def get_raw_data_async(self):
        """Async version of get_raw_data() — non-blocking AVALID poll."""
        if not self.connected:
            return None, None

        try:
            integration_ms = self.INTEGRATION_TIMES_MS[self._integration]
            # Sleep for most of the integration period before polling — the
            # AVALID bit can't go high before the integration completes, so
            # polling early just wastes I²C traffic.
            await asyncio.sleep_ms(max(0, integration_ms - 10))

            deadline = time.ticks_add(time.ticks_ms(), integration_ms + 20)
            while not self._is_avalid():
                if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                    self.last_error = "AVALID timeout"
                    return None, None
                await asyncio.sleep_ms(5)

            ch0 = self._read_u16(self.REG_C0DATAL)
            ch1 = self._read_u16(self.REG_C1DATAL)
            return self._apply_dark_offset(ch0, ch1)

        except Exception as e:
            self.last_error = str(e)
            return None, None

    def get_raw_data_unadjusted(self):
        """
        Read raw channel data WITHOUT dark-offset subtraction.
        Used by calibrate_dark_offset() to capture the baseline.
        """
        if not self.connected:
            return None, None
        try:
            integration_ms = self.INTEGRATION_TIMES_MS[self._integration]
            deadline = time.ticks_add(time.ticks_ms(), integration_ms * 2 + 20)
            while not self._is_avalid():
                if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                    self.last_error = "AVALID timeout"
                    return None, None
                time.sleep_ms(5)
            ch0 = self._read_u16(self.REG_C0DATAL)
            ch1 = self._read_u16(self.REG_C1DATAL)
            return ch0, ch1
        except Exception as e:
            self.last_error = str(e)
            return None, None

    async def get_raw_data_unadjusted_async(self):
        """Async version of get_raw_data_unadjusted()."""
        if not self.connected:
            return None, None
        try:
            integration_ms = self.INTEGRATION_TIMES_MS[self._integration]
            await asyncio.sleep_ms(max(0, integration_ms - 10))
            deadline = time.ticks_add(time.ticks_ms(), integration_ms + 20)
            while not self._is_avalid():
                if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                    self.last_error = "AVALID timeout"
                    return None, None
                await asyncio.sleep_ms(5)
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

        # Gain factor: per-device calibrated override takes precedence.
        gain_factor = self._gain_factors_override.get(
            self._gain,
            self.GAIN_FACTORS.get(self._gain, 25.0),
        )

        integration_ms = self.INTEGRATION_TIMES_MS.get(self._integration, 300)

        # Saturation limits per datasheet: 100ms = 37888 full-scale,
        # 200–600ms = 65535 full-scale. Trip one count before to be safe.
        sat_limit = 37887 if self._integration == self.INTEGRATIONTIME_100MS else 65535
        if ch0 >= sat_limit or ch1 >= sat_limit:
            self.last_error = "Sensor saturated - lower gain or shorten integration"
            return None

        # No-light guard: ch0 == 0 means nothing hit the visible+IR channel.
        if ch0 == 0:
            return 0.0

        # Counts per lux: CPL = (ATIME_ms * AGAIN) / DF
        cpl = (integration_ms * gain_factor) / self.LUX_DF
        if cpl <= 0:
            return None

        # Standard TSL2591 lux formula (Adafruit / community consensus).
        # ch1/ch0 is the IR ratio; the (1 - ch1/ch0) factor attenuates
        # the reading as the scene gets more IR-heavy (e.g. tungsten).
        lux = (ch0 - ch1) * (1.0 - ch1 / ch0) / cpl

        # Negative lux means the IR channel exceeded the visible channel —
        # signal invalid rather than clamping to zero.
        if lux < 0:
            self.last_error = "Invalid reading (ch1 > ch0)"
            return None

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

        Discards the first read if gain/integration changed since the last
        read (the ADC would still be mid-integration with stale settings),
        and trims the high+low outliers before averaging when enough
        samples are available — this rejects enlarger flicker spikes and
        noise without hiding real variance.

        Args:
            samples: Number of samples to keep after trimming (default: 5)
            delay_ms: Delay between samples in ms (default: 50)

        Returns:
            dict: {
                'lux': float,           # Trimmed-mean lux value
                'min': float,           # Minimum reading (pre-trim)
                'max': float,           # Maximum reading (pre-trim)
                'samples': int,         # Number of valid samples used
                'variance': float       # Reading variance (stability indicator)
            }
        """
        if self._needs_settle:
            await self.read_lux_async()
            self._needs_settle = False

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

        min_lux = min(readings)
        max_lux = max(readings)

        # Trim one high and one low outlier once we have >=5 samples.
        # Below that, trimming removes too much signal.
        if len(readings) >= 5:
            trimmed = sorted(readings)[1:-1]
        else:
            trimmed = readings

        avg_lux = sum(trimmed) / len(trimmed)

        if len(trimmed) > 1:
            variance = sum((x - avg_lux) ** 2 for x in trimmed) / len(trimmed)
        else:
            variance = 0.0

        self.last_lux = avg_lux

        return {
            'lux': avg_lux,
            'min': min_lux,
            'max': max_lux,
            'samples': len(trimmed),
            'variance': variance
        }
    
    # Gain ordering, used by auto_gain and calibrate_gain_factors.
    _GAIN_ORDER = (GAIN_LOW, GAIN_MED, GAIN_HIGH, GAIN_MAX)

    def auto_gain(self):
        """
        Adjust gain for optimal sensitivity, one step per call, with
        hysteresis: step DOWN only when ch0 is clearly saturated, step UP
        only when ch0 is clearly below the noise floor. The dead-zone
        between 5000 and 55000 means steady scenes don't ping-pong.

        Returns:
            int: New gain setting
        """
        ch0, ch1 = self.get_raw_data()
        if ch0 is None:
            return self._gain

        # Step down (reduce gain) if saturated
        if ch0 >= 55000 or ch1 >= 55000:
            idx = self._GAIN_ORDER.index(self._gain)
            if idx > 0:
                self.set_gain(self._GAIN_ORDER[idx - 1])

        # Step up (increase gain) if well below useful range
        elif ch0 < 5000 and ch1 < 5000:
            idx = self._GAIN_ORDER.index(self._gain)
            if idx < len(self._GAIN_ORDER) - 1:
                self.set_gain(self._GAIN_ORDER[idx + 1])

        return self._gain

    # ── Dark-offset calibration ─────────────────────────────────────────

    async def calibrate_dark_offset(self, samples=16):
        """
        Capture the dark-signal baseline for the CURRENT (gain, integration)
        pair. Caller MUST ensure the sensor is in darkness (enlarger OFF,
        sensor covered or in the closed darkroom).

        The offset is averaged across `samples` reads and stored in
        self._dark_offsets keyed by (gain_reg, int_reg). Subsequent reads
        automatically subtract it.

        Returns:
            dict: {'ch0': float, 'ch1': float, 'samples': int} or
                  {'error': str} on failure.
        """
        if not self.connected:
            return {'error': 'Sensor not connected'}

        # Discard any stale integration first.
        if self._needs_settle:
            await self.get_raw_data_unadjusted_async()
            self._needs_settle = False

        ch0_sum = 0
        ch1_sum = 0
        count = 0
        for _ in range(samples):
            ch0, ch1 = await self.get_raw_data_unadjusted_async()
            if ch0 is None:
                continue
            ch0_sum += ch0
            ch1_sum += ch1
            count += 1

        if count == 0:
            return {'error': self.last_error or 'No valid samples'}

        ch0_avg = ch0_sum / count
        ch1_avg = ch1_sum / count
        self._dark_offsets[(self._gain, self._integration)] = (ch0_avg, ch1_avg)
        return {'ch0': ch0_avg, 'ch1': ch1_avg, 'samples': count}

    def clear_dark_offsets(self):
        """Remove all stored dark-offset calibrations."""
        self._dark_offsets = {}

    def get_dark_offsets(self):
        """Return stored dark offsets as a JSON-safe dict."""
        result = {}
        for (gain, integ), (off0, off1) in self._dark_offsets.items():
            key = "{:d}_{:d}".format(gain, integ)
            result[key] = {
                'gain_reg': gain,
                'integration_reg': integ,
                'integration_ms': self.INTEGRATION_TIMES_MS.get(integ, 0),
                'ch0_offset': off0,
                'ch1_offset': off1,
            }
        return result

    def load_dark_offsets(self, offsets):
        """
        Load dark offsets from a dict produced by get_dark_offsets().
        Silently skips entries that don't match the current driver layout.
        """
        self._dark_offsets = {}
        if not offsets:
            return
        for entry in offsets.values():
            try:
                g = int(entry['gain_reg'])
                i = int(entry['integration_reg'])
                o0 = float(entry['ch0_offset'])
                o1 = float(entry['ch1_offset'])
                self._dark_offsets[(g, i)] = (o0, o1)
            except (KeyError, TypeError, ValueError):
                continue

    # ── Per-device gain factor calibration ──────────────────────────────

    async def calibrate_gain_factors(self, reference_gain=None, samples=8):
        """
        Measure the actual gain ratios of this specific sensor.

        Caller must point the sensor at a STEADY light source (not flicker-
        prone), bright enough to give a useful ch0 reading at LOW gain but
        not so bright that MED saturates. MED gain + 300ms integration is
        a sensible default test condition.

        The reference gain (default MED) keeps its nominal factor; other
        gain stages are scaled by their measured ratio to the reference.

        Returns:
            dict: { 'factors': {gain_reg: float, ...}, 'reference_gain': int }
        """
        if not self.connected:
            return {'error': 'Sensor not connected'}

        if reference_gain is None:
            reference_gain = self.GAIN_MED

        saved_gain = self._gain
        measurements = {}

        try:
            for gain in self._GAIN_ORDER:
                self.set_gain(gain)
                await self.get_raw_data_unadjusted_async()  # settle
                self._needs_settle = False
                total = 0
                count = 0
                saturated = False
                for _ in range(samples):
                    ch0, ch1 = await self.get_raw_data_unadjusted_async()
                    if ch0 is None:
                        continue
                    # Skip saturated stages; we can't measure a ratio from them.
                    sat = 37887 if self._integration == self.INTEGRATIONTIME_100MS else 65534
                    if ch0 >= sat or ch1 >= sat:
                        saturated = True
                        break
                    total += ch0
                    count += 1
                if saturated or count == 0:
                    measurements[gain] = None
                else:
                    measurements[gain] = total / count
        finally:
            self.set_gain(saved_gain)

        ref_counts = measurements.get(reference_gain)
        if not ref_counts:
            return {'error': 'Reference gain measurement failed or saturated'}

        ref_nominal = self.GAIN_FACTORS[reference_gain]
        factors = {}
        for gain, counts in measurements.items():
            if counts is None:
                # Keep nominal for stages that couldn't be measured.
                factors[gain] = self.GAIN_FACTORS[gain]
            else:
                factors[gain] = (counts / ref_counts) * ref_nominal

        self._gain_factors_override = factors
        return {'factors': factors, 'reference_gain': reference_gain}

    def clear_gain_factors(self):
        """Remove per-device gain calibration and fall back to nominal."""
        self._gain_factors_override = {}

    def get_gain_factors(self):
        """Return active gain factors (override if set, else nominal)."""
        if self._gain_factors_override:
            return dict(self._gain_factors_override)
        return dict(self.GAIN_FACTORS)

    def load_gain_factors(self, factors):
        """Load gain factors from a dict {gain_reg_int: factor_float}."""
        self._gain_factors_override = {}
        if not factors:
            return
        for key, val in factors.items():
            try:
                g = int(key)
                f = float(val)
                if g in self.GAIN_FACTORS and f > 0:
                    self._gain_factors_override[g] = f
            except (TypeError, ValueError):
                continue
    
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
            'last_error': self.last_error,
            'dark_offsets': self.get_dark_offsets(),
            'dark_offset_active': (self._gain, self._integration) in self._dark_offsets,
            'gain_factors': self.get_gain_factors(),
            'gain_calibrated': bool(self._gain_factors_override),
        }


class DarkroomLightMeter:
    """
    High-level darkroom light meter using TSL2591 sensor.
    
    Provides photographic-specific functions:
    - Base exposure calculation
    - Contrast measurement (ΔEV)
    - Filter grade recommendation
    - Split-grade exposure calculation
    
    This class owns sensor hardware and measurement state.
    Pure computation is delegated to:
      - lib.exposure_calc (exposure time, filter recommendation, virtual proof)
      - lib.splitgrade_enhanced (split-grade calculations, ΔEV)
    
    Calibration:
    The light meter needs calibration per paper type. The calibration
    constant (lux-seconds) represents the exposure needed for a proper print.
    """
    
    # Default calibration constant (lux × seconds)
    DEFAULT_CALIBRATION = 1000.0

    # Where dark offsets + per-device gain factors are persisted.
    CALIBRATION_FILE = "light_meter_calibration.json"

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

        # Per-paper split-grade tunables (all stops, float). Shape:
        # { paper_id: {'overall_offset_stops': float, 'contrast_bias_stops': float,
        #              'highlight_trim_stops': float, 'shadow_trim_stops': float,
        #              'contrast_highlight_trim_stops': float,
        #              'contrast_shadow_trim_stops': float,
        #              'ca_overall_offset_stops': float,
        #              'ca_contrast_bias_stops': float} }
        self.split_settings = {}

        # Current paper selection (server-side state)
        self.current_paper_id = 'ilford_cooltone'

        # Legacy filter system for backward compatibility (deprecated)
        self.filter_system = 'ilford'

        # Stored readings for contrast calculation
        self.highlight_lux = None
        self.shadow_lux = None

        # Load persisted sensor calibration (dark offsets + gain factors)
        self._load_sensor_calibration()

    def _load_sensor_calibration(self):
        """Load dark offsets and gain factors from CALIBRATION_FILE, if present."""
        try:
            with open(self.CALIBRATION_FILE, 'r') as f:
                data = json.load(f)
        except (OSError, ValueError):
            return

        if not isinstance(data, dict):
            return

        dark = data.get('dark_offsets')
        if dark:
            self.sensor.load_dark_offsets(dark)

        gain = data.get('gain_factors')
        if gain:
            self.sensor.load_gain_factors(gain)

        split = data.get('split_settings')
        if isinstance(split, dict):
            self.split_settings = {
                str(pid): dict(s) for pid, s in split.items() if isinstance(s, dict)
            }

    def _save_sensor_calibration(self):
        """Persist dark offsets, gain factors, and split-grade settings to CALIBRATION_FILE."""
        payload = {
            'dark_offsets': self.sensor.get_dark_offsets(),
            # Store gain factors only if user-calibrated (not nominal defaults).
            'gain_factors': (
                {str(k): v for k, v in self.sensor._gain_factors_override.items()}
                if self.sensor._gain_factors_override else {}
            ),
            'split_settings': self.split_settings,
        }
        try:
            with open(self.CALIBRATION_FILE, 'w') as f:
                json.dump(payload, f)
        except OSError as e:
            print(f"WARNING: failed to save {self.CALIBRATION_FILE}: {e}")
    
    # ── Paper / calibration state ─────────────────────────────────────
    
    def set_current_paper(self, paper_id):
        """Set the current paper selection."""
        paper_data = get_paper_data(paper_id)
        if paper_data:
            self.current_paper_id = paper_id
        else:
            raise ValueError(f"Invalid paper_id: {paper_id}")
    
    def get_current_paper(self):
        """Get the current paper ID."""
        return self.current_paper_id
    
    def set_filter_system(self, system):
        """Set the active filter system (legacy, deprecated)."""
        valid_systems = ['ilford', 'foma_fomaspeed', 'foma_fomatone']
        if system in valid_systems:
            self.filter_system = system
        else:
            raise ValueError(f"Invalid filter system. Use: {valid_systems}")
    
    def set_calibration(self, paper_id, calibration_constant):
        """Set calibration constant for a paper type."""
        self.calibrations[paper_id] = calibration_constant
    
    def get_calibration(self, paper_id=None):
        """Get calibration constant for paper type."""
        if paper_id and paper_id in self.calibrations:
            return self.calibrations[paper_id]
        return self.default_calibration

    # ── Per-paper split-grade settings (zone targets + trim stops) ────

    SPLIT_DEFAULTS = {
        # Split-Grade Analyzer tunables.
        'overall_offset_stops': 0.0,
        'contrast_bias_stops': 0.0,
        # highlight_trim multiplies the soft leg; shadow_trim multiplies the
        # hard leg. Named per the dominant tone each leg controls in real
        # paper (soft saturates at shadow → soft leg's effect lives mostly
        # at the highlight; hard's toe at highlight → hard leg's effect
        # lives mostly at the shadow).
        'highlight_trim_stops': 0.0,
        'shadow_trim_stops': 0.0,
        # Contrast Analyzer tunables (separate state so the two tools have
        # independent knobs). Per-paper, persisted alongside split-grade.
        'contrast_highlight_trim_stops': 0.0,
        'contrast_shadow_trim_stops': 0.0,
        'ca_overall_offset_stops': 0.0,
        'ca_contrast_bias_stops': 0.0,
    }

    def get_split_settings(self, paper_id=None):
        """Get split-grade settings for a paper, falling back to defaults."""
        pid = paper_id or self.current_paper_id
        stored = self.split_settings.get(pid, {}) if pid else {}
        merged = dict(self.SPLIT_DEFAULTS)
        for key, value in stored.items():
            if key in merged:
                merged[key] = value
        return merged

    def set_split_settings(self, paper_id, **kwargs):
        """
        Update split-grade settings for a paper.

        Accepted keys (all stops, float): overall_offset_stops,
        contrast_bias_stops, highlight_trim_stops, shadow_trim_stops,
        contrast_highlight_trim_stops, contrast_shadow_trim_stops,
        ca_overall_offset_stops, ca_contrast_bias_stops.
        """
        if not paper_id:
            raise ValueError("paper_id is required")
        current = dict(self.split_settings.get(paper_id, {}))
        # Drop legacy keys if present from older saves; the new algorithm
        # replaced zone targets with overall_offset / contrast_bias and
        # renamed soft_trim/hard_trim to highlight_trim/shadow_trim.
        current.pop('highlight_zone', None)
        current.pop('shadow_zone', None)
        current.pop('soft_trim_stops', None)
        current.pop('hard_trim_stops', None)
        for key in (
            'overall_offset_stops',
            'contrast_bias_stops',
            'highlight_trim_stops',
            'shadow_trim_stops',
            'contrast_highlight_trim_stops',
            'contrast_shadow_trim_stops',
            'ca_overall_offset_stops',
            'ca_contrast_bias_stops',
        ):
            if key in kwargs and kwargs[key] is not None:
                current[key] = float(kwargs[key])
        self.split_settings[paper_id] = current
        self._save_sensor_calibration()
        return self.get_split_settings(paper_id)

    def clear_split_settings(self, paper_id):
        """Remove stored split-grade settings for a paper (revert to defaults)."""
        if paper_id in self.split_settings:
            del self.split_settings[paper_id]
            self._save_sensor_calibration()

    # ── Sensor measurements ───────────────────────────────────────────
    
    async def measure_lux_async(self, samples=5):
        """Take an averaged light measurement."""
        return await self.sensor.read_averaged_lux_async(samples=samples)
    
    async def measure_highlight_async(self, samples=5):
        """Measure and store highlight reading."""
        result = await self.measure_lux_async(samples)
        if result and result.get('lux'):
            self.highlight_lux = result['lux']
        return result
    
    async def measure_shadow_async(self, samples=5):
        """Measure and store shadow reading."""
        result = await self.measure_lux_async(samples)
        if result and result.get('lux'):
            self.shadow_lux = result['lux']
        return result
    
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
            'calibrations_stored': len(self.calibrations),
        }
    
    # ── Delegation: exposure calculations (lib.exposure_calc) ─────────
    
    def calculate_exposure_time(self, lux, calibration=None, filter_grade=None, paper_id=None):
        """Calculate exposure time from lux reading."""
        return _calculate_exposure_time(
            lux,
            calibration=calibration or self.default_calibration,
            filter_grade=filter_grade,
            paper_id=paper_id or self.current_paper_id,
        )
    
    def calculate_virtual_proof_sample(self, lux, reference_lux=None,
                                       paper_id=None, filter_grade=None,
                                       calibration=None):
        """Calculate a virtual proof sample (predicted print density)."""
        return _calculate_virtual_proof_sample(
            lux,
            reference_lux=reference_lux,
            paper_id=paper_id or self.current_paper_id,
            filter_grade=filter_grade,
            calibration=calibration or self.default_calibration,
        )
    
    def recommend_filter_grade(self, delta_ev, system=None, paper_id=None):
        """Recommend filter grade based on measured contrast."""
        return _recommend_filter_grade(
            delta_ev,
            paper_id=paper_id or self.current_paper_id,
        )
    
    def validate_paper_database_loge_range(self):
        """Validate that all papers in the database have logE_range defined."""
        return _validate_paper_database_loge_range()
    
    # ── Delegation: split-grade calculations (lib.splitgrade_enhanced) ─
    
    def calculate_delta_ev(self, highlight_lux, shadow_lux):
        """Calculate contrast range (ΔEV) from highlight and shadow readings."""
        return _calculate_delta_ev(highlight_lux, shadow_lux)
    
    def calculate_split_grade(self, highlight_lux, shadow_lux,
                              calibration=None, system=None, paper_id=None):
        """Calculate split-grade exposure times (legacy, fixed filters)."""
        return _calculate_split_grade_legacy(
            highlight_lux,
            shadow_lux,
            calibration=calibration or self.default_calibration,
            paper_id=paper_id or self.current_paper_id,
        )
    
    def calculate_split_grade_heiland(self, highlight_lux, shadow_lux,
                                      calibration=None, system=None,
                                      overall_offset_stops=None,
                                      contrast_bias_stops=None,
                                      highlight_trim_stops=None,
                                      shadow_trim_stops=None):
        """RH-Designs-style split-grade. Tunables fall back to per-paper
        stored split_settings (or defaults) when not supplied."""
        paper_id = system or self.current_paper_id
        settings = self.get_split_settings(paper_id)
        return _calculate_split_grade_heiland(
            highlight_lux,
            shadow_lux,
            calibration=calibration or self.get_calibration(paper_id),
            system=paper_id,
            overall_offset_stops=(
                overall_offset_stops if overall_offset_stops is not None
                else settings['overall_offset_stops']
            ),
            contrast_bias_stops=(
                contrast_bias_stops if contrast_bias_stops is not None
                else settings['contrast_bias_stops']
            ),
            highlight_trim_stops=(
                highlight_trim_stops if highlight_trim_stops is not None
                else settings['highlight_trim_stops']
            ),
            shadow_trim_stops=(
                shadow_trim_stops if shadow_trim_stops is not None
                else settings['shadow_trim_stops']
            ),
        )
    
    # ── Orchestration (uses stored state) ─────────────────────────────
    
    def get_contrast_analysis(self, paper_id=None, calibration=None,
                              highlight_trim_stops=None,
                              shadow_trim_stops=None,
                              overall_offset_stops=None,
                              contrast_bias_stops=None):
        """
        Get contrast analysis from stored highlight/shadow readings.

        Per-paper tunables (all stops, fall back to stored settings):
          - highlight_trim_stops / shadow_trim_stops: shift the lux readings
            before any computation (interpretive bias on what counts as
            "highlight" / "shadow").
          - contrast_bias_stops: shift the equivalent-grade lookup. Positive
            biases toward a HARDER grade (smaller effective ΔEV); negative
            toward softer.
          - overall_offset_stops: scale the suggested midpoint exposure time
            by 2^offset. Positive = darker print (longer time); negative
            = lighter (shorter).

        Returns:
            dict: ΔEV (measured + biased), recommended grade,
                  midpoint exposure times, legacy split-grade preview.
        """
        if self.highlight_lux is None or self.shadow_lux is None:
            return {
                'error': 'Missing highlight or shadow reading',
                'highlight_lux': self.highlight_lux,
                'shadow_lux': self.shadow_lux,
            }

        pid = paper_id or self.current_paper_id

        settings = self.get_split_settings(pid)
        h_trim = (
            highlight_trim_stops if highlight_trim_stops is not None
            else settings.get('contrast_highlight_trim_stops', 0.0)
        )
        s_trim = (
            shadow_trim_stops if shadow_trim_stops is not None
            else settings.get('contrast_shadow_trim_stops', 0.0)
        )
        overall = (
            overall_offset_stops if overall_offset_stops is not None
            else settings.get('ca_overall_offset_stops', 0.0)
        )
        bias = (
            contrast_bias_stops if contrast_bias_stops is not None
            else settings.get('ca_contrast_bias_stops', 0.0)
        )

        # Convention (matches split-grade soft/hard trim): positive trim
        # means MORE exposure for that zone. To increase exposure at the
        # metered point we divide its lux by 2**trim, so the resulting
        # K/lux suggested time grows.
        h_adj = self.highlight_lux * (2.0 ** -float(h_trim))
        s_adj = self.shadow_lux * (2.0 ** -float(s_trim))

        delta_ev = self.calculate_delta_ev(h_adj, s_adj)
        # Effective ΔEV for grade lookup: positive bias → harder grade
        # (paper sees a flatter negative). Measured delta_ev is unchanged.
        if delta_ev is None:
            delta_ev_effective = None
        else:
            delta_ev_effective = max(0.0, delta_ev - float(bias))
        recommended = self.recommend_filter_grade(
            delta_ev_effective, paper_id=pid,
        )
        # Legacy split-grade preview uses raw lux (not affected by Contrast
        # Analyzer trims, which only apply to the contrast analysis).
        split_grade = self.calculate_split_grade(
            self.highlight_lux, self.shadow_lux, paper_id=pid,
        )

        exposure_times = None
        if recommended:
            cal = calibration if calibration else self.get_calibration(pid)
            # Apply overall_offset by scaling the calibration constant; this
            # lets apply_reciprocity inside _calculate_midpoint_exposure_time
            # see the post-offset time and clamp/correct it correctly.
            effective_cal = cal * (2.0 ** float(overall))
            exposure_times = _calculate_midpoint_exposure_time(
                h_adj,
                s_adj,
                recommended,
                calibration=effective_cal,
                paper_id=pid,
            )

        recommended_response = None
        if recommended:
            recommended_response = {
                'grade': recommended.get('grade'),
                'match_quality': recommended.get('match_quality'),
                'reasoning': recommended.get('reasoning'),
                'out_of_range': recommended.get('out_of_range'),
            }

        return {
            'highlight_lux': self.highlight_lux,
            'shadow_lux': self.shadow_lux,
            'highlight_lux_adjusted': h_adj,
            'shadow_lux_adjusted': s_adj,
            'highlight_trim_stops': float(h_trim),
            'shadow_trim_stops': float(s_trim),
            'overall_offset_stops': float(overall),
            'contrast_bias_stops': float(bias),
            'delta_ev': delta_ev,
            'delta_ev_effective': delta_ev_effective,
            'recommended_grade': recommended_response,
            'split_grade': split_grade,
            'exposure_times': exposure_times,
        }

