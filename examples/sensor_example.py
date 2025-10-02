#!/usr/bin/env python3
"""
Example script demonstrating how to use the new Sensor Layer
"""

import time
from peripherals.sensor_manager.manager import SensorManager

def main():
    # Create sensor manager instance (default 20Hz sampling rate)
    sensor = SensorManager()
    
    # Initialize the sensor
    if not sensor.initialize():
        print("Failed to initialize sensor")
        return
    
    # Print sensor status
    status = sensor.get_status()
    print("\nSensor Status:")
    print("-------------")
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\nReading acceleration data...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Read acceleration data
            data = sensor.read_acceleration()
            
            if data:
                print(f"\rX: {data['x']:6.2f}g  "
                      f"Y: {data['y']:6.2f}g  "
                      f"Z: {data['z']:6.2f}g", end="")
            else:
                print("\rError reading sensor", end="")
                
            time.sleep(1/20)  # 20Hz refresh rate
            
    except KeyboardInterrupt:
        print("\n\nStopping sensor...")
        sensor.shutdown()

if __name__ == "__main__":
    main()
