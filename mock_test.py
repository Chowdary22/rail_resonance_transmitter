"""
Mock test to verify the clean architecture structure without dependencies
"""

import time
from datetime import datetime

# Mock implementations of our modules
class MockSensor:
    def __init__(self):
        self.is_running = False
    
    def initialize(self):
        print("✅ Mock sensor initialized")
        self.is_running = True
        return True
    
    def start_collection(self):
        print("✅ Mock data collection started")
        return True
    
    def get_latest_readings(self, count):
        # Return mock readings
        return [
            {"timestamp": time.time(), "x": 0.1, "y": 0.2, "z": 0.3},
            {"timestamp": time.time(), "x": 0.2, "y": 0.3, "z": 0.4},
        ]
    
    def get_status(self):
        return {"running": self.is_running, "buffer_size": 10}
    
    def shutdown(self):
        self.is_running = False


def process_batch(readings, sampling_rate_hz):
    print(f"✅ Processing {len(readings)} readings at {sampling_rate_hz}Hz")
    return {
        "mean_X": 0.15,
        "std_X": 0.05,
        "fft_X_max": 0.2,
        "timestamp_start": readings[0]["timestamp"],
        "timestamp_end": readings[-1]["timestamp"],
    }


def format_csv(features):
    print(f"✅ Formatting {len(features)} features")
    return "feature1,feature2\n0.1,0.2"


def send_ack(port, baudrate, message):
    print(f"✅ Sending ACK to {port} at {baudrate}")
    return True


class LTETransmitter:
    def __init__(self, broker, port, topic, max_buffer_size=100):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.connected = False
    
    def start(self):
        print(f"✅ LTE started with broker {self.broker}:{self.port}")
        self.connected = True
    
    def publish(self, payload):
        print(f"✅ Publishing {len(payload)} bytes to {self.topic}")
        return True
    
    def get_connection_status(self):
        return {
            "connected": self.connected,
            "broker": f"{self.broker}:{self.port}",
            "topic": self.topic,
            "buffer_size": 0,
        }
    
    def get_buffer_status(self):
        return {"buffer_size": 0, "max_buffer_size": 100}
    
    def stop(self):
        self.connected = False


# Mock config
HARDWARE = {"sensor": {"sampling_frequency": 20}}
COMMUNICATION = {"mqtt": {"broker": "test.broker", "port": 8883, "topic": "test/topic"}}
DATA_COLLECTION = {"buffer_size": 10}


def main():
    print(" Starting Rail Resonance Transmitter (MOCK TEST)...")
    print(f" Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize components
    sensor = MockSensor()
    sensor.initialize()
    sensor.start_collection()
    
    lte = LTETransmitter(
        COMMUNICATION["mqtt"]["broker"],
        COMMUNICATION["mqtt"]["port"],
        COMMUNICATION["mqtt"]["topic"],
    )
    lte.start()
    
    # Main loop - just do one iteration
    print("\n🔄 Running main loop (one iteration)...")
    readings = sensor.get_latest_readings(DATA_COLLECTION["buffer_size"])
    print(f"📊 Got {len(readings)} readings from sensor")
    
    features = process_batch(readings, HARDWARE["sensor"]["sampling_frequency"])
    print(f"🧮 Extracted {len(features)} features")
    
    payload = format_csv(features)
    
    if send_ack("COM1", 115200, b"FEATURES"):
        if lte.publish(payload):
            print("✅ Data sent successfully via LTE")
        else:
            print("⚠️ LTE transmission failed, data buffered")
    else:
        print("❌ Serial ACK failed. Skipping LTE transmission.")
    
    # Cleanup
    print("\n🛑 Shutting down gracefully...")
    lte.stop()
    sensor.shutdown()
    print("✅ System halted successfully.")


if __name__ == "__main__":
    main()

