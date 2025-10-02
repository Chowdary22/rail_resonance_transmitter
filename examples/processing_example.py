#!/usr/bin/env python3
"""
Example script demonstrating how to use the new Processing Layer
"""

import pandas as pd
from processing.feature_extraction.processor import FeatureProcessor

def main():
    # Create some sample data
    data = {
        'timestamp': list(range(100)),
        'x_axis': [0.1 * i + 0.5 for i in range(100)],  # Linear trend
        'y_axis': [0.2 * i * i for i in range(100)],    # Quadratic trend
        'z_axis': [10 * i % 20 for i in range(100)]     # Sawtooth pattern
    }
    df = pd.DataFrame(data)
    
    # Create processor with 20Hz sampling rate
    processor = FeatureProcessor(sampling_rate=20)
    
    # Process data
    features = processor.process(df)
    
    if features:
        print("\nExtracted Features:")
        print("------------------")
        
        # Group features by type
        groups = {
            "Statistical": ["mean", "std", "min", "max", "rms"],
            "Frequency": ["fft", "freq", "energy"],
            "Time": ["timestamp", "duration"]
        }
        
        for group, keywords in groups.items():
            print(f"\n{group} Features:")
            for key, value in features.items():
                if any(kw in key for kw in keywords):
                    print(f"{key:25}: {value:10.4f}")
        
        # Save features
        processor.save_features(features, "example_features.csv")
    else:
        print("❌ Feature extraction failed")

if __name__ == "__main__":
    main()
