"""
Timer Management for Pico 2 W
Handles timed relay activation using asyncio for non-blocking operation
"""

import asyncio
import time as utime


class TimerManager:
    """Manages timed relay activations using asyncio"""
    
    def __init__(self, gpio_controller):
        """
        Initialize timer manager
        
        Args:
            gpio_controller: GPIOController instance for relay control
        """
        self.gpio = gpio_controller
        self.active_timers = {}  # Track active timers: {gpio: {start_time, duration, running}}
        self.tasks = {}  # Track asyncio tasks: {gpio: task}
        
    async def start_timer(self, gpio_pin, duration):
        """
        Start a timed relay activation
        
        Turns relay ON immediately, waits for duration, then turns relay OFF.
        Cancels any existing timer for the pin first.
        
        Args:
            gpio_pin (int): GPIO pin number
            duration (float): Duration in seconds
            
        Returns:
            bool: True if timer started successfully
        """
        try:
            # Cancel existing timer for this pin
            await self.stop_timer(gpio_pin)
            
            # Create timer record
            self.active_timers[gpio_pin] = {
                'start_time': utime.time(),
                'duration': duration,
                'running': True
            }
            
            print(f"Timer started: GPIO {gpio_pin} for {duration}s")
            
            # Turn relay ON immediately
            self.gpio.set_relay_state(gpio_pin, True)
            
            # Wait for duration (non-blocking with asyncio)
            await asyncio.sleep(duration)
            
            # Turn relay OFF
            if self.active_timers.get(gpio_pin, {}).get('running'):
                self.gpio.set_relay_state(gpio_pin, False)
                print(f"Timer completed: GPIO {gpio_pin}")
            
            # Mark timer as complete
            if gpio_pin in self.active_timers:
                self.active_timers[gpio_pin]['running'] = False
                
            return True
            
        except asyncio.CancelledError:
            print(f"Timer cancelled for GPIO {gpio_pin}")
            # Ensure relay is OFF
            self.gpio.set_relay_state(gpio_pin, False)
            return False
            
        except Exception as e:
            print(f"Timer error on GPIO {gpio_pin}: {e}")
            # Ensure relay is OFF on error
            self.gpio.set_relay_state(gpio_pin, False)
            return False
            
        finally:
            # Clean up timer record
            if gpio_pin in self.active_timers:
                del self.active_timers[gpio_pin]
            if gpio_pin in self.tasks:
                del self.tasks[gpio_pin]
                
    async def stop_timer(self, gpio_pin):
        """
        Stop any active timer for a pin
        
        Turns off the relay immediately and cancels the timer task.
        
        Args:
            gpio_pin (int): GPIO pin number
            
        Returns:
            bool: True if timer was stopped, False if no timer was active
        """
        try:
            # Cancel task if exists
            if gpio_pin in self.tasks:
                task = self.tasks[gpio_pin]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self.tasks[gpio_pin]
                
            # Turn off relay immediately
            self.gpio.set_relay_state(gpio_pin, False)
            
            # Remove from active timers
            if gpio_pin in self.active_timers:
                del self.active_timers[gpio_pin]
                print(f"Timer stopped for GPIO {gpio_pin}")
                return True
                
            return False
            
        except Exception as e:
            print(f"Error stopping timer for GPIO {gpio_pin}: {e}")
            return False
            
    def create_timer_task(self, gpio_pin, duration):
        """
        Create and register a timer task
        
        Use this to create asyncio tasks that are tracked by the manager.
        
        Args:
            gpio_pin (int): GPIO pin number
            duration (float): Duration in seconds
            
        Returns:
            asyncio.Task: The created task
        """
        # Cancel existing task for this pin
        if gpio_pin in self.tasks:
            task = self.tasks[gpio_pin]
            if not task.done():
                task.cancel()
                
        # Create new task
        task = asyncio.create_task(self.start_timer(gpio_pin, duration))
        self.tasks[gpio_pin] = task
        
        return task
        
    def is_timer_active(self, gpio_pin):
        """
        Check if a timer is currently active
        
        Args:
            gpio_pin (int): GPIO pin number
            
        Returns:
            bool: True if timer is running, False otherwise
        """
        if gpio_pin in self.active_timers:
            return self.active_timers[gpio_pin].get('running', False)
        return False
        
    def get_timer_elapsed(self, gpio_pin):
        """
        Get elapsed time for an active timer
        
        Args:
            gpio_pin (int): GPIO pin number
            
        Returns:
            float: Elapsed time in seconds, or None if no timer
        """
        if gpio_pin in self.active_timers:
            timer = self.active_timers[gpio_pin]
            if timer.get('running'):
                elapsed = utime.time() - timer['start_time']
                return elapsed
        return None
        
    def get_timer_remaining(self, gpio_pin):
        """
        Get remaining time for an active timer
        
        Args:
            gpio_pin (int): GPIO pin number
            
        Returns:
            float: Remaining time in seconds, or None if no timer
        """
        if gpio_pin in self.active_timers:
            timer = self.active_timers[gpio_pin]
            if timer.get('running'):
                elapsed = utime.time() - timer['start_time']
                remaining = timer['duration'] - elapsed
                return max(0, remaining)
        return None
        
    def get_active_timers(self):
        """
        Get list of all active timers
        
        Returns:
            dict: Dictionary of active timers with GPIO as key
        """
        active = {}
        for gpio_pin, timer in self.active_timers.items():
            if timer.get('running'):
                elapsed = utime.time() - timer['start_time']
                remaining = timer['duration'] - elapsed
                active[gpio_pin] = {
                    'duration': timer['duration'],
                    'elapsed': elapsed,
                    'remaining': max(0, remaining)
                }
        return active
        
    async def cleanup(self):
        """
        Cleanup all timers on shutdown
        Cancels all tasks and turns off all relays
        """
        try:
            print("\nCleaning up timers...")
            
            # Cancel all tasks
            for gpio_pin, task in list(self.tasks.items()):
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                        
            # Turn off all relays
            for gpio_pin in self.active_timers:
                self.gpio.set_relay_state(gpio_pin, False)
                
            # Clear records
            self.active_timers.clear()
            self.tasks.clear()
            
            print("✓ Timers cleaned up")
            
        except Exception as e:
            print(f"Error during timer cleanup: {e}")
