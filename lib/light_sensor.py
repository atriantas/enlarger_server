"""
TSL2591X High Dynamic Range Light Sensor Driver for MicroPython
Raspberry Pi Pico 2 W - Darkroom Light Meter

I2C Interface on GP0 (SDA) / GP1 (SCL)
Supports auto-gain, dynamic integration time, and noise filtering.
"""

from machine import I2C, Pin
import asyncio
import time

# TSL2591X I2C Address
TSL2591_ADDR = 0x29

# Command Register
TSL2591_COMMAND_BIT = 0xA0  # Command bit for register access
TSL2591_NORMAL_OP = 0x20    # Normal operation

# Register Addresses
TSL2591_ENABLE_REG = 0x00
TSL2591_CONFIG_REG = 0x01
TSL2591_ID_REG = 0x12
TSL2591_STATUS_REG = 0x13
TSL2591_C0DATAL_REG = 0x14  # CH0 low byte
TSL2591_C0DATAH_REG = 0x15  # CH0 high byte
TSL2591_C1DATAL_REG = 0x16  # CH1 low byte
TSL2591_C1DATAH_REG = 0x17  # CH1 high byte

# Enable Register Values
TSL2591_ENABLE_POWERON = 0x01
TSL2591_ENABLE_POWEROFF = 0x00
TSL2591_ENABLE_AEN = 0x02   # ALS Enable
TSL2591_ENABLE_AIEN = 0x10  # ALS Interrupt Enable
TSL2591_ENABLE_NPIEN = 0x80 # No Persist Interrupt Enable

# Gain Settings (CONFIG register bits 4-5)
TSL2591_GAIN_LOW = 0x00    # 1x gain
TSL2591_GAIN_MED = 0x10    # 25x gain (medium)
TSL2591_GAIN_HIGH = 0x20   # 428x gain (high)
TSL2591_GAIN_MAX = 0x30    # 9876x gain (maximum)

# Gain multipliers for lux calculation
GAIN_FACTORS = {
    TSL2591_GAIN_LOW: 1.0,
    TSL2591_GAIN_MED: 25.0,
    TSL2591_GAIN_HIGH: 428.0,
    TSL2591_GAIN_MAX: 9876.0
}

GAIN_NAMES = {
    TSL2591_GAIN_LOW: "1x",
    TSL2591_GAIN_MED: "25x",
    TSL2591_GAIN_HIGH: "428x",
    TSL2591_GAIN_MAX: "9876x"
}

# Integration Time Settings (CONFIG register bits 0-2)
TSL2591_INTEGRATIONTIME_100MS = 0x00  # 100ms
TSL2591_INTEGRATIONTIME_200MS = 0x01  # 200ms
TSL2591_INTEGRATIONTIME_300MS = 0x02  # 300ms
TSL2591_INTEGRATIONTIME_400MS = 0x03  # 400ms
TSL2591_INTEGRATIONTIME_500MS = 0x04  # 500ms
TSL2591_INTEGRATIONTIME_600MS = 0x05  # 600ms

# Integration time in milliseconds
INTEGRATION_TIMES = {
    TSL2591_INTEGRATIONTIME_100MS: 100,
    TSL2591_INTEGRATIONTIME_200MS: 200,
    TSL2591_INTEGRATIONTIME_300MS: 300,
    TSL2591_INTEGRATIONTIME_400MS: 400,
    TSL2591_INTEGRATIONTIME_500MS: 500,
    TSL2591_INTEGRATIONTIME_600MS: 600
}

# Auto-gain thresholds (raw counts)
AUTO_GAIN_LOW_THRESHOLD = 100       # Switch to higher gain below this
AUTO_GAIN_HIGH_THRESHOLD = 36000    # Switch to lower gain above this (near saturation)
AUTO_GAIN_HYSTERESIS = 5000         # Hysteresis to prevent hunting (increased from 500)
AUTO_GAIN_STABILITY_SAMPLES = 3     # Require N consecutive out-of-range readings before switching


class LightSensor:
    """
    TSL2591X High Dynamic Range Light Sensor Driver
    
    Features:
    - Auto-gain switching with hysteresis
    - Dynamic integration time (100ms for bright, 600ms for low-light)
    - Median + moving average filtering for noise reduction
    - IR subtraction for actinic light approximation
    - Async read support for non-blocking operation
    """
    
    DEFAULT_SDA = 0
    DEFAULT_SCL = 1
    
    # Filter settings
    MEDIAN_WINDOW = 5      # Samples for median filter
    MOVING_AVG_WINDOW = 10 # Samples for moving average
    
    # Response modes
    RESPONSE_MODE_STABLE = 0      # Full filtering (slow but smooth)
    RESPONSE_MODE_BALANCED = 1    # Medium filtering (default)
    RESPONSE_MODE_FAST = 2        # Minimal filtering (fast but noisier)
    
    def __init__(self, sda_pin=DEFAULT_SDA, scl_pin=DEFAULT_SCL, freq=400000):
        """
        Initialize the TSL2591X sensor.
        
        Args:
            sda_pin: GPIO pin for I2C SDA (default: GP0)
            scl_pin: GPIO pin for I2C SCL (default: GP1)
            freq: I2C bus frequency (default: 400kHz)
        """
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.freq = freq
        
        # Sensor state
        self.i2c = None
        self.is_connected = False
        self.last_error = None
        
        # Current settings
        self.gain = TSL2591_GAIN_MED
        self.integration_time = TSL2591_INTEGRATIONTIME_100MS
        self.auto_gain_enabled = False  # DISABLED by default for stable meter readings
        self.response_mode = self.RESPONSE_MODE_BALANCED  # Default: balanced speed/noise
        
        # Gain stability tracking (prevent oscillation)
        self._out_of_range_count = 0
        self._last_valid_ch0 = None
        
        # Last readings
        self.last_lux = None
        self.last_ev = None
        self.last_ch0 = None
        self.last_ch1 = None
        self.last_read_time = None
        
        # Filter buffers
        self._median_buffer = []
        self._moving_avg_buffer = []
        
        # Initialize hardware
        self._init_hardware()
    
    def _init_hardware(self):
        """Initialize I2C bus and sensor."""
        try:
            self.i2c = I2C(0, sda=Pin(self.sda_pin), scl=Pin(self.scl_pin), freq=self.freq)
            
            # Scan for device
            devices = self.i2c.scan()
            if TSL2591_ADDR not in devices:
                self.is_connected = False
                self.last_error = f"TSL2591X not found at 0x{TSL2591_ADDR:02X}. Found: {[hex(d) for d in devices]}"
                print(f"⚠️ Light Sensor: {self.last_error}")
                return
            
            # Verify device ID
            device_id = self._read_register(TSL2591_ID_REG)
            if device_id != 0x50:  # TSL2591 ID
                self.is_connected = False
                self.last_error = f"Invalid device ID: 0x{device_id:02X} (expected 0x50)"
                print(f"⚠️ Light Sensor: {self.last_error}")
                return
            
            # Power on and enable ALS
            self._enable()
            
            # Set initial gain and integration time
            self._set_config(self.gain, self.integration_time)
            
            self.is_connected = True
            self.last_error = None
            print(f"✅ Light Sensor: TSL2591X initialized on GP{self.sda_pin}/GP{self.scl_pin}")
            
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            print(f"❌ Light Sensor init failed: {e}")
    
    def _write_register(self, reg, value):
        """Write a byte to a register."""
        cmd = TSL2591_COMMAND_BIT | TSL2591_NORMAL_OP | reg
        self.i2c.writeto(TSL2591_ADDR, bytes([cmd, value]))
    
    def _read_register(self, reg):
        """Read a byte from a register."""
        cmd = TSL2591_COMMAND_BIT | TSL2591_NORMAL_OP | reg
        self.i2c.writeto(TSL2591_ADDR, bytes([cmd]))
        return self.i2c.readfrom(TSL2591_ADDR, 1)[0]
    
    def _read_word(self, reg):
        """Read a 16-bit word from two consecutive registers."""
        cmd = TSL2591_COMMAND_BIT | TSL2591_NORMAL_OP | reg
        self.i2c.writeto(TSL2591_ADDR, bytes([cmd]))
        data = self.i2c.readfrom(TSL2591_ADDR, 2)
        return data[0] | (data[1] << 8)
    
    def _enable(self):
        """Power on the sensor and enable ALS."""
        self._write_register(TSL2591_ENABLE_REG, 
                            TSL2591_ENABLE_POWERON | TSL2591_ENABLE_AEN)
    
    def _disable(self):
        """Power off the sensor."""
        self._write_register(TSL2591_ENABLE_REG, TSL2591_ENABLE_POWEROFF)
    
    def _set_config(self, gain, integration_time):
        """Set gain and integration time."""
        self.gain = gain
        self.integration_time = integration_time
        config = gain | integration_time
        self._write_register(TSL2591_CONFIG_REG, config)
    
    def set_gain(self, gain):
        """
        Manually set the gain.
        
        Args:
            gain: One of TSL2591_GAIN_LOW, _MED, _HIGH, _MAX
        """
        self._set_config(gain, self.integration_time)
        self.auto_gain_enabled = False
    
    def set_integration_time(self, integration_time):
        """
        Set the integration time.
        
        Args:
            integration_time: One of TSL2591_INTEGRATIONTIME_100MS to _600MS
        """
        self._set_config(self.gain, integration_time)
    
    def enable_auto_gain(self, enabled=True):
        """Enable or disable automatic gain adjustment."""
        self.auto_gain_enabled = enabled
    
    def _read_raw_channels(self):
        """
        Read raw channel data from sensor.
        
        Returns:
            tuple: (ch0_raw, ch1_raw) - CH0 is visible+IR, CH1 is IR only
        """
        ch0 = self._read_word(TSL2591_C0DATAL_REG)
        ch1 = self._read_word(TSL2591_C1DATAL_REG)
        return ch0, ch1
    
    def _calculate_lux(self, ch0, ch1):
        """
        Calculate lux from raw channel values.
        
        Uses the TSL2591 lux equation with IR subtraction for
        better approximation of visible (actinic) light.
        
        Args:
            ch0: Raw CH0 value (visible + IR)
            ch1: Raw CH1 value (IR only)
            
        Returns:
            float: Calculated lux value
        """
        if ch0 == 0:
            return 0.0
        
        # Get timing and gain factors
        atime = INTEGRATION_TIMES[self.integration_time]
        again = GAIN_FACTORS[self.gain]
        
        # Calculate counts per lux (CPL)
        # CPL = (ATIME * AGAIN) / DF
        # DF (Device Factor) = 408 for TSL2591
        cpl = (atime * again) / 408.0
        
        if cpl == 0:
            return 0.0
        
        # Calculate lux using the standard formula with IR correction
        # Lux = (C0DATA - C1DATA) * (1 - (C1DATA / C0DATA)) / CPL
        # Simplified: Lux = (C0 - 2*C1) / CPL for typical conditions
        
        # More accurate formula from datasheet
        lux1 = (ch0 - (1.87 * ch1)) / cpl
        lux2 = ((0.63 * ch0) - ch1) / cpl
        
        # Use the higher of the two calculations (handles different light sources)
        lux = max(lux1, lux2, 0.0)
        
        return lux
    
    def _calculate_ev(self, lux):
        """
        Calculate Exposure Value (EV) from lux.
        
        EV = log2(lux / 2.5) for ISO 100
        
        Args:
            lux: Light level in lux
            
        Returns:
            float: EV value (can be negative for very low light)
        """
        if lux <= 0:
            return -10.0  # Very dark
        
        import math
        # EV = log2(lux / 2.5) at ISO 100
        ev = math.log2(lux / 2.5)
        return ev
    
    def _auto_adjust_gain(self, ch0):
        """
        Automatically adjust gain based on reading with hysteresis and stability checking.
        
        This method prevents rapid gain oscillation by:
        1. Requiring readings to be outside the threshold+hysteresis range
        2. Counting consecutive out-of-range readings before switching
        3. Only switching after N consecutive readings confirm the change
        
        Args:
            ch0: Raw CH0 value
            
        Returns:
            bool: True if gain was changed
        """
        if not self.auto_gain_enabled:
            return False
        
        current_gain = self.gain
        new_gain = current_gain
        
        # Define hysteresis ranges for each gain level
        # For low gain, check upper threshold + hysteresis for switching to med gain
        # For med gain, check both thresholds with hysteresis
        # For high gain, check lower threshold + hysteresis for switching to med gain
        # For max gain, check lower threshold + hysteresis for switching to high gain
        
        high_threshold_with_hyst = AUTO_GAIN_HIGH_THRESHOLD + AUTO_GAIN_HYSTERESIS
        low_threshold_with_hyst = AUTO_GAIN_LOW_THRESHOLD - AUTO_GAIN_HYSTERESIS
        
        out_of_range = False
        
        # Check if we need to decrease gain (too bright)
        if ch0 > high_threshold_with_hyst:
            out_of_range = True
            if current_gain == TSL2591_GAIN_MAX:
                new_gain = TSL2591_GAIN_HIGH
            elif current_gain == TSL2591_GAIN_HIGH:
                new_gain = TSL2591_GAIN_MED
            elif current_gain == TSL2591_GAIN_MED:
                new_gain = TSL2591_GAIN_LOW
        
        # Check if we need to increase gain (too dark)
        elif ch0 < low_threshold_with_hyst:
            out_of_range = True
            if current_gain == TSL2591_GAIN_LOW:
                new_gain = TSL2591_GAIN_MED
            elif current_gain == TSL2591_GAIN_MED:
                new_gain = TSL2591_GAIN_HIGH
            elif current_gain == TSL2591_GAIN_HIGH:
                new_gain = TSL2591_GAIN_MAX
        
        # Stability checking: only switch after N consecutive out-of-range readings
        if out_of_range and new_gain != current_gain:
            self._out_of_range_count += 1
            
            if self._out_of_range_count >= AUTO_GAIN_STABILITY_SAMPLES:
                # Confirmed: switch gain
                self._set_config(new_gain, self.integration_time)
                self._out_of_range_count = 0  # Reset counter
                return True
        else:
            # Back in range, reset counter
            self._out_of_range_count = 0
        
        return False
    
    def _apply_median_filter(self, value):
        """
        Apply median filter to reduce impulsive noise.
        
        Args:
            value: New lux value
            
        Returns:
            float: Median-filtered value
        """
        self._median_buffer.append(value)
        if len(self._median_buffer) > self.MEDIAN_WINDOW:
            self._median_buffer.pop(0)
        
        if len(self._median_buffer) < 3:
            return value
        
        sorted_values = sorted(self._median_buffer)
        mid = len(sorted_values) // 2
        return sorted_values[mid]
    
    def _apply_moving_average(self, value):
        """
        Apply moving average filter for smoothing.
        
        Args:
            value: Median-filtered lux value
            
        Returns:
            float: Smoothed value
        """
        self._moving_avg_buffer.append(value)
        if len(self._moving_avg_buffer) > self.MOVING_AVG_WINDOW:
            self._moving_avg_buffer.pop(0)
        
        return sum(self._moving_avg_buffer) / len(self._moving_avg_buffer)
    
    def read_lux_sync(self):
        """
        Synchronous lux reading (blocking).
        
        Returns:
            dict: Reading data or error
        """
        if not self.is_connected:
            return {
                "status": "error",
                "error": self.last_error or "Sensor not connected"
            }
        
        try:
            # Read raw channels
            ch0, ch1 = self._read_raw_channels()
            
            # Auto-adjust gain if needed
            gain_changed = self._auto_adjust_gain(ch0)
            if gain_changed:
                # Wait for new integration and re-read (shorter wait in fast mode)
                wait_time = INTEGRATION_TIMES[self.integration_time] + 50
                if self.response_mode == self.RESPONSE_MODE_FAST:
                    wait_time = min(wait_time, 100)  # Cap at 100ms
                time.sleep_ms(wait_time)
                ch0, ch1 = self._read_raw_channels()
            
            # Calculate raw lux first
            raw_lux = self._calculate_lux(ch0, ch1)
            
            # Apply filtering based on response mode
            if self.response_mode == self.RESPONSE_MODE_STABLE:
                # Full filtering: median + moving average (slowest, smoothest)
                median_lux = self._apply_median_filter(raw_lux)
                filtered_lux = self._apply_moving_average(median_lux)
            elif self.response_mode == self.RESPONSE_MODE_FAST:
                # Minimal filtering: just raw lux (fastest, may be noisier)
                filtered_lux = raw_lux
            else:  # RESPONSE_MODE_BALANCED (default)
                # Medium filtering: only moving average (good balance)
                filtered_lux = self._apply_moving_average(raw_lux)
            
            # Calculate EV
            ev = self._calculate_ev(filtered_lux)
            
            # Store last values
            self.last_lux = filtered_lux
            self.last_ev = ev
            self.last_ch0 = ch0
            self.last_ch1 = ch1
            self.last_read_time = time.ticks_ms()
            
            return {
                "status": "success",
                "lux": round(filtered_lux, 2),
                "lux_raw": round(raw_lux, 2),
                "ev": round(ev, 2),
                "ch0_raw": ch0,
                "ch1_raw": ch1,
                "gain": GAIN_NAMES[self.gain],
                "integration_ms": INTEGRATION_TIMES[self.integration_time],
                "timestamp": self.last_read_time,
                "response_mode": ["stable", "balanced", "fast"][self.response_mode]
            }
            
        except Exception as e:
            self.last_error = str(e)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def read_lux_async(self):
        """
        Asynchronous lux reading (non-blocking).
        
        Waits for integration time before reading.
        
        Returns:
            dict: Reading data or error
        """
        if not self.is_connected:
            return {
                "status": "error",
                "error": self.last_error or "Sensor not connected"
            }
        
        try:
            # Wait for integration to complete
            await asyncio.sleep_ms(INTEGRATION_TIMES[self.integration_time] + 10)
            
            # Read raw channels
            ch0, ch1 = self._read_raw_channels()
            
            # Auto-adjust gain if needed
            gain_changed = self._auto_adjust_gain(ch0)
            if gain_changed:
                # Wait for new integration and re-read
                await asyncio.sleep_ms(INTEGRATION_TIMES[self.integration_time] + 50)
                ch0, ch1 = self._read_raw_channels()
            
            # Calculate lux
            raw_lux = self._calculate_lux(ch0, ch1)
            
            # Apply filters
            median_lux = self._apply_median_filter(raw_lux)
            filtered_lux = self._apply_moving_average(median_lux)
            
            # Calculate EV
            ev = self._calculate_ev(filtered_lux)
            
            # Store last values
            self.last_lux = filtered_lux
            self.last_ev = ev
            self.last_ch0 = ch0
            self.last_ch1 = ch1
            self.last_read_time = time.ticks_ms()
            
            return {
                "status": "success",
                "lux": round(filtered_lux, 2),
                "lux_raw": round(raw_lux, 2),
                "ev": round(ev, 2),
                "ch0_raw": ch0,
                "ch1_raw": ch1,
                "gain": GAIN_NAMES[self.gain],
                "integration_ms": INTEGRATION_TIMES[self.integration_time],
                "timestamp": self.last_read_time
            }
            
        except Exception as e:
            self.last_error = str(e)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_last_reading(self):
        """
        Get the last cached reading without triggering a new read.
        
        Returns:
            dict: Last reading data
        """
        return {
            "lux": self.last_lux,
            "ev": self.last_ev,
            "ch0_raw": self.last_ch0,
            "ch1_raw": self.last_ch1,
            "gain": GAIN_NAMES.get(self.gain, "unknown"),
            "integration_ms": INTEGRATION_TIMES.get(self.integration_time, 0),
            "timestamp": self.last_read_time,
            "is_connected": self.is_connected
        }
    
    def get_status(self):
        """
        Get sensor status information.
        
        Returns:
            dict: Status information
        """
        return {
            "is_connected": self.is_connected,
            "error": self.last_error,
            "gain": GAIN_NAMES.get(self.gain, "unknown"),
            "auto_gain": self.auto_gain_enabled,
            "integration_ms": INTEGRATION_TIMES.get(self.integration_time, 0),
            "last_lux": self.last_lux,
            "last_ev": self.last_ev,
            "sda_pin": self.sda_pin,
            "scl_pin": self.scl_pin
        }
    
    def set_low_light_mode(self):
        """
        Configure sensor for low-light metering (darkroom).
        Sets maximum gain and longest integration time.
        """
        self._set_config(TSL2591_GAIN_MAX, TSL2591_INTEGRATIONTIME_600MS)
        self.auto_gain_enabled = True
        print("📷 Light Sensor: Low-light mode enabled (9876x gain, 600ms integration)")
    
    def set_bright_mode(self):
        """
        Configure sensor for bright conditions (focusing).
        Sets low gain and short integration time.
        """
        self._set_config(TSL2591_GAIN_LOW, TSL2591_INTEGRATIONTIME_100MS)
        self.auto_gain_enabled = True
        print("☀️ Light Sensor: Bright mode enabled (1x gain, 100ms integration)")
    
    def set_manual_gain(self, gain_level):
        """
        Set manual gain level and disable auto-gain.
        
        Args:
            gain_level: One of TSL2591_GAIN_LOW, TSL2591_GAIN_MED, TSL2591_GAIN_HIGH, TSL2591_GAIN_MAX
            
        Returns:
            bool: True if gain was set successfully
        """
        if gain_level not in GAIN_FACTORS:
            return False
        
        self._set_config(gain_level, self.integration_time)
        self.auto_gain_enabled = False  # Disable auto-gain for manual mode
        self._out_of_range_count = 0  # Reset stability counter
        print(f"🔧 Light Sensor: Manual gain set to {GAIN_NAMES[gain_level]}, auto-gain DISABLED")
        return True
    
    def enable_auto_gain(self):
        """Enable auto-gain with enhanced stability."""
        self.auto_gain_enabled = True
        self._out_of_range_count = 0  # Reset stability counter
        print("⚙️ Light Sensor: Auto-gain ENABLED with enhanced stability")
    
    def disable_auto_gain(self):
        """Disable auto-gain for stable manual readings."""
        self.auto_gain_enabled = False
        self._out_of_range_count = 0  # Reset stability counter
        print("⚙️ Light Sensor: Auto-gain DISABLED for stable readings")
    
    def set_response_mode(self, mode):
        """
        Set sensor response mode for speed vs noise tradeoff.
        
        Args:
            mode: One of RESPONSE_MODE_STABLE, RESPONSE_MODE_BALANCED, RESPONSE_MODE_FAST
                  - STABLE (0): Full median + moving average filtering (slowest, smoothest)
                  - BALANCED (1): Only moving average (default, good balance)
                  - FAST (2): Raw readings (fastest, may be noisier)
                  
        Returns:
            bool: True if mode was set
        """
        if mode not in (self.RESPONSE_MODE_STABLE, self.RESPONSE_MODE_BALANCED, self.RESPONSE_MODE_FAST):
            return False
        
        self.response_mode = mode
        mode_names = ["STABLE", "BALANCED", "FAST"]
        print(f"⚡ Light Sensor: Response mode set to {mode_names[mode]}")
        return True
    
    def clear_filters(self):
        """Clear filter buffers for fresh readings."""
        self._median_buffer.clear()
        self._moving_avg_buffer.clear()
