# Configuration file for Rail Resonance Transmitter
# config.py

import os
import time  # Kept for potential timing needs

# === Hardware Configuration ===
HARDWARE = {
    "sensor": {
        "i2c_bus": 1,
        "adxl345_address": 0x53,
        "sampling_frequency": 20,  # Hz
        "range": "16g",  # ±16g range
        "resolution": "full"  # Full resolution mode
    },
    "modem": {
        "uart_ports": ["/dev/ttyUSB3", "/dev/ttyUSB2", "/dev/ttyUSB1", "/dev/ttyUSB0"],
        "baudrate": 115200,
        "timeout": 1
    }
}

# === Data Collection Configuration ===
DATA_COLLECTION = {
    "sensor_freq": 0.05,  # 20Hz = 0.05s interval
    "mqtt_send_freq": 1,  # Send data every 1 second
    "buffer_size": 10,  # Process data every 10 samples
    "max_offline_buffer": 1000  # Maximum offline messages to buffer
}

# === Communication Configuration ===
COMMUNICATION = {
    "mqtt": {
        "broker": "broker.emqx.io",  # Public broker with both 1883 and 8883 ports
        "port": 8883,  # Using secure port to bypass firewall
        "topic": "rail/vibration/data",
        "keepalive": 60,
        "connection_retry_interval": 10,  # Reduced to 10 seconds for faster retry
        "health_check_interval": 5,  # Reduced to 5 seconds
        # Stable client ID based on hostname to avoid churn across restarts
        "client_id": f"rail_sensor_{os.uname().nodename}"
    },
    "serial": {
        "retry_attempts": 3,
        "retry_delay": 0.5,  # seconds
        "timeout": 1.0  # seconds for serial read
    }
}

# === File Paths ===
PATHS = {
    "logs": {
        "base": "/home/testuser/logs",
        "raw_data": "/home/testuser/logs/adxl345",
        "processed_data": "/home/testuser/logs/processed",
        "buffer": "/home/testuser/logs/buffer",  # Directory for buffer files
        "offline_buffer": "/home/testuser/logs/buffer/offline_data.json"  # Actual buffer file
    }
}

# === GPIO Configuration ===
GPIO = {
    "alert_led_pin": 18,
    "mode": "BCM"
}

# === Feature Extraction Configuration ===
FEATURES = {
    "fft_enabled": True,
    "rms_enabled": True,
    "statistical_enabled": True,
    "frequency_analysis": True
}

# === System Configuration ===
SYSTEM = {
    "health_monitoring_interval": 30,  # seconds
    "max_sensor_errors": 5,
    "graceful_shutdown_timeout": 5  # seconds
}

# === Validation Functions ===
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check if log directories exist or can be created
    for path_name, path in PATHS["logs"].items():
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create log directory {path}: {e}")
    
    # Validate hardware settings
    if DATA_COLLECTION["sensor_freq"] <= 0:
        errors.append("Sensor frequency must be positive")
    
    if DATA_COLLECTION["buffer_size"] < 2:
        errors.append("Buffer size must be at least 2")
    
    # Validate communication settings
    if COMMUNICATION["mqtt"]["port"] < 1 or COMMUNICATION["mqtt"]["port"] > 65535:
        errors.append("Invalid MQTT port number")
    
    if COMMUNICATION["mqtt"]["connection_retry_interval"] < 1:
        errors.append("Connection retry interval must be at least 1 second")
    
    return errors

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        "hardware": {
            "sensor": f"ADXL345 on I2C bus {HARDWARE['sensor']['i2c_bus']} at 0x{HARDWARE['sensor']['adxl345_address']:02X}",
            "sampling_rate": f"{HARDWARE['sensor']['sampling_frequency']} Hz",
            "modem_ports": HARDWARE['modem']['uart_ports']
        },
        "data_collection": {
            "sensor_interval": f"{DATA_COLLECTION['sensor_freq']}s",
            "processing_buffer": DATA_COLLECTION['buffer_size'],
            "mqtt_interval": f"{DATA_COLLECTION['mqtt_send_freq']}s"
        },
        "communication": {
            "mqtt_broker": f"{COMMUNICATION['mqtt']['broker']}:{COMMUNICATION['mqtt']['port']}",
            "topic": COMMUNICATION['mqtt']['topic'],
            "offline_buffer": DATA_COLLECTION['max_offline_buffer']
        },
        "paths": {
            "raw_data": PATHS['logs']['raw_data'],
            "processed_data": PATHS['logs']['processed_data']
        }
    }

# === Environment-specific Overrides ===
def load_environment_config():
    """Load environment-specific configuration overrides"""
    import os
    
    # Override MQTT broker from environment if set
    env_broker = os.getenv('MQTT_BROKER')
    if env_broker:
        COMMUNICATION['mqtt']['broker'] = env_broker
        print(f"📡 MQTT broker overridden from environment: {env_broker}")
    
    # Override MQTT topic from environment if set
    env_topic = os.getenv('MQTT_TOPIC')
    if env_topic:
        COMMUNICATION['mqtt']['topic'] = env_topic
        print(f"📝 MQTT topic overridden from environment: {env_topic}")
    
    # Override log paths from environment if set
    env_log_base = os.getenv('LOG_BASE_PATH')
    if env_log_base:
        PATHS['logs']['base'] = env_log_base
        PATHS['logs']['raw_data'] = os.path.join(env_log_base, 'adxl345')
        PATHS['logs']['processed_data'] = os.path.join(env_log_base, 'processed')
        PATHS['logs']['offline_buffer'] = os.path.join(env_log_base, 'offline_buffer.json')
        print(f"📁 Log paths overridden from environment: {env_log_base}")

# Load environment config on import
load_environment_config()
