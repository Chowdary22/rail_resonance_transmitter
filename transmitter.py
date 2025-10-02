"""
Transport Layer: LTETransmitter

Manages MQTT over LTE with simple buffering when offline.
"""

import threading
import time
from queue import Queue
from typing import Dict

import paho.mqtt.client as mqtt

from config import COMMUNICATION


class LTETransmitter:
    def __init__(self, broker: str, port: int, topic: str, max_buffer_size: int = 1000):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.max_buffer_size = max_buffer_size
        self._client = mqtt.Client(client_id=COMMUNICATION["mqtt"]["client_id"])
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._connected = False
        self._buffer: Queue = Queue(maxsize=max_buffer_size)
        self._thread: threading.Thread | None = None
        self._stop = False

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = (rc == 0)
        if self._connected:
            print("✅ MQTT connected")
        else:
            print(f"❌ MQTT connect failed rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        print("⚠️ MQTT disconnected")

    def start(self) -> None:
        try:
            self._client.tls_set() if self.port == 8883 else None
            self._client.connect_async(self.broker, self.port, keepalive=COMMUNICATION["mqtt"]["keepalive"])
            self._client.loop_start()
            self._stop = False
            self._thread = threading.Thread(target=self._drain_buffer_loop, daemon=True)
            self._thread.start()
        except Exception as e:
            print(f"❌ LTE start error: {e}")

    def stop(self) -> None:
        self._stop = True
        try:
            if self._thread:
                self._thread.join(timeout=1.0)
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:
            pass

    def _drain_buffer_loop(self) -> None:
        retry_interval = COMMUNICATION["mqtt"]["connection_retry_interval"]
        while not self._stop:
            try:
                if self._connected and not self._buffer.empty():
                    payload = self._buffer.get_nowait()
                    self._publish_now(payload)
                else:
                    time.sleep(retry_interval)
            except Exception as e:
                print(f"⚠️ Buffer drain error: {e}")
                time.sleep(retry_interval)

    def _publish_now(self, payload: str) -> bool:
        try:
            result = self._client.publish(self.topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
        except Exception as e:
            print(f"❌ Publish error: {e}")
        return False

    def publish(self, payload: str) -> bool:
        if self._connected:
            if self._publish_now(payload):
                return True
        # Buffer when not connected or publish fails
        if self._buffer.full():
            try:
                self._buffer.get_nowait()
            except Exception:
                pass
        try:
            self._buffer.put_nowait(payload)
        except Exception:
            return False
        return False

    def get_connection_status(self) -> Dict:
        return {
            "connected": self._connected,
            "broker": f"{self.broker}:{self.port}",
            "topic": self.topic,
            "buffer_size": self._buffer.qsize()
        }

    def get_buffer_status(self) -> Dict:
        return {
            "buffer_size": self._buffer.qsize(),
            "max_buffer_size": self.max_buffer_size
        }



