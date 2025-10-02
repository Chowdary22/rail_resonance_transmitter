#!/usr/bin/env python3
"""
Example script demonstrating how to use both Sensor and Data layers
"""

import time
from peripherals.sensor_manager.manager import SensorManager
from data_handling.collector import DataCollector

def main():
    # 1. Create and initialize sensor
    sensor = SensorManager(sampling_rate=20)  # 20Hz sampling
    if not sensor.initialize():
        print("Failed to initialize sensor")
        return
        
    # 2. Create data collector
    collector = DataCollector(sensor, buffer_size=100)  # Buffer 100 samples
    
    # 3. Start collection
    if not collector.start_collection():
        print("Failed to start collection")
        return
        
    print("\nCollecting data...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get latest 5 readings
            readings = collector.get_latest_readings(count=5)
            
            # Print buffer status
            status = collector.get_buffer_status()
            print(f"\rBuffer: {status['buffer_size']}/100 samples "
                  f"{'[FULL]' if status['buffer_full'] else ''}", end="")
            
            # If there's an error, show it
            if status['has_error']:
                print("\nCollection error detected!")
                break
                
            time.sleep(0.1)  # Update display at 10Hz
            
    except KeyboardInterrupt:
        print("\n\nStopping collection...")
        
    finally:
        # 4. Clean shutdown
        collector.stop_collection()
        sensor.shutdown()
        
        # 5. Show final readings
        print("\nLast 5 readings:")
        readings = collector.get_latest_readings(count=5)
        for reading in readings:
            print(f"Time: {reading['timestamp']:.3f}, "
                  f"X: {reading['x']:6.2f}g, "
                  f"Y: {reading['y']:6.2f}g, "
                  f"Z: {reading['z']:6.2f}g")

if __name__ == "__main__":
    main()
