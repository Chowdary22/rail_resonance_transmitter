# Rail Resonance Transmitter for vibration monitoring using Raspberry Pi 4, ADXL345, and RAK2013

import time
import threading
import csv
import os
from datetime import datetime
import RPi.GPIO as GPIO

# Import modular components
from peripherals.i2c_device import I2CDevice
from modules.feature_extractor import FeatureExtractor
from modules.data_formatter import DataFormatter
from modules.communication_manager import SerialACKManager
from modules.lte_transmitter import LTETransmitter

# === Configuration ===
ALERT_LED_PIN = 18
SENSOR_FREQ = 0.05  # 20Hz
MQTT_SEND_FREQ = 1  # 1-second upload
SD_CARD_FILE = "/home/logs/adxl345"
sensor_data = {"x_axis": 0.0, "y_axis": 0.0, "z_axis": 0.0, "timestamp": 0.0}
data_lock = threading.Lock()

# === Sensor Thread ===
def sensor_task(sensor: I2CDevice, buffer: dict):
    while True:
        x, y, z = sensor.read_data()
        with data_lock:
            buffer.update({
                "x_axis": x * 9.81,  # Convert g to m/s^2
                "y_axis": y * 9.81,
                "z_axis": z * 9.81,
                "timestamp": time.time()
            })
        time.sleep(SENSOR_FREQ)

# === GPIO Setup ===
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ALERT_LED_PIN, GPIO.OUT)
    GPIO.output(ALERT_LED_PIN, GPIO.LOW)
    print("GPIO initialized")

# === Main Function ===
def main():
    print("Starting Rail Resonance Transmitter...")
    setup_gpio()

    sensor = I2CDevice(1, 0x53)
    extractor = FeatureExtractor()
    formatter = DataFormatter()
    serial_com = SerialACKManager()
    lte = LTETransmitter("test.mosquitto.org", 1883, "rail/vibration/data")
    lte.start()

    # Start sensor polling in a thread
    threading.Thread(target=sensor_task, args=(sensor, sensor_data), daemon=True).start()
    print("System is running. Press Ctrl+C to exit.\n")

    try:
        while True:
            with data_lock:
                raw = sensor_data.copy()

            # 1. Preprocess
            processed = extractor.convert_to_g(raw)

            # 2. Save processed data to SD card (CSV file)
            file_exists = os.path.isfile(SD_CARD_FILE)
            with open(SD_CARD_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "x_axis", "y_axis", "z_axis"])
                writer.writerow([
                    processed["timestamp"],
                    processed["x_axis"],
                    processed["y_axis"],
                    processed["z_axis"]
                ])

            # 3. Package and send the preprocessed data to AI
            payload = formatter.format_csv_string(processed)

            if serial_com.send_ack(processed):
                lte.publish(payload) # Send data to the AI via MQTT or HTTP
                print(f"Sent: {payload}")
            else:
                print("Serial ACK failed. Skipping MQTT.")

            time.sleep(MQTT_SEND_FREQ)

    except KeyboardInterrupt:
        print("Shutting down...")
        lte.stop()
        serial_com.close()
        GPIO.cleanup()
        print("System halted.")

if __name__ == "__main__":
    main()
