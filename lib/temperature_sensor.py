"""
Temperature Sensor Driver for DS1820 Digital Temperature Sensor
Raspberry Pi Pico 2 W - MicroPython v1.27.0

Communicates with DS1820 via 1-Wire protocol on GP18.
Asynchronously reads temperature and caches latest value.
"""

import asyncio
import machine
import onewire
import ds18x20
import time


class TemperatureSensor:
    """
    DS1820 temperature sensor interface using 1-Wire protocol.
    
    Attributes:
        pin_num: GPIO pin number (default: 18)
        last_temp: Last successfully read temperature in Celsius
        last_error: Last error message (None if OK)
        rom_addresses: List of device ROM addresses found on bus
    """
    
    # Configuration
    CONVERSION_TIME_MS = 750  # DS1820 conversion time (750ms for 12-bit)
    DEFAULT_PIN = 18
    
    def __init__(self, pin_num=DEFAULT_PIN):
        """
        Initialize DS1820 sensor on specified pin.
        
        Args:
            pin_num: GPIO pin number (default: 18)
        """
        self.pin_num = pin_num
        self.last_temp = None
        self.last_error = None
        self.rom_addresses = []
        
        try:
            # Setup 1-Wire bus
            self.data_pin = machine.Pin(pin_num)
            self.one_wire = onewire.OneWire(self.data_pin)
            self.ds_sensor = ds18x20.DS18X20(self.one_wire)
            
            # Scan for devices
            self.rom_addresses = self.ds_sensor.scan()
            
            if not self.rom_addresses:
                self.last_error = "No DS1820 devices found on bus"
                print(f"WARNING: {self.last_error}")
            else:
                print(f"✓ DS1820 initialized on GP{pin_num}")
                print(f"  Found {len(self.rom_addresses)} device(s)")
                
        except Exception as e:
            self.last_error = str(e)
            print(f"ERROR: Failed to initialize DS1820: {e}")
    
    async def read_temperature_async(self):
        """
        Asynchronously read temperature from first sensor on bus.
        
        Returns:
            float: Temperature in Celsius, or None if sensor read fails
        """
        try:
            if not self.rom_addresses:
                self.last_error = "No DS1820 devices found"
                return None
            
            # Start conversion on all devices
            self.ds_sensor.convert_temp()
            
            # Wait for conversion to complete (non-blocking with asyncio)
            await asyncio.sleep_ms(self.CONVERSION_TIME_MS)
            
            # Read temperature from first device
            rom = self.rom_addresses[0]
            temp = self.ds_sensor.read_temp(rom)
            
            self.last_temp = temp
            self.last_error = None
            return temp
            
        except Exception as e:
            self.last_error = str(e)
            print(f"WARNING: Failed to read DS1820: {e}")
            return None
    
    def get_last_temperature(self):
        """
        Get last successfully read temperature without blocking.
        
        Returns:
            float: Temperature in Celsius, or None if never read successfully
        """
        return self.last_temp
    
    def is_connected(self):
        """
        Check if sensor is connected.
        
        Returns:
            bool: True if devices found on bus, False otherwise
        """
        return len(self.rom_addresses) > 0
    
    def get_status(self):
        """
        Get sensor status information.
        
        Returns:
            dict: Status information with temperature, error, and device count
        """
        return {
            "temperature": self.last_temp,
            "is_connected": self.is_connected(),
            "device_count": len(self.rom_addresses),
            "error": self.last_error,
            "pin": self.pin_num
        }

