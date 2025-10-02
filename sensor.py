"""
Consolidated Sensor service: initializes ADXL345 via I2C and collects readings
into a bounded buffer with a background thread.

Preserves: ADXL345 collection, I2C handling, buffering, status, and shutdown.
"""

import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional

from peripherals.adxl345_driver.driver import ADXL345Driver
from peripherals.adxl345_driver import constants as const


@dataclass
class SensorReading:
    timestamp: float
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict[str, float]:
        return {"timestamp": self.timestamp, "x": self.x, "y": self.y, "z": self.z}


class Sensor:
    def __init__(self, sampling_rate_hz: int = 20, buffer_size: int = 1000):
        self.driver = ADXL345Driver()
        self.sampling_rate_hz = sampling_rate_hz
        self._buffer = deque(maxlen=buffer_size)
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._configured_rate = self._map_rate(sampling_rate_hz)

    def _map_rate(self, rate: int) -> int:
        rate_map = {100: const.RATE_100HZ, 50: const.RATE_50HZ, 25: const.RATE_25HZ, 20: const.RATE_20HZ}
        return rate_map.get(rate, const.RATE_20HZ)

    def initialize(self) -> bool:
        ok = self.driver.initialize(range_setting=const.RANGE_16G, rate=self._configured_rate)
        if ok:
            print("✅ ADXL345 sensor initialized")
        else:
            print("❌ ADXL345 initialization failed")
        return ok

    def start_collection(self) -> bool:
        if self._running:
            return False
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def _loop(self) -> None:
        interval = 1.0 / float(self.sampling_rate_hz)
        while self._running:
            try:
                accel = self.driver.read_acceleration()
                if accel is not None:
                    x, y, z = accel
                    reading = SensorReading(timestamp=time.time(), x=x, y=y, z=z)
                    with self._lock:
                        self._buffer.append(reading)
            except Exception as e:
                print(f"❌ Sensor read error: {e}")
            time.sleep(interval)

    def get_latest_readings(self, count: int) -> List[Dict[str, float]]:
        try:
            with self._lock:
                if not self._buffer:
                    return []
                # Slice from the right (most recent)
                items = list(self._buffer)[-count:]
            return [r.to_dict() for r in items]
        except Exception as e:
            print(f"❌ Error accessing buffer: {e}")
            return []

    def get_status(self) -> Dict:
        with self._lock:
            size = len(self._buffer)
        return {"running": self._running, "sampling_rate_hz": self.sampling_rate_hz, "buffer_size": size}

    def shutdown(self) -> None:
        self._running = False
        try:
            if self._thread:
                self._thread.join(timeout=1.0)
        except Exception:
            pass



