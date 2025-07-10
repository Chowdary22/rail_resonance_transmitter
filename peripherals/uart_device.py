# uart_device.py
import serial
import time

class UARTDevice:
    def __init__(self, port, baudrate):
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            time.sleep(1)  # Wait for serial connection to stabilize
            print("UART initialized on", port)
            self._configure_rak2013()
        except Exception as e:
            print("Error initializing UART:", e)

    def _configure_rak2013(self):
        try:
            # Send AT commands to initialize RAK2013 (example commands)
            self.serial.write(b"AT\r\n")
            time.sleep(0.5)
            response = self.serial.read_all().decode()
            if "OK" in response:
                print("RAK2013 responded successfully")
            else:
                print("RAK2013 initialization failed")
        except Exception as e:
            print("Error configuring RAK2013:", e)

    def write(self, message):
        try:
            self.serial.write(message.encode() + b"\r\n")
            time.sleep(0.5)
            response = self.serial.read_all().decode()
            print("UART response:", response)
        except Exception as e:
            print("Error writing to UART:", e)