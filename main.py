# Rail Resonance Transmitter for vibration monitoring using Raspberry Pi 4, ADXL345, and Quectel EC25-E

import time
import threading
import csv
import os
from datetime import datetime
import RPi.GPIO as RPiGPIO

# Import configuration
from config import (
    HARDWARE, DATA_COLLECTION, COMMUNICATION, PATHS, GPIO as GPIO_CONFIG, SYSTEM, 
    validate_config, get_config_summary
)

# Import modular components
from sensor import Sensor
from processor import process_batch, format_csv
from communication import send_ack
from transmitter import LTETransmitter

# === Global Variables ===
data_lock = threading.Lock()

# === GPIO Setup ===
def setup_gpio():
    """Initialize GPIO pins"""
    try:
        RPiGPIO.setmode(RPiGPIO.BCM)
        RPiGPIO.setup(GPIO_CONFIG["alert_led_pin"], RPiGPIO.OUT)
        RPiGPIO.output(GPIO_CONFIG["alert_led_pin"], RPiGPIO.LOW)
        print("✅ GPIO initialized")
    except Exception as e:
        print(f"❌ GPIO setup failed: {e}")

# === System Health Monitoring ===
def monitor_system_health(sensor: Sensor, lte: LTETransmitter):
    """Monitor system health and display status"""
    while True:
        try:
            print("\n" + "="*50)
            print("🏥 SYSTEM HEALTH STATUS")
            print("="*50)
            
            # Sensor status
            s = sensor.get_status() if sensor else {"running": False, "buffer_size": 0}
            print(f"📊 Sensor: {'✅ Running' if s.get('running') else '❌ Stopped'} | Buffer: {s.get('buffer_size', 0)}")
            
            # LTE status
            lte_status = lte.get_connection_status()
            print(f"📡 LTE: {'✅ Connected' if lte_status['connected'] else '❌ Disconnected'}")
            print(f"   Broker: {lte_status['broker']}")
            print(f"   Topic: {lte_status['topic']}")
            print(f"   Buffer: {lte_status['buffer_size']} messages")
            
            # Buffer status
            buffer_status = lte.get_buffer_status()
            print(f"💾 Offline Buffer: {buffer_status['buffer_size']}/{buffer_status['max_buffer_size']}")
            
            print("="*50)
            
        except Exception as e:
            print(f"❌ Health monitoring error: {e}")
        
        time.sleep(SYSTEM["health_monitoring_interval"])

# === Main Function ===
def main():
    print(" Starting Rail Resonance Transmitter...")
    print(f" Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate configuration
    config_errors = validate_config()
    if config_errors:
        print("❌ Configuration validation failed:")
        for error in config_errors:
            print(f"   - {error}")
        return
    
    # Display configuration summary
    config_summary = get_config_summary()
    print("\n📋 Configuration Summary:")
    for category, settings in config_summary.items():
        print(f"   {category.upper()}:")
        for key, value in settings.items():
            print(f"     {key}: {value}")
    
    setup_gpio()

    # Ensure directories exist
    os.makedirs(PATHS["logs"]["raw_data"], exist_ok=True)
    os.makedirs(PATHS["logs"]["processed_data"], exist_ok=True)
    print("✅ Log directories created")

    # Initialize components
    try:
        sampling_rate = HARDWARE["sensor"]["sampling_frequency"]
        sensor = Sensor(sampling_rate_hz=int(sampling_rate), buffer_size=DATA_COLLECTION["max_offline_buffer"])
        if not sensor.initialize():
            return
        sensor.start_collection()
        print("✅ Sensor collection started")
    except Exception as e:
        print(f"❌ Sensor initialization failed: {e}")
        return
    
    lte = LTETransmitter(
        COMMUNICATION["mqtt"]["broker"],
        COMMUNICATION["mqtt"]["port"],
        COMMUNICATION["mqtt"]["topic"],
        max_buffer_size=DATA_COLLECTION["max_offline_buffer"]
    )
    
    # Start LTE transmitter
    lte.start()
    
    # Start health monitoring
    health_thread = threading.Thread(target=monitor_system_health, args=(sensor, lte), daemon=True)
    health_thread.start()
    print("✅ Health monitoring started")
    
    print("🚀 System is running. Press Ctrl+C to exit.\n")

    # File paths for logging
    raw_file = f"{PATHS['logs']['raw_data']}/adxl345_log_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    processed_file = f"{PATHS['logs']['processed_data']}/processed_features_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"

    try:
        # Write header to raw CSV
        with open(raw_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "x", "y", "z"])

        print(f"📁 Raw data logging to: {raw_file}")
        print(f"📁 Processed data logging to: {processed_file}")

        while True:
            # Fetch latest readings from sensor buffer
            readings = sensor.get_latest_readings(count=DATA_COLLECTION["buffer_size"])

            # Append raw readings to CSV
            if readings:
                with open(raw_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    for r in readings:
                        # r keys: timestamp, x, y, z (in g)
                        writer.writerow([r["timestamp"], r["x"], r["y"], r["z"]])

            # Process in batches when enough samples are available
            if len(readings) >= DATA_COLLECTION["buffer_size"]:
                try:
                    features = process_batch(readings, sampling_rate_hz=float(HARDWARE["sensor"]["sampling_frequency"]))

                    # Save processed features to CSV
                    if features:
                        # Write header if file is new/empty
                        header_needed = not os.path.exists(processed_file) or os.path.getsize(processed_file) == 0
                        keys_sorted = sorted(features.keys())
                        with open(processed_file, "a", newline="") as pf:
                            writer = csv.writer(pf)
                            if header_needed:
                                writer.writerow(keys_sorted)
                            writer.writerow([features[k] for k in keys_sorted])

                        # Format and attempt to send
                        payload = format_csv(features)
                        # Use AT probe so modem responds with OK, which we accept as ACK-equivalent
                        msg = b"AT\r"
                        if send_ack(HARDWARE["modem"]["uart_ports"][0], HARDWARE["modem"]["baudrate"], msg):
                            if lte.publish(payload):
                                print("✅ Data sent successfully via LTE")
                            else:
                                print("⚠️ LTE transmission failed, data buffered")
                        else:
                            print("❌ Serial ACK failed. Skipping LTE transmission.")

                except Exception as e:
                    print(f"❌ Data processing error: {e}")

            time.sleep(DATA_COLLECTION["mqtt_send_freq"])

    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        lte.stop()
        try:
            sensor.shutdown()
        except Exception:
            pass
        RPiGPIO.cleanup()
        print("✅ System halted successfully.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        lte.stop()
        try:
            sensor.shutdown()
        except Exception:
            pass
        RPiGPIO.cleanup()
        raise

if __name__ == "__main__":
    main()