# peripherals/spi_device.py
# Mock SPI device
class SPIDevice:
    def __init__(self, bus, device):
        self.bus = bus
        self.device = device
        print("SPI device ready on bus", bus, "device", device)

    def read_data(self):
        print("No SPI data yet")
        return None