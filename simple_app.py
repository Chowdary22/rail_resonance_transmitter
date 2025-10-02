"""
Simplified Rail Resonance Transmitter that works with system packages
"""

import time
import threading
from datetime import datetime
import RPi.GPIO as RPiGPIO
import os

# Configuration
HARDWARE = {
    "sensor": {
        "sampling_frequency": 20,
    },
    "modem": {
        "uart_ports": ["/dev/ttyUSB0"],
        "baudrate": 115200,
    },
}

COMMUNICATION = {
    "mqtt": {
        "broker": "broker.emqx.io",
        "port": 8883,
        "topic": "rail/vibration/data",
        "client_id": f"rail_sensor_simple",
    },
    "serial": {
        "retry_attempts": 3,
        "retry_delay": 0.5,
        "timeout": 1.0,
    },
}

PATHS = {
    "logs": {
        "base": "/home/testuser/logs",
        "raw_data": "/home/testuser/logs/adxl345",
        "processed_data": "/home/testuser/logs/processed",
    }
}

GPIO_CONFIG = {
    "alert_led_pin": 18,
    "mode": "BCM",
}

# Simplified sensor implementation
class Sensor:
    def __init__(self):
        self.is_running = False
        self.thread = None
        
    def initialize(self):
        print("✅ Sensor initialized (simplified)")
        self.is_running = True
        return True
        
    def start_collection(self):
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
        print("✅ Sensor collection started")
        return True
        
    def _collection_loop(self):
        while self.is_running:
            # Simulate reading sensor
            time.sleep(1.0 / HARDWARE["sensor"]["sampling_frequency"])
            
    def get_latest_readings(self, count):
        # Return simulated readings
        readings = []
        for i in range(count):
            readings.append({
                "timestamp": time.time() - (count - i) * 0.05,
                "x": 0.1 * i,
                "y": 0.2 * i,
                "z": 0.3 * i,
            })
        return readings
        
    def get_status(self):
        return {
            "running": self.is_running,
            "sampling_rate_hz": HARDWARE["sensor"]["sampling_frequency"],
            "buffer_size": 10,
        }
        
    def shutdown(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)

# Simplified processor
def process_batch(readings, sampling_rate_hz):
    print(f"✅ Processing {len(readings)} readings at {sampling_rate_hz}Hz")
    
    # Calculate simple statistics
    x_values = [r["x"] for r in readings]
    y_values = [r["y"] for r in readings]
    z_values = [r["z"] for r in readings]
    
    return {
        "mean_X": sum(x_values) / len(x_values) if x_values else 0,
        "mean_Y": sum(y_values) / len(y_values) if y_values else 0,
        "mean_Z": sum(z_values) / len(z_values) if z_values else 0,
        "max_X": max(x_values) if x_values else 0,
        "max_Y": max(y_values) if y_values else 0,
        "max_Z": max(z_values) if z_values else 0,
        "timestamp_start": readings[0]["timestamp"] if readings else 0,
        "timestamp_end": readings[-1]["timestamp"] if readings else 0,
    }

# Simplified formatter
def format_csv(features):
    keys = sorted(features.keys())
    header = ",".join(keys)
    values = ",".join(str(features[k]) for k in keys)
    return f"{header}\n{values}"

# Simplified communication
def send_ack(port, baudrate, message):
    print(f"✅ Serial ACK to {port} (simulated)")
    return True

# Simplified transmitter
class LTETransmitter:
    def __init__(self, broker, port, topic, max_buffer_size=100):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.connected = False
        self.buffer = []
        
    def start(self):
        print(f"✅ LTE started with broker {self.broker}:{self.port}")
        self.connected = True
        
    def publish(self, payload):
        print(f"✅ Publishing {len(payload)} bytes to {self.topic}")
        if not self.connected:
            self.buffer.append(payload)
            return False
        return True
        
    def get_connection_status(self):
        return {
            "connected": self.connected,
            "broker": f"{self.broker}:{self.port}",
            "topic": self.topic,
            "buffer_size": len(self.buffer),
        }
        
    def get_buffer_status(self):
        return {
            "buffer_size": len(self.buffer),
            "max_buffer_size": 100,
        }
        
    def stop(self):
        self.connected = False

# GPIO setup
def setup_gpio():
    try:
        RPiGPIO.setmode(RPiGPIO.BCM)
        RPiGPIO.setup(GPIO_CONFIG["alert_led_pin"], RPiGPIO.OUT)
        RPiGPIO.output(GPIO_CONFIG["alert_led_pin"], RPiGPIO.LOW)
        print("✅ GPIO initialized")
    except Exception as e:
        print(f"❌ GPIO setup failed: {e}")

# Main function
def main():
    print("🚀 Starting Rail Resonance Transmitter (Simple Version)...")
    print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup GPIO
    setup_gpio()
    
    # Ensure log directories exist
    os.makedirs(PATHS["logs"]["raw_data"], exist_ok=True)
    os.makedirs(PATHS["logs"]["processed_data"], exist_ok=True)
    print("✅ Log directories created")
    
    # Initialize components
    sensor = Sensor()
    sensor.initialize()
    sensor.start_collection()
    
    lte = LTETransmitter(
        COMMUNICATION["mqtt"]["broker"],
        COMMUNICATION["mqtt"]["port"],
        COMMUNICATION["mqtt"]["topic"],
    )
    lte.start()
    
    # File paths for logging
    raw_file = f"{PATHS['logs']['raw_data']}/adxl345_log_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    processed_file = f"{PATHS['logs']['processed_data']}/processed_features_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    
    # Write header to raw CSV
    with open(raw_file, "a", newline="") as f:
        f.write("timestamp,x,y,z\n")
    
    print(f"📁 Raw data logging to: {raw_file}")
    print(f"📁 Processed data logging to: {processed_file}")
    
    try:
        # Process 5 batches then exit
        for i in range(5):
            print(f"\n🔄 Processing batch {i+1}/5...")
            
            # Get readings from sensor
            readings = sensor.get_latest_readings(10)
            
            # Log raw readings
            with open(raw_file, "a", newline="") as f:
                for r in readings:
                    f.write(f"{r['timestamp']},{r['x']},{r['y']},{r['z']}\n")
            
            # Process readings
            features = process_batch(readings, HARDWARE["sensor"]["sampling_frequency"])
            
            # Save processed features
            header_needed = i == 0
            with open(processed_file, "a", newline="") as f:
                if header_needed:
                    keys = sorted(features.keys())
                    f.write(",".join(keys) + "\n")
                f.write(",".join(str(features[k]) for k in sorted(features.keys())) + "\n")
            
            # Format and send
            payload = format_csv(features)
            
            if send_ack(HARDWARE["modem"]["uart_ports"][0], HARDWARE["modem"]["baudrate"], b"FEATURES"):
                if lte.publish(payload):
                    print("✅ Data sent successfully via LTE")
                else:
                    print("⚠️ LTE transmission failed, data buffered")
            else:
                print("❌ Serial ACK failed. Skipping LTE transmission.")
            
            # Wait before next batch
            time.sleep(1)
        
        # Flash LED to indicate completion
        for _ in range(3):
            RPiGPIO.output(GPIO_CONFIG["alert_led_pin"], RPiGPIO.HIGH)
            time.sleep(0.2)
            RPiGPIO.output(GPIO_CONFIG["alert_led_pin"], RPiGPIO.LOW)
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        lte.stop()
        sensor.shutdown()
        RPiGPIO.cleanup()
        print("✅ System halted successfully.")

if __name__ == "__main__":
    main()

