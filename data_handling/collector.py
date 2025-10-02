"""
Data Collector - Manages sensor data collection and buffering
"""

import time
import threading
from typing import Dict, List, Optional
from queue import Queue
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SensorReading:
    """Structure for a single sensor reading"""
    timestamp: float
    x: float
    y: float
    z: float
    
    def to_dict(self) -> Dict:
        """Convert reading to dictionary format"""
        return {
            "timestamp": self.timestamp,
            "x": self.x,
            "y": self.y,
            "z": self.z
        }

class DataCollector:
    def __init__(self, sensor_manager, buffer_size: int = 1000):
        """
        Initialize data collector
        
        Args:
            sensor_manager: Instance of SensorManager
            buffer_size: Maximum number of readings to buffer
        """
        self.sensor = sensor_manager
        self.buffer: Queue = Queue(maxsize=buffer_size)
        self.collection_thread: Optional[threading.Thread] = None
        self.is_collecting = False
        self.collection_error = False
        
    def start_collection(self) -> bool:
        """
        Start data collection in a separate thread
        
        Returns:
            bool: True if collection started successfully
        """
        if self.is_collecting:
            print("⚠️ Collection already running")
            return False
            
        if not self.sensor.is_running:
            print("⚠️ Sensor not initialized")
            return False
            
        self.is_collecting = True
        self.collection_error = False
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self.collection_thread.start()
        return True
    
    def stop_collection(self) -> None:
        """Stop data collection"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=1.0)
            self.collection_thread = None
    
    def _collection_loop(self) -> None:
        """Main data collection loop"""
        while self.is_collecting:
            try:
                # Read sensor data
                data = self.sensor.read_acceleration()
                if data is None:
                    self.collection_error = True
                    continue
                
                # Create reading with timestamp
                reading = SensorReading(
                    timestamp=time.time(),
                    x=data['x'],
                    y=data['y'],
                    z=data['z']
                )
                
                # Add to buffer, removing oldest if full
                if self.buffer.full():
                    self.buffer.get_nowait()  # Remove oldest
                self.buffer.put_nowait(reading)
                
                # Sleep for next sample
                time.sleep(1.0 / self.sensor.sampling_rate)
                
            except Exception as e:
                print(f"❌ Collection error: {e}")
                self.collection_error = True
    
    def get_buffer_status(self) -> Dict:
        """Get buffer status information"""
        return {
            "is_collecting": self.is_collecting,
            "buffer_size": self.buffer.qsize(),
            "buffer_full": self.buffer.full(),
            "has_error": self.collection_error
        }
    
    def get_latest_readings(self, count: int = 1) -> List[Dict]:
        """
        Get the most recent readings
        
        Args:
            count: Number of readings to return
            
        Returns:
            List of readings as dictionaries
        """
        readings = []
        try:
            # Convert queue to list temporarily
            temp_list = []
            while not self.buffer.empty() and len(temp_list) < count:
                temp_list.append(self.buffer.get())
            
            # Put readings back in queue
            for reading in temp_list:
                self.buffer.put(reading)
                readings.append(reading.to_dict())
                
        except Exception as e:
            print(f"❌ Error getting readings: {e}")
            
        return readings
    
    def clear_buffer(self) -> None:
        """Clear all readings from buffer"""
        while not self.buffer.empty():
            self.buffer.get()
