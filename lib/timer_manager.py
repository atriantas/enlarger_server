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
    
    def __init__(self, gpio_control):
        """
        Initialize timer manager.
        
        Args:
            gpio_control: GPIOControl instance for relay control
        """
        self.gpio = gpio_control
        self.active_timers = {}  # pin -> task info
    
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
        
        # Store task reference for cancellation
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
        if pin not in self.active_timers:
            return False
        
        timer_info = self.active_timers[pin]
        
        # Cancel the task if it exists
        if "task" in timer_info:
            timer_info["task"].cancel()
        
        # Ensure relay is off
        self.gpio.set_relay_state(pin, False)
        
        # Remove from active timers
        if pin in self.active_timers:
            del self.active_timers[pin]
        
        print(f"Stopped timer for GPIO {pin}")
        return True
    
    def stop_all_timers(self):
        """Stop all active timers."""
        pins = list(self.active_timers.keys())
        for pin in pins:
            self.stop_timer(pin)
    
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
