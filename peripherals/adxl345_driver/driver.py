"""
ADXL345 Driver - Low-level I2C communication with ADXL345 accelerometer
"""

import smbus2
import time
from typing import Tuple, Optional
from . import constants as const

class ADXL345Driver:
    def __init__(self, bus_num: int = 1, address: int = const.ADXL345_ADDRESS):
        """Initialize ADXL345 driver with I2C bus number and device address"""
        self.bus = smbus2.SMBus(bus_num)
        self.address = address
        self.is_initialized = False
        
    def initialize(self, 
                  range_setting: int = const.RANGE_16G,
                  rate: int = const.RATE_20HZ) -> bool:
        """
        Initialize the ADXL345 sensor with specified settings
        
        Args:
            range_setting: Measurement range (2G, 4G, 8G, or 16G)
            rate: Data rate in Hz
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Verify device ID
            device_id = self.bus.read_byte_data(self.address, const.REG_DEVID)
            if device_id != 0xE5:  # Expected ADXL345 ID
                raise ValueError(const.ERR_DEVICE_NOT_FOUND)
            
            # Configure measurement range and resolution
            self.bus.write_byte_data(
                self.address,
                const.REG_DATA_FORMAT,
                const.FULL_RES_BIT | range_setting
            )
            
            # Set data rate
            self.bus.write_byte_data(self.address, const.REG_BW_RATE, rate)
            
            # Enable measurement mode
            self.bus.write_byte_data(
                self.address,
                const.REG_POWER_CTL,
                const.MEASURE_BIT
            )
            
            # Wait for sensor to stabilize
            time.sleep(0.1)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ ADXL345 initialization failed: {e}")
            self.is_initialized = False
            return False
    
    def read_raw_data(self) -> Optional[Tuple[int, int, int]]:
        """
        Read raw acceleration data from sensor
        
        Returns:
            Tuple[int, int, int]: Raw X, Y, Z values or None if read fails
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Sensor not initialized")
            
            # Read 6 bytes (2 bytes per axis)
            data = self.bus.read_i2c_block_data(self.address, const.REG_DATAX0, 6)
            
            # Convert to 16-bit values (little-endian)
            x = int.from_bytes(data[0:2], byteorder='little', signed=True)
            y = int.from_bytes(data[2:4], byteorder='little', signed=True)
            z = int.from_bytes(data[4:6], byteorder='little', signed=True)
            
            return (x, y, z)
            
        except Exception as e:
            print(f"❌ ADXL345 read failed: {e}")
            return None
    
    def read_acceleration(self) -> Optional[Tuple[float, float, float]]:
        """
        Read acceleration in g units
        
        Returns:
            Tuple[float, float, float]: X, Y, Z acceleration in g or None if read fails
        """
        raw_data = self.read_raw_data()
        if raw_data is None:
            return None
            
        x, y, z = raw_data
        
        # Convert to g using scale factor (assuming full resolution mode)
        scale_factor = const.SCALE_FACTOR_16G
        return (
            x / scale_factor,
            y / scale_factor,
            z / scale_factor
        )
    
    def self_test(self) -> bool:
        """
        Perform basic self-test
        
        Returns:
            bool: True if self-test passes
        """
        try:
            # Read device ID
            device_id = self.bus.read_byte_data(self.address, const.REG_DEVID)
            if device_id != 0xE5:
                return False
            
            # Try reading acceleration
            accel = self.read_acceleration()
            if accel is None:
                return False
            
            return True
            
        except Exception:
            return False