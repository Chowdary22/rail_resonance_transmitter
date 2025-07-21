# Data Sending block
# modules/lte_transmitter.py
import paho.mqtt.client as mqtt

class LTETransmitter:
    def __init__(self, broker, port, topic):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic = topic

    def start(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT connection error: {e}")

    def publish(self, message):
        try:
            self.client.publish(self.topic, message)
        except Exception as e:
            print(f"MQTT publish error: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
