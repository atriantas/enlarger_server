"""
Async Timer Manager for Raspberry Pi Pico 2 W
Non-blocking timer control using asyncio
Supports scheduled start via future timestamp for synchronized countdowns
MicroPython v1.27.0 compatible
"""

import asyncio
import time

# Fixed delay for network latency compensation (milliseconds)
SYNC_DELAY_MS = 150


class TimerManager:
    """
    Manages non-blocking relay timers using asyncio.
    
    Supports:
    - Immediate timer start
    - Scheduled timer start (synchronized with client)
    - Timer cancellation
    - Status tracking
    """
    
    def __init__(self, gpio_control, temperature_sensor=None):
        """
        Initialize timer manager.
        
        Args:
            gpio_control: GPIOControl instance for relay control
            temperature_sensor: Optional TemperatureSensor instance for heating control
        """
        self.gpio = gpio_control
        self.active_timers = {}  # pin -> task info
        self._task_refs = {}  # pin -> task object (never overwritten, used for cancellation)
        self.temperature_sensor = temperature_sensor
        self.heating_task = None
        self.target_temperature = 20.0  # Default target in Celsius
        self.heating_hysteresis = 0.5  # Dead zone in Celsius
        self.heating_pin = 16  # GP16 for heating element
        self.heating_enabled = False  # Temperature control disabled by default
        self.last_temperature = None  # Last read temperature
    
    def get_current_time_ms(self):
        """Get current time in milliseconds since boot."""
        return time.ticks_ms()
    
    def calculate_start_at(self):
        """
        Calculate scheduled start timestamp.
        Returns current time + fixed delay for synchronization.
        
        Returns:
            int: Timestamp in milliseconds when timer should start
        """
        return time.ticks_add(self.get_current_time_ms(), SYNC_DELAY_MS)
    
    async def _timer_task(self, pin, duration_sec, start_at_ms=None):
        """
        Internal timer task that runs asynchronously.
        
        Args:
            pin (int): GPIO pin to control
            duration_sec (float): Duration in seconds
            start_at_ms (int): Optional scheduled start timestamp
        """
        task_id = f"timer_{pin}"
        
        try:
            # Wait until scheduled start time if provided
            if start_at_ms is not None:
                now = self.get_current_time_ms()
                wait_ms = time.ticks_diff(start_at_ms, now)
                if wait_ms > 0:
                    await asyncio.sleep_ms(wait_ms)
            
            # Record start time
            self.active_timers[pin] = {
                "start_time": self.get_current_time_ms(),
                "duration_ms": int(duration_sec * 1000),
                "running": True
            }
            
            print(f"Timer started: GPIO {pin} for {duration_sec}s")
            
            # Turn relay ON
            self.gpio.set_relay_state(pin, True)
            
            # Wait for duration
            await asyncio.sleep(duration_sec)
            
            # Turn relay OFF
            self.gpio.set_relay_state(pin, False)
            
            print(f"Timer completed: GPIO {pin}")
            
        except asyncio.CancelledError:
            # Timer was cancelled
            self.gpio.set_relay_state(pin, False)
            print(f"Timer cancelled: GPIO {pin}")
            raise
        finally:
            # Cleanup timer info
            if pin in self.active_timers:
                del self.active_timers[pin]
            if pin in self._task_refs:
                current_task = None
                try:
                    current_task = asyncio.current_task()
                except AttributeError:
                    current_task = None
                if current_task is None or self._task_refs.get(pin) is current_task:
                    del self._task_refs[pin]
    
    def start_timer(self, pin, duration_sec, scheduled=True):
        """
        Start a timer for relay activation.
        
        Args:
            pin (int): GPIO pin to control
            duration_sec (float): Duration in seconds
            scheduled (bool): If True, use scheduled start for sync
            
        Returns:
            dict: Timer info including start_at timestamp
        """
        # Cancel any existing timer for this pin
        self.stop_timer(pin)
        
        # Calculate scheduled start time
        start_at_ms = self.calculate_start_at() if scheduled else None
        
        # Create and store the task
        task = asyncio.create_task(
            self._timer_task(pin, duration_sec, start_at_ms)
        )
        
        # Store task reference separately (never overwritten by _timer_task)
        # This ensures cancellation can always reach the running task
        self._task_refs[pin] = task
        
        # Store task reference for display/backward compatibility
        self.active_timers[pin] = {
            "task": task,
            "start_at": start_at_ms,
            "duration_ms": int(duration_sec * 1000),
            "running": False  # Will be True once task actually starts relay
        }
        
        return {
            "pin": pin,
            "duration": duration_sec,
            "start_at": start_at_ms,
            "sync_delay_ms": SYNC_DELAY_MS
        }
    
    def stop_timer(self, pin):
        """
        Stop any active timer for a pin.
        
        Args:
            pin (int): GPIO pin to stop timer for
            
        Returns:
            bool: True if timer was stopped, False if no timer found
        """
        if pin not in self.active_timers and pin not in self._task_refs:
            return False
        
        # Cancel task using the separate reference (most reliable)
        if pin in self._task_refs:
            self._task_refs[pin].cancel()
            del self._task_refs[pin]
        
        # Also try active_timers for backward compatibility
        if pin in self.active_timers:
            timer_info = self.active_timers[pin]
            if "task" in timer_info and timer_info["task"] not in (None,):
                try:
                    timer_info["task"].cancel()
                except:
                    pass
            del self.active_timers[pin]
        
        # Ensure relay is off
        self.gpio.set_relay_state(pin, False)
        
        print(f"Stopped timer for GPIO {pin}")
        return True
    
    def stop_all_timers(self):
        """Stop all active timers and heating control."""
        # Stop all relay timers (covers both _task_refs and active_timers)
        pins = list(self.active_timers.keys()) + list(self._task_refs.keys())
        for pin in set(pins):  # Use set to avoid duplicates
            self.stop_timer(pin)
        
        # Stop heating control
        if self.heating_task:
            self.heating_task.cancel()
            self.heating_task = None
    
    def get_timer_status(self, pin):
        """
        Get status of a specific timer.
        
        Args:
            pin (int): GPIO pin to check
            
        Returns:
            dict or None: Timer status or None if no active timer
        """
        if pin not in self.active_timers:
            return None
        
        info = self.active_timers[pin]
        
        if "start_time" in info and info.get("running"):
            # Timer is actively running
            elapsed_ms = time.ticks_diff(
                self.get_current_time_ms(),
                info["start_time"]
            )
            remaining_ms = max(0, info["duration_ms"] - elapsed_ms)
            
            return {
                "pin": pin,
                "running": True,
                "elapsed_ms": elapsed_ms,
                "remaining_ms": remaining_ms,
                "duration_ms": info["duration_ms"]
            }
        else:
            # Timer is scheduled but not yet started
            return {
                "pin": pin,
                "running": False,
                "scheduled": True,
                "start_at": info.get("start_at"),
                "duration_ms": info.get("duration_ms")
            }
    
    def get_all_timer_status(self):
        """
        Get status of all active timers.
        
        Returns:
            dict: Pin numbers mapped to timer status
        """
        result = {}
        for pin in self.active_timers:
            status = self.get_timer_status(pin)
            if status:
                result[pin] = status
        return result
    
    def get_active_count(self):
        """Get count of active timers."""
        return len(self.active_timers)
    
    async def start_heating_control(self):
        """
        Start background heating control task.
        
        Polls temperature sensor every 15 seconds ONLY when enabled.
        Controls relay using hysteresis: ON when temp < (target - hysteresis),
        OFF when temp >= target.
        When disabled, relay is OFF and no sensor reads occur.
        """
        if not self.temperature_sensor:
            print("WARNING: No temperature sensor configured, heating disabled")
            return
        
        print("Heating control task started (waits for enable command)...")
        
        try:
            while True:
                if not self.heating_enabled:
                    # Disabled - don't touch relay, allow manual control
                    # Just wait and check enable state periodically
                    await asyncio.sleep(1)  # Check enable state every 1s
                    continue
                
                # Enabled - read temperature (async, 750ms conversion + delay)
                temp = await self.temperature_sensor.read_temperature_async()
                self.last_temperature = temp
                
                if temp is None:
                    # Sensor read failed - ensure relay is OFF for safety
                    self.gpio.set_relay_state(self.heating_pin, False)
                    print("Heating: Sensor error - relay OFF (safety)")
                else:
                    # Apply hysteresis control
                    current_relay_state = self.gpio.get_relay_state(self.heating_pin)
                    
                    if temp < (self.target_temperature - self.heating_hysteresis):
                        # Turn relay ON (heating)
                        if not current_relay_state:
                            self.gpio.set_relay_state(self.heating_pin, True)
                            print(f"Heating: ON (temp={temp:.1f}°C < {self.target_temperature - self.heating_hysteresis:.1f}°C)")
                    elif temp >= self.target_temperature:
                        # Turn relay OFF (reached target)
                        if current_relay_state:
                            self.gpio.set_relay_state(self.heating_pin, False)
                            print(f"Heating: OFF (temp={temp:.1f}°C >= {self.target_temperature:.1f}°C)")
                
                # Wait 15 seconds before next poll
                await asyncio.sleep(15)
                
        except asyncio.CancelledError:
            # Heating control cancelled
            self.gpio.set_relay_state(self.heating_pin, False)
            print("Heating control stopped, relay OFF")
            raise
        except Exception as e:
            print(f"ERROR in heating control: {e}")
            self.gpio.set_relay_state(self.heating_pin, False)
    
    def set_target_temperature(self, target_celsius):
        """
        Set target temperature for heating control.
        
        Args:
            target_celsius (float): Target temperature in Celsius
        """
        self.target_temperature = target_celsius
        print(f"Target temperature set to {target_celsius}°C")
    
    def get_heating_status(self):
        """
        Get heating control status.
        
        Returns:
            dict: Heating status with temperature, target, relay state, and enabled flag
        """
        if not self.temperature_sensor:
            return {"error": "Temperature sensor not configured"}
        
        relay_state = self.gpio.get_relay_state(self.heating_pin)
        
        return {
            "temperature": self.last_temperature,
            "target": self.target_temperature,
            "relay_on": relay_state,
            "connected": self.temperature_sensor.is_connected() if self.heating_enabled else False,
            "enabled": self.heating_enabled
        }
    
    def set_heating_enabled(self, enabled):
        """
        Enable or disable temperature control.
        
        When disabled, sensor reading stops and relay turns OFF.
        
        Args:
            enabled (bool): True to enable, False to disable
        """
        self.heating_enabled = enabled
        if not enabled:
            # Immediately turn off relay when disabled
            self.gpio.set_relay_state(self.heating_pin, False)
            self.last_temperature = None
        print(f"Temperature control {'enabled' if enabled else 'disabled'}")
    
    def is_heating_enabled(self):
        """Check if heating control is enabled."""
        return self.heating_enabled

