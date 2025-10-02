# Rail Resonance Transmitter

A professional-grade rail vibration monitoring system using Raspberry Pi 4, ADXL345 accelerometer, and Quectel EC25-E LTE modem.

## 🏗️ System Architecture

### Hardware Components
- **Raspberry Pi 4B**: Main processing unit
- **ADXL345**: 3-axis accelerometer (±16g range, 20Hz sampling)
- **Quectel EC25-E**: LTE modem for cellular data transmission
- **Sixfab Hat**: Base hat with SIM card slot and antennas

### Software Components
- **Modular Design**: Separated concerns for maintainability
- **Real-time Processing**: 20Hz sensor sampling with feature extraction
- **Dual Communication**: Serial ACK + MQTT over LTE
- **Offline Buffering**: Local storage when network unavailable
- **Health Monitoring**: Continuous system status tracking

## 📁 Project Structure

```
rail_resonance_transmitter/
├── main.py                 # Main application entry point
├── config.py               # Centralized configuration
├── test_system.py          # Comprehensive system testing
├── modules/                # Core functionality modules
│   ├── feature_extractor.py    # Statistical + FFT analysis
│   ├── lte_transmitter.py     # Enhanced LTE communication
│   ├── communication_manager.py # Serial communication
│   └── data_formatter.py      # Data formatting utilities
├── peripherals/            # Hardware interface layer
│   ├── i2c_device.py          # ADXL345 sensor interface
│   ├── spi_device.py          # SPI device templates
│   └── uart_device.py         # UART device templates
└── tests/                  # Test scripts and validation
```

## 🚀 Features

### Data Collection
- **20Hz Sampling**: Continuous vibration monitoring
- **3-Axis Analysis**: X, Y, Z acceleration measurements
- **Real-time Processing**: Statistical and frequency domain features
- **Local Storage**: Raw data logging to SD card

### Feature Extraction
- **Statistical Features**: Mean, standard deviation, min/max, RMS
- **Frequency Analysis**: FFT-based dominant frequency detection
- **Multi-axis Processing**: Independent analysis of all axes
- **Data Validation**: Input validation and error handling

### Communication
- **LTE Transmission**: MQTT over cellular network
- **Offline Buffering**: 1000 message local buffer
- **Automatic Reconnection**: Robust network handling
- **Serial ACK**: Local communication verification

### System Monitoring
- **Health Checks**: Continuous component status monitoring
- **Error Recovery**: Graceful handling of failures
- **Performance Metrics**: Real-time system statistics
- **Graceful Shutdown**: Clean system termination

## ⚙️ Configuration

### Hardware Settings
```python
HARDWARE = {
    "sensor": {
        "i2c_bus": 1,
        "adxl345_address": 0x53,
        "sampling_frequency": 20,  # Hz
        "range": "16g"
    },
    "modem": {
        "uart_ports": ["/dev/ttyUSB2", "/dev/ttyUSB1", "/dev/ttyUSB0", "/dev/ttyUSB3"],
        "baudrate": 115200
    }
}
```

### Communication Settings
```python
COMMUNICATION = {
    "mqtt": {
        "broker": "test.mosquitto.org",  # Change to your broker
        "port": 1883,
        "topic": "rail/vibration/data"
    }
}
```

### Environment Variables
```bash
export MQTT_BROKER="your.broker.com"
export MQTT_TOPIC="custom/topic/path"
export LOG_BASE_PATH="/custom/log/path"
```

## 🧪 Testing

### Run System Tests
```bash
python3 test_system.py
```

Tests include:
- Module imports
- Configuration validation
- Sensor functionality
- Feature extraction
- Communication systems
- File system access

### Test Individual Components
```bash
# Test sensor only
python3 -c "from peripherals.i2c_device import I2CDevice; s=I2CDevice(1,0x53); print(s.read_data())"

# Test feature extraction
python3 -c "from modules.feature_extractor import preprocess_data; import pandas as pd; df=pd.DataFrame({'x_axis':[0,1,2],'y_axis':[0,1,2],'z_axis':[0,1,2]}); print(preprocess_data(df))"
```

## 📊 Data Output

### Raw Data Format
```csv
timestamp,x_axis,y_axis,z_axis
1693668000.123,0.15,-0.02,9.81
1693668000.173,0.18,0.03,9.82
```

### Processed Features
```json
{
  "mean_X": 0.165,
  "std_X": 0.015,
  "rms_X": 0.166,
  "fft_X_max": 0.25,
  "freq_X_dominant": 2.5,
  "sample_count": 10,
  "timestamp_start": 1693668000.123,
  "timestamp_end": 1693668000.623
}
```

## 🔧 Installation

### Prerequisites
- Raspberry Pi 4B with Raspberry Pi OS
- Python 3.7+
- ADXL345 sensor connected via I2C
- Quectel EC25-E modem with active SIM card

### Setup
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd rail_resonance_transmitter
   ```

2. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure Hardware**
   - Connect ADXL345 to I2C bus 1, address 0x53
   - Mount Sixfab hat with EC25-E modem
   - Insert active SIM card

4. **Update Configuration**
   - Edit `config.py` with your MQTT broker details
   - Verify UART port mapping for your setup

5. **Test System**
   ```bash
   python3 test_system.py
   ```

6. **Run Application**
   ```bash
   python3 main.py
   ```

## 📡 LTE Setup

### Modem Configuration
The system automatically detects and configures the Quectel EC25-E modem:
- **APN Detection**: Automatically finds correct APN settings
- **Connection Monitoring**: Continuous status tracking
- **Fallback Handling**: Graceful degradation when offline

### Troubleshooting
- **Check SIM Card**: Ensure data plan is active
- **Verify APN**: Contact carrier for correct APN settings
- **Signal Strength**: Monitor with `sudo qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength`
- **Network Registration**: Check with `sudo qmicli -d /dev/cdc-wdm0 --nas-get-serving-system`

## 🚨 Troubleshooting

### Common Issues
1. **Sensor Not Detected**: Check I2C bus and address
2. **Serial Communication Failed**: Verify UART port mapping
3. **LTE Connection Issues**: Check SIM card and APN settings
4. **Data Processing Errors**: Verify input data format

### Debug Commands
```bash
# Check I2C devices
i2cdetect -y 1

# Monitor system logs
journalctl -u rail-resonance -f

# Test modem connection
sudo qmicli -d /dev/cdc-wdm0 --wds-start-network="apn=internet"
```

## 📈 Performance

### System Requirements
- **CPU**: 25% average usage during operation
- **Memory**: ~50MB RAM usage
- **Storage**: ~1MB/day for raw data + features
- **Network**: 1KB/s average LTE data usage

### Optimization Tips
- Adjust sampling frequency in `config.py`
- Modify buffer size for different processing requirements
- Use environment variables for dynamic configuration
- Monitor system health for performance insights

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement improvements
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For technical support:
1. Check troubleshooting section
2. Review system logs
3. Run diagnostic tests
4. Open issue with detailed error information

---

**Built with ❤️ for rail safety and monitoring**
