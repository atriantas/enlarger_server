"""
GPIO Control Module for Raspberry Pi Pico 2 W
Controls 4 relays on GPIO pins 14, 15, 16, 17
Active-LOW logic: Pin.value(0) = ON, Pin.value(1) = OFF
MicroPython v1.27.0 compatible
"""

from machine import Pin

# GPIO Pin Configuration for Pico 2 W
RELAY_PINS = {
    14: {"name": "Enlarger Timer", "state": False},
    15: {"name": "Safelight", "state": False},
    16: {"name": "Heating Element", "state": False},
    17: {"name": "White Light", "state": False}
}


class GPIOControl:
    """
    GPIO controller for relay management.
    
    Handles initialization, state control, and cleanup of relay pins.
    Uses active-LOW logic for relay modules.
    """
    
    def __init__(self):
        """Initialize GPIO pins as outputs with relays OFF."""
        self.pins = {}
        self.states = {}
        
        for pin_num in RELAY_PINS:
            # Initialize pin as output
            self.pins[pin_num] = Pin(pin_num, Pin.OUT)
            # Set to HIGH (OFF for active-low relays)
            self.pins[pin_num].value(1)
            self.states[pin_num] = False
            print(f"GPIO {pin_num} ({RELAY_PINS[pin_num]['name']}): initialized OFF")
        
        print("GPIO setup complete")
    
    def set_relay_state(self, pin, state):
        """
        Set relay state (True=ON, False=OFF).
        
        Args:
            pin (int): GPIO pin number (14, 15, 16, or 17)
            state (bool): True to turn ON, False to turn OFF
            
        Returns:
            bool: True if successful, False if invalid pin
        """
        if pin not in self.pins:
            print(f"Error: Invalid GPIO pin {pin}")
            return False
        
        # Active-LOW: 0 = ON, 1 = OFF
        pin_value = 0 if state else 1
        self.pins[pin].value(pin_value)
        self.states[pin] = state
        
        state_str = "ON" if state else "OFF"
        print(f"GPIO {pin} ({RELAY_PINS[pin]['name']}): {state_str}")
        return True
    
    def get_relay_state(self, pin):
        """
        Get current state of a relay.
        
        Args:
            pin (int): GPIO pin number
            
        Returns:
            bool or None: Current state, or None if invalid pin
        """
        if pin not in self.states:
            return None
        return self.states[pin]
    
    def get_all_states(self):
        """
        Get status of all relays.
        
        Returns:
            dict: Pin numbers mapped to state info
        """
        result = {}
        for pin in RELAY_PINS:
            result[pin] = {
                "name": RELAY_PINS[pin]["name"],
                "state": self.states.get(pin, False)
            }
        return result
    
    def all_on(self):
        """Turn all relays ON."""
        for pin in self.pins:
            self.set_relay_state(pin, True)
    
    def all_off(self):
        """Turn all relays OFF."""
        for pin in self.pins:
            self.set_relay_state(pin, False)
    
    def cleanup(self):
        """
        Cleanup GPIO on shutdown.
        Turns off all relays and resets pins.
        """
        print("Cleaning up GPIO...")
        for pin in self.pins:
            self.pins[pin].value(1)  # OFF
            self.states[pin] = False
        print("GPIO cleanup complete")
    
    def is_valid_pin(self, pin):
        """Check if pin number is valid."""
        return pin in RELAY_PINS
    
    def get_pin_name(self, pin):
        """Get the name associated with a pin."""
        if pin in RELAY_PINS:
            return RELAY_PINS[pin]["name"]
        return "Unknown"

