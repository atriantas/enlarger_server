"""
GPIO Relay Control for Pico 2 W
Controls 4 relays on GPIO pins 14-17 with active-LOW logic
"""

from machine import Pin
import json


class GPIOController:
    """Manages GPIO pins for relay control on Pico 2 W"""
    
    # GPIO Pin mapping (Pico 2 W)
    RELAY_PINS = {
        14: {"name": "Enlarger Timer", "state": False},
        15: {"name": "Safelight", "state": False},
        16: {"name": "Ventilation", "state": False},
        17: {"name": "White Light", "state": False}
    }
    
    def __init__(self):
        """Initialize GPIO controller with pin objects"""
        self.pins = {}
        self.relay_names = {}
        
    def initialize(self):
        """
        Initialize all GPIO pins as outputs
        All pins set to HIGH (OFF state for active-LOW relays)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for gpio_pin, info in self.RELAY_PINS.items():
                # Create pin object
                self.pins[gpio_pin] = Pin(gpio_pin, Pin.OUT)
                
                # Set to HIGH (OFF for active-LOW relay)
                self.pins[gpio_pin].value(1)
                
                # Store relay name for lookups
                self.relay_names[gpio_pin] = info["name"]
                
                print(f"✓ GPIO {gpio_pin} ({info['name']}) initialized as OUTPUT (OFF)")
                
            return True
            
        except Exception as e:
            print(f"❌ Error initializing GPIO: {e}")
            return False
            
    def set_relay_state(self, gpio_pin, state):
        """
        Set relay state (True=ON, False=OFF)
        
        Active-LOW relay logic:
        - state=True (ON)  → pin.value(0) [LOW]
        - state=False (OFF) → pin.value(1) [HIGH]
        
        Args:
            gpio_pin (int): GPIO pin number
            state (bool): True to turn relay ON, False to turn OFF
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if gpio_pin not in self.pins:
                print(f"❌ Invalid GPIO pin: {gpio_pin}")
                return False
                
            # Active-LOW: 0=ON, 1=OFF
            pin_value = 0 if state else 1
            self.pins[gpio_pin].value(pin_value)
            
            # Update internal state
            self.RELAY_PINS[gpio_pin]["state"] = state
            
            status = "ON" if state else "OFF"
            print(f"GPIO {gpio_pin} ({self.relay_names[gpio_pin]}): {status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting GPIO {gpio_pin}: {e}")
            return False
            
    def get_relay_state(self, gpio_pin):
        """
        Get current relay state
        
        Args:
            gpio_pin (int): GPIO pin number
            
        Returns:
            bool: Current state (True=ON, False=OFF), or None if error
        """
        try:
            if gpio_pin not in self.RELAY_PINS:
                return None
            return self.RELAY_PINS[gpio_pin]["state"]
        except Exception as e:
            print(f"❌ Error getting GPIO {gpio_pin} state: {e}")
            return None
            
    def get_all_states(self):
        """
        Get states of all relays
        
        Returns:
            dict: Dictionary mapping GPIO pins to their states
        """
        states = {}
        for gpio_pin, info in self.RELAY_PINS.items():
            states[str(gpio_pin)] = {
                "name": info["name"],
                "state": info["state"]
            }
        return states
        
    def cleanup(self):
        """
        Turn off all relays and cleanup GPIO
        Called on shutdown to ensure safe state
        """
        try:
            print("\nCleaning up GPIO...")
            
            # Turn off all relays (set to HIGH)
            for gpio_pin in self.pins:
                self.pins[gpio_pin].value(1)
                self.RELAY_PINS[gpio_pin]["state"] = False
                
            print("✓ All relays turned OFF")
            return True
            
        except Exception as e:
            print(f"❌ Error during GPIO cleanup: {e}")
            return False
            
    def get_relay_info(self, gpio_pin):
        """
        Get information about a specific relay
        
        Args:
            gpio_pin (int): GPIO pin number
            
        Returns:
            dict: Relay information or None if not found
        """
        if gpio_pin in self.RELAY_PINS:
            return {
                "gpio": gpio_pin,
                "name": self.RELAY_PINS[gpio_pin]["name"],
                "state": self.RELAY_PINS[gpio_pin]["state"]
            }
        return None
