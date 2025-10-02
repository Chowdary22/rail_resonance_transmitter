"""
Sensor Manager - High-level management of ADXL345 sensor operations
"""

from typing import Dict, Optional, Tuple
from ..adxl345_driver.driver import ADXL345Driver
from ..adxl345_driver import constants as const

class SensorManager:
    def __init__(self, sampling_rate: int = 20):
        """
        Initialize sensor manager
        
        Args:
            sampling_rate: Desired sampling rate in Hz (default 20Hz)
        """
        self.driver = ADXL345Driver()
        self.sampling_rate = sampling_rate
        self.is_running = False
        self._configure_rate(sampling_rate)
        
    def _configure_rate(self, rate: int) -> None:
        """Convert Hz to ADXL345 rate setting"""
        rate_map = {
            100: const.RATE_100HZ,
            50: const.RATE_50HZ,
            25: const.RATE_25HZ,
            20: const.RATE_20HZ
        }
        self.rate_setting = rate_map.get(rate, const.RATE_20HZ)
        
    def initialize(self) -> bool:
        """
        Initialize the sensor with configured settings
        
        Returns:
            bool: True if initialization successful
        """
        success = self.driver.initialize(
            range_setting=const.RANGE_16G,
            rate=self.rate_setting
        )
        
        if success:
            print("✅ ADXL345 sensor initialized")
            self.is_running = True
        else:
            print("❌ ADXL345 initialization failed")
            self.is_running = False
            
        return success
    
    def read_acceleration(self) -> Optional[Dict[str, float]]:
        """
        Read acceleration data in a structured format
        
        Returns:
            Dict with keys 'x', 'y', 'z' containing acceleration values in g,
            or None if read fails
        """
        if not self.is_running:
            print("⚠️ Sensor not initialized")
            return None
            
        accel = self.driver.read_acceleration()
        if accel is None:
            return None
            
        x, y, z = accel
        return {
            "x": x,
            "y": y,
            "z": z
        }
    
    def read_raw(self) -> Optional[Tuple[int, int, int]]:
        """
        Read raw sensor data for debugging
        
        Returns:
            Tuple of raw X, Y, Z values or None if read fails
        """
        if not self.is_running:
            return None
        return self.driver.read_raw_data()
    
    def get_status(self) -> Dict[str, any]:
        """
        Get sensor status information
        
        Returns:
            Dict containing sensor status information
        """
        return {
            "initialized": self.is_running,
            "sampling_rate": self.sampling_rate,
            "range": "±16g",
            "resolution": "full"
        }
    
    def self_test(self) -> bool:
        """
        Perform sensor self-test
        
        Returns:
            bool: True if self-test passes
        """
        return self.driver.self_test()
    
    def shutdown(self) -> None:
        """Clean shutdown of sensor"""
        self.is_running = False
