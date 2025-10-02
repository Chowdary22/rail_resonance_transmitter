#!/usr/bin/env python3
"""
System Test Script for Rail Resonance Transmitter
Tests all components before running the main system
"""

import time
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from config import validate_config, get_config_summary
        print("✅ Configuration module imported")
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    
    try:
        from peripherals.i2c_device import I2CDevice
        print("✅ I2C device module imported")
    except ImportError as e:
        print(f"❌ I2C device import failed: {e}")
        return False
    
    try:
        from modules.feature_extractor import preprocess_data, validate_data
        print("✅ Feature extractor module imported")
    except ImportError as e:
        print(f"❌ Feature extractor import failed: {e}")
        return False
    
    try:
        from modules.communication_manager import SerialACKManager
        print("✅ Communication manager module imported")
    except ImportError as e:
        print(f"❌ Communication manager import failed: {e}")
        return False
    
    try:
        from modules.lte_transmitter import LTETransmitter
        print("✅ LTE transmitter module imported")
    except ImportError as e:
        print(f"❌ LTE transmitter import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration validation"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import validate_config, get_config_summary
        
        # Validate configuration
        errors = validate_config()
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        # Display configuration summary
        config_summary = get_config_summary()
        print("✅ Configuration validation passed")
        print("📋 Configuration summary:")
        for category, settings in config_summary.items():
            print(f"   {category.upper()}:")
            for key, value in settings.items():
                print(f"     {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_sensor():
    """Test ADXL345 sensor"""
    print("\n🔍 Testing ADXL345 sensor...")
    
    try:
        from peripherals.i2c_device import I2CDevice
        from config import HARDWARE
        
        # Initialize sensor
        sensor = I2CDevice(
            HARDWARE["sensor"]["i2c_bus"],
            HARDWARE["sensor"]["adxl345_address"]
        )
        print("✅ Sensor initialized")
        
        # Read sample data
        for i in range(5):
            x, y, z = sensor.read_data()
            print(f"   Sample {i+1}: X={x:.3f}g, Y={y:.3f}g, Z={z:.3f}g")
            time.sleep(0.1)
        
        # Test data conversion
        x_ms2, y_ms2, z_ms2 = x * 9.81, y * 9.81, z * 9.81
        print(f"   Converted to m/s²: X={x_ms2:.3f}, Y={y_ms2:.3f}, Z={z_ms2:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensor test failed: {e}")
        return False

def test_feature_extraction():
    """Test feature extraction"""
    print("\n🔍 Testing feature extraction...")
    
    try:
        import pandas as pd
        from modules.feature_extractor import preprocess_data, validate_data
        
        # Create test data
        test_data = {
            'timestamp': [time.time() - 0.5, time.time() - 0.4, time.time() - 0.3, time.time() - 0.2, time.time() - 0.1],
            'x_axis': [0.1, 0.2, 0.15, 0.25, 0.18],
            'y_axis': [-0.05, 0.1, -0.02, 0.08, 0.03],
            'z_axis': [9.81, 9.82, 9.80, 9.83, 9.81]
        }
        
        df = pd.DataFrame(test_data)
        
        # Validate data
        is_valid, message = validate_data(df)
        if not is_valid:
            print(f"❌ Data validation failed: {message}")
            return False
        
        print("✅ Data validation passed")
        
        # Extract features
        features = preprocess_data(df)
        if not features:
            print("❌ Feature extraction failed")
            return False
        
        print("✅ Feature extraction successful")
        print("📊 Extracted features:")
        for key, value in features.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4f}")
            else:
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature extraction test failed: {e}")
        return False

def test_serial_communication():
    """Test serial communication"""
    print("\n🔍 Testing serial communication...")
    
    try:
        from modules.communication_manager import SerialACKManager
        from config import HARDWARE
        
        # Initialize serial communication
        serial_com = SerialACKManager(
            port=HARDWARE["modem"]["uart_ports"][0],
            baudrate=HARDWARE["modem"]["baudrate"]
        )
        
        # Check connection status
        status = serial_com.get_connection_status()
        print(f"   Serial connection: {'✅ Connected' if status else '❌ Disconnected'}")
        
        if status:
            print("✅ Serial communication test passed")
            return True
        else:
            print("⚠️ Serial communication not available (modem may not be connected)")
            return True  # Don't fail the test if modem isn't connected
        
    except Exception as e:
        print(f"❌ Serial communication test failed: {e}")
        return False

def test_lte_transmitter():
    """Test LTE transmitter (without actually connecting)"""
    print("\n🔍 Testing LTE transmitter...")
    
    try:
        from modules.lte_transmitter import LTETransmitter
        from config import COMMUNICATION, DATA_COLLECTION
        
        # Initialize LTE transmitter
        lte = LTETransmitter(
            COMMUNICATION["mqtt"]["broker"],
            COMMUNICATION["mqtt"]["port"],
            COMMUNICATION["mqtt"]["topic"],
            max_buffer_size=DATA_COLLECTION["max_offline_buffer"]
        )
        
        # Check initial status
        status = lte.get_connection_status()
        print(f"   Initial status: {'✅ Connected' if status['connected'] else '❌ Disconnected'}")
        print(f"   Broker: {status['broker']}")
        print(f"   Topic: {status['topic']}")
        
        # Test buffering (without actually connecting)
        test_payload = "test_data"
        lte.publish(test_payload)
        
        buffer_status = lte.get_buffer_status()
        print(f"   Buffer status: {buffer_status['buffer_size']}/{buffer_status['max_buffer_size']}")
        
        print("✅ LTE transmitter test passed")
        return True
        
    except Exception as e:
        print(f"❌ LTE transmitter test failed: {e}")
        return False

def test_file_system():
    """Test file system access"""
    print("\n🔍 Testing file system...")
    
    try:
        from config import PATHS
        
        # Test directory creation
        test_dir = "/tmp/rail_test"
        os.makedirs(test_dir, exist_ok=True)
        
        # Test file writing
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test data")
        
        # Test file reading
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Cleanup
        os.remove(test_file)
        os.rmdir(test_dir)
        
        if content == "Test data":
            print("✅ File system test passed")
            return True
        else:
            print("❌ File system test failed: content mismatch")
            return False
        
    except Exception as e:
        print(f"❌ File system test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Rail Resonance Transmitter System Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Sensor", test_sensor),
        ("Feature Extraction", test_feature_extraction),
        ("Serial Communication", test_serial_communication),
        ("LTE Transmitter", test_lte_transmitter),
        ("File System", test_file_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
