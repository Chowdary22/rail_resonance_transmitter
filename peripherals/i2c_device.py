# i2c_device.py
import smbus2
import time

class I2CDevice:
    def __init__(self, bus, address):
        self.bus = smbus2.SMBus(bus)  # Initialize I2C bus (bus 1 on Raspberry Pi)
        self.address = address  # ADXL345 I2C address (0x53)
        self._setup_adxl345()  # Configure the sensor when initialized

    def _setup_adxl345(self):
        try:
            # ADXL345 register addresses
            POWER_CTL = 0x2D  # Power control register
            DATA_FORMAT = 0x31  # Data format register
            BW_RATE = 0x2C  # Bandwidth rate register

            # Configure ADXL345
            self.bus.write_byte_data(self.address, DATA_FORMAT, 0x0B)  # Full resolution, ±16g range
            self.bus.write_byte_data(self.address, BW_RATE, 0x0A)  # 100 Hz output rate
            self.bus.write_byte_data(self.address, POWER_CTL, 0x08)  # Enable measurement mode
            time.sleep(0.1)  # Wait for sensor to stabilize
            print("ADXL345 initialized successfully")
        except Exception as e:
            print("Error setting up ADXL345:", e)

    def read_data(self):
        try:
            # ADXL345 data registers (X, Y, Z axes, 2 bytes each)
            data = self.bus.read_i2c_block_data(self.address, 0x32, 6)
            # Convert 2-byte data to signed integers (little-endian)
            x = int.from_bytes(data[0:2], byteorder='little', signed=True)
            y = int.from_bytes(data[2:4], byteorder='little', signed=True)
            z = int.from_bytes(data[4:6], byteorder='little', signed=True)
            # Convert raw values to g (assuming ±16g range, full resolution)
            # ADXL345 sensitivity: ~256 LSB/g for ±16g in full resolution
            x_g = x / 256.0
            y_g = y / 256.0
            z_g = z / 256.0
            return x_g, y_g, z_g
        except Exception as e:
            print("Error reading ADXL345:", e)
            return 0.0, 0.0, 0.0  # Return zeros on error