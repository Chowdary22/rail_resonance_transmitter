# ADXL345 Constants and Register Definitions

# Device Address
ADXL345_ADDRESS = 0x53

# Register Addresses
REG_DEVID = 0x00        # Device ID
REG_POWER_CTL = 0x2D    # Power Control
REG_DATA_FORMAT = 0x31  # Data Format Control
REG_BW_RATE = 0x2C     # Data Rate and Power Mode Control
REG_DATAX0 = 0x32      # X-axis Data 0
REG_DATAX1 = 0x33      # X-axis Data 1
REG_DATAY0 = 0x34      # Y-axis Data 0
REG_DATAY1 = 0x35      # Y-axis Data 1
REG_DATAZ0 = 0x36      # Z-axis Data 0
REG_DATAZ1 = 0x37      # Z-axis Data 1

# Configuration Values
RANGE_2G = 0x00    # ±2g range
RANGE_4G = 0x01    # ±4g range
RANGE_8G = 0x02    # ±8g range
RANGE_16G = 0x03   # ±16g range

RATE_100HZ = 0x0A  # 100 Hz output data rate
RATE_50HZ = 0x09   # 50 Hz output data rate
RATE_25HZ = 0x08   # 25 Hz output data rate
RATE_20HZ = 0x07   # 20 Hz output data rate

# Configuration Bits
MEASURE_BIT = 0x08  # Measurement mode
FULL_RES_BIT = 0x08  # Full resolution mode

# Conversion Factors
SCALE_FACTOR_2G = 256.0   # LSB/g for ±2g range
SCALE_FACTOR_4G = 128.0   # LSB/g for ±4g range
SCALE_FACTOR_8G = 64.0    # LSB/g for ±8g range
SCALE_FACTOR_16G = 32.0   # LSB/g for ±16g range

# Error Codes
ERR_DEVICE_NOT_FOUND = "ADXL345 device not found"
ERR_INVALID_RANGE = "Invalid measurement range"
ERR_INVALID_RATE = "Invalid data rate"
ERR_READ_FAILED = "Failed to read sensor data"
