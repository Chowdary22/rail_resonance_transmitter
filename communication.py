"""
Simplified serial ACK helper preserving retry behavior from config.
Adds configurable timeouts and minimal response normalization.
"""

import time
import serial

from config import COMMUNICATION


def send_ack(port: str, baudrate: int, message: bytes) -> bool:
    attempts = int(COMMUNICATION["serial"].get("retry_attempts", 3))
    delay = float(COMMUNICATION["serial"].get("retry_delay", 0.5))
    timeout = float(COMMUNICATION["serial"].get("timeout", 1.0))
    for attempt in range(1, attempts + 1):
        try:
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                ser.reset_input_buffer()
                ser.write(message)
                ser.flush()
                resp = ser.read(4)  # allow for trailing newline/CR
                resp = resp.strip().upper()
                if resp in (b"ACK", b"OK"):
                    return True
        except Exception as e:
            print(f"⚠️ Serial attempt {attempt} failed: {e}")
        time.sleep(delay)
    return False



