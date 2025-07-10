# main.py
from thread_handler import start_thread, stop_all_threads
from i2c_device import I2CDevice
from uart_device import UARTDevice
from storage import DataStorage
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO

# Initialize variables
sensor_data = {"x_axis": 0.0, "y_axis": 0.0, "z_axis": 0.0}
mqtt_broker = "test.mosquitto.org"
mqtt_topic = "rail/vibration/data"
alert_topic = "rail/vibration/alert"
ALERT_LED_PIN = 18  # GPIO pin for LED (adjust as needed)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code", rc)
    client.subscribe(alert_topic)  # Subscribe to alert topic

def on_message(client, userdata, msg):
    # Handle alerts from predictive maintenance software
    message = msg.payload.decode()
    print("Received alert:", message)
    if "abnormal" in message.lower():
        GPIO.output(ALERT_LED_PIN, GPIO.HIGH)  # Turn on LED
    else:
        GPIO.output(ALERT_LED_PIN, GPIO.LOW)  # Turn off LED

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ALERT_LED_PIN, GPIO.OUT)
    GPIO.output(ALERT_LED_PIN, GPIO.LOW)

def read_vibration(i2c_sensor, data, storage):
    while True:
        try:
            data["x_axis"], data["y_axis"], data["z_axis"] = i2c_sensor.read_data()
            print(f"Vibration: X={data['x_axis']:.2f}g, Y={data['y_axis']:.2f}g, Z={data['z_axis']:.2f}g")
            # Save to microSD
            storage.save_data(data["x_axis"], data["y_axis"], data["z_axis"])
            time.sleep(1)  # Sample every 1 second
        except Exception as e:
            print("Sensor error:", e)
            time.sleep(1)

def send_to_mqtt(client, data):
    while True:
        try:
            message = f"{data['x_axis']:.2f},{data['y_axis']:.2f},{data['z_axis']:.2f}"
            client.publish(mqtt_topic, message)
            print("Sent to MQTT:", message)
            time.sleep(5)  # Send every 5 seconds
        except Exception as e:
            print("MQTT error:", e)
            time.sleep(5)

if __name__ == "__main__":
    # Set up peripherals
    i2c = I2CDevice(bus=1, address=0x53)  # ADXL345 sensor
    uart = UARTDevice(port="/dev/ttyS0", baudrate=9600)  # RAK2013 modem
    storage = DataStorage()

    # Set up MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(mqtt_broker, 1883, 60)
        client.loop_start()  # Start MQTT loop in background
    except Exception as e:
        print("Failed to connect to MQTT broker:", e)

    # Set up GPIO for LED
    setup_gpio()

    # Start threads
    start_thread("sensor_thread", read_vibration, (i2c, sensor_data, storage))
    start_thread("mqtt_thread", send_to_mqtt, (client, sensor_data))

    try:
        while True:
            time.sleep(10)  # Keep program running
    except KeyboardInterrupt:
        print("Stopping program...")
        client.loop_stop()
        client.disconnect()
        stop_all_threads()
        GPIO.cleanup()
        print("Program stopped.")