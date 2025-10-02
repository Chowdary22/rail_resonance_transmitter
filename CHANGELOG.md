# Rail Resonance Transmitter - Change Log

## System Components Status

### ✅ Working Components
- **ADXL345 Sensor**: Fully functional, providing accurate readings
- **Data Processing**: Successfully computing 25 features
- **GPIO System**: Properly initialized and managed
- **Logging System**: Creating and writing to all log files
- **Configuration System**: Centralized and validated

### ⚠️ Partially Working
- **Modem Communication**: Initializes but has response issues
- **Buffer System**: Structure fixed but needs testing

### ❌ Needs Attention
- **MQTT Connection**: Still facing connectivity issues
- **Serial ACK**: Response handling needs improvement

## Detailed Changes

### 1. GPIO System Updates
```python
# Changed from
import RPi.GPIO as GPIO
# To
import RPi.GPIO as RPiGPIO

# Updated all GPIO calls
RPiGPIO.setmode(RPiGPIO.BCM)
RPiGPIO.setup(GPIO_CONFIG["alert_led_pin"], RPiGPIO.OUT)
RPiGPIO.cleanup()
```

### 2. MQTT Configuration Evolution
```python
# Initial configuration
"broker": "test.mosquitto.org"
# First update
"broker": "broker.hivemq.com"
# Current configuration
"broker": "broker.emqx.io"
"port": 8883  # Secure port
```

### 3. Modem Communication Improvements

#### Initial Implementation
```python
# Basic initialization sequence
init_commands = [
    "AT",           # Test command
    "ATE0",        # Disable echo
    "AT+CMEE=2",   # Enable verbose errors
    "AT+CPIN?",    # Check SIM
    "AT+CSQ"       # Signal quality
]
```

#### Enhanced Implementation (Latest)
```python
# Comprehensive initialization with timing
init_commands = [
    ("AT", 1),                 # Test command with 1s wait
    ("ATZ", 2),               # Reset modem to defaults
    ("ATE0", 1),              # Disable echo
    ("AT+CMEE=2", 1),         # Enable verbose errors
    ("AT+CPIN?", 1),          # Check SIM status
    ("AT+CSQ", 1),            # Check signal quality
    ("AT+CREG?", 1),          # Check network registration
    ("AT+COPS?", 1),          # Check current operator
    ("AT+QIURC=1", 1),        # Enable URC for data calls
    ("AT+QICSGP=1,1,\\"\\",\\"\\",\\"\\",1", 1),  # Set APN profile
    ("AT+QIACT=1", 2),        # Activate PDP context
    ("AT+QISTATE?", 1)        # Check PDP context state
]
```

#### Improvements Made:
1. Added proper command timing
2. Added PDP context activation
3. Added network registration check
4. Added operator verification
5. Improved response handling
6. Added buffer management
7. Added detailed error reporting

#### Latest Debug Enhancements:
1. **Detailed Command Logging**
   - Show command being sent
   - Display wait time for each command
   - Show raw response data
   - Show response length

2. **Smart Response Parsing**
   - Signal strength extraction (CSQ)
   - Network registration status (CREG)
   - Current operator information (COPS)
   - Detailed error reporting

3. **Improved Error Handling**
   - Better error classification
   - More informative error messages
   - Non-fatal handling of initial AT test
   - Response validation for each command type

### 4. Data Processing Optimization
- Changed from string format to direct numeric storage
- Added validation for processed features
- Improved error handling in processing pipeline

### 5. File Structure
```
rail_resonance_transmitter/
├── main.py                 # Main application
├── config.py              # Centralized configuration
├── modules/               # Core functionality
│   ├── feature_extractor.py
│   ├── lte_transmitter.py
│   ├── communication_manager.py
│   └── data_formatter.py
└── peripherals/           # Hardware interfaces
    ├── i2c_device.py
    └── uart_device.py
```

### 6. Configuration System
```python
HARDWARE = {
    "sensor": {
        "i2c_bus": 1,
        "adxl345_address": 0x53,
        "sampling_frequency": 20
    },
    "modem": {
        "uart_ports": ["/dev/ttyUSB2", "/dev/ttyUSB1", "/dev/ttyUSB0", "/dev/ttyUSB3"],
        "baudrate": 115200
    }
}

PATHS = {
    "logs": {
        "base": "/home/testuser/logs",
        "raw_data": "/home/testuser/logs/adxl345",
        "processed_data": "/home/testuser/logs/processed",
        "buffer": "/home/testuser/logs/buffer",
        "offline_buffer": "/home/testuser/logs/buffer/offline_data.json"
    }
}
```

## Current Issues and Next Steps

### MQTT Connection
- Current Error: `[Errno 111] Connection refused`
- Possible solutions:
  1. Try alternative ports (1883, 443)
  2. Implement SSL/TLS for secure connection
  3. Test with local broker

### Serial Communication
- Current Status: Modem initializes but doesn't respond to data
- Next steps:
  1. Implement proper data mode
  2. Add response validation
  3. Improve timing between commands

## Environment Requirements

- Python 3.7+
- Raspberry Pi OS
- Required packages in requirements.txt
- Hardware:
  - Raspberry Pi 4B
  - ADXL345 sensor
  - Quectel EC25-E modem
  - Sixfab hat

## Testing Status

- ✅ GPIO functionality
- ✅ Sensor readings
- ✅ Data processing
- ✅ Log file operations
- ❌ MQTT connectivity
- ⚠️ Modem communication

## Next Development Phase

1. Complete modem communication reliability
2. Establish stable MQTT connection
3. Implement comprehensive error recovery
4. Add system monitoring dashboard
5. Implement data backup system

## Architecture Consolidation (Latest)

### Major Simplification - December 2024

**Goal**: Reduce complexity from 12+ files to 6 core files while preserving all functionality.

#### New Simplified Structure
```
rail_resonance_transmitter/
├── main.py                 # Main orchestrator (simplified)
├── config.py              # Configuration (unchanged)
├── sensor.py              # All sensor functionality
├── processor.py           # All feature extraction
├── communication.py       # Simple serial ACK
├── transmitter.py         # MQTT over LTE
└── examples/              # Keep examples
```

#### Files Consolidated

**Sensor Layer** (3 files → 1 file):
- `peripherals/sensor_manager/manager.py` + `data_handling/collector.py` + `peripherals/adxl345_driver/driver.py` → `sensor.py`
- New `Sensor` class with: `initialize()`, `start_collection()`, `get_latest_readings()`, `get_status()`, `shutdown()`
- Preserves: ADXL345 I2C handling, threaded collection, bounded queue buffering

**Processing Layer** (5 files → 1 file):
- `processing/feature_extraction/*` + `modules/feature_extractor.py` → `processor.py`
- New functions: `process_batch()`, `format_csv()`
- Preserves: Statistical features, frequency domain analysis, data validation, CSV formatting

**Communication Layer** (287 lines → 20 lines):
- `modules/communication_manager.py` → `communication.py`
- New function: `send_ack(port, baudrate, message)`
- Preserves: Serial ACK with retry logic from config

**Transport Layer** (rename only):
- `modules/lte_transmitter.py` → `transmitter.py`
- Re-exports `LTETransmitter` for simpler imports
- Preserves: MQTT over LTE, TLS on 8883, offline buffering, drain loop

#### Main.py Updates
- Simplified imports: `from sensor import Sensor`
- Streamlined main loop: fetch readings → process batch → log CSV → ACK → publish
- Preserved: Raw CSV logging, processed CSV logging, health monitoring, error handling
- Removed: Manual buffer management, complex threading, redundant formatter

#### Benefits Achieved
- **60% reduction** in file count (12+ → 6 files)
- **Cleaner imports**: Simple module names instead of deep paths
- **Easier maintenance**: Less code to understand and modify
- **Preserved functionality**: All core features maintained
- **Better testing**: Fewer components to test

#### Core Features Preserved
- ✅ ADXL345 sensor data collection via I2C
- ✅ Data buffering and processing (statistical + frequency features)
- ✅ LTE transmission capability with offline buffering
- ✅ Error handling and logging (CSV files)
- ✅ Serial ACK verification
- ✅ Configuration management
- ✅ Health monitoring

#### Migration Notes
- Old complex modules remain for reference but are no longer used
- New simplified modules maintain same external behavior
- All configuration settings preserved in `config.py`
- Examples updated to use new simplified structure

---
Last Updated: 2024-12-19 16:30:00
