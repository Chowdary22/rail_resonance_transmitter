# Serial communication with ACK for RAK2013
class SerialACKManager:
    def __init__(self):
        self.serial = serial.Serial(UART_PORT, UART_BAUDRATE, timeout=1)
    
    def send_ack(self, data):
        try:
            message = f"{data['x_axis']:.2f},{data['y_axis']:.2f},{data['z_axis']:.2f},{data['timestamp']:.2f}\n"
            self.serial.write(message.encode())
            response = self.serial.readline().decode().strip()
            return "OK" in response
        except Exception as e:
            print(f"Serial error: {e}")
            return False
    
    def close(self):
        self.serial.close()