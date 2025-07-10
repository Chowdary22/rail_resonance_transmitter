import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock
from peripherals.i2c_device import I2CDevice
from peripherals.spi_device import SPIDevice
from peripherals.uart_device import UARTDevice
from thread_handler import start_thread

import pytest
import time

# Test 1: I2C read_data()
def test_i2c_read_data_range():
    i2c = I2CDevice(bus=1, address=0x53)
    x, y, z = i2c.read_data()
    assert -10 <= x <= 10
    assert -10 <= y <= 10
    assert -10 <= z <= 10

# Test 2: UART write() mock
def test_uart_write():
    mock_uart = MagicMock()
    device = UARTDevice(port="COM1", baudrate=9600)
    device.write = mock_uart.write
    device.write("Hello")
    mock_uart.write.assert_called_once_with("Hello")

# Test 3: SPI read_data() output
def test_spi_read_data():
    spi = SPIDevice(bus=0, device=0)
    assert spi.read_data() is None

# Test 4: start_thread with fake task
def test_thread_starts_and_runs():
    flag = {"ran": False}
    def dummy_task(*args):
        flag["ran"] = True

    start_thread("dummy", dummy_task, (None,))
    time.sleep(0.1)  # Wait a bit for the thread to run
    assert flag["ran"]
