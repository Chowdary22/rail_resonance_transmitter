# Raspberry Pi Communication Init Scripts

This project contains basic Python scripts to initialize I2C, SPI, and UART interfaces on a Raspberry Pi 4B. These scripts are reusable templates for future sensor or peripheral integration.

## Files

| File         | Description                          |
|--------------|--------------------------------------|
| `main.py`    | Example script that ties it all together |
| `i2c_init.py`| Initializes I2C and reads sample register |
| `spi_init.py`| Initializes SPI and sends test data  |
| `uart_init.py`| Initializes UART and sends/receives |
| `README.md`  | Project documentation                |

## Requirements

Install required packages:

''bash
pip install smbus2 spidev pyserial

# Rail Vibration Project
Monitors vibration on a 7th axis rail using a Raspberry Pi, ADXL345 sensor, and RAK2013 modem.

## Files
- `main.py`: Starts the program and threads.
- `thread_handler.py`: Manages threads.
- `peripherals/`: Mock classes for I2C, SPI, UART.
- `tests/`: Test scripts.

## Setup
1. Activate virtual environment:
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
