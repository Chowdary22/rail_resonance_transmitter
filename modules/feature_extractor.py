import pandas as pd
import numpy as np

# Load the raw sensor data from two CSV files
file_path_1 = '/home/testuser/logs/adxl345/adxl345_log_20250725-111035.csv'  
file_path_2 = '/home/testuser/logs/adxl345/adxl345_log_20250725-111110.csv'  

df1 = pd.read_csv(file_path_1)
df2 = pd.read_csv(file_path_2)

# Preprocessing function: Compute mean, std, FFT
def preprocess_data(df):
    features = {
        "mean_X": df['x_axis'].mean(),
        "std_X": df['x_axis'].std(),
        "mean_Y": df['y_axis'].mean(),
        "std_Y": df['y_axis'].std(),
        "mean_Z": df['z_axis'].mean(),
        "std_Z": df['z_axis'].std()
    }

    # Perform FFT on X, Y, Z axes
    fft_X = np.fft.fft(df['x_axis'].values)
    fft_Y = np.fft.fft(df['y_axis'].values)
    fft_Z = np.fft.fft(df['z_axis'].values)

    n = len(df['x_axis'])
    fft_X_mag = np.abs(fft_X[:n//2])  # Positive frequencies
    fft_Y_mag = np.abs(fft_Y[:n//2])
    fft_Z_mag = np.abs(fft_Z[:n//2])

    # Add FFT features (max amplitude of FFT)
    features["fft_X_max"] = np.max(fft_X_mag)
    features["fft_Y_max"] = np.max(fft_Y_mag)
    features["fft_Z_max"] = np.max(fft_Z_mag)

    return features

# Process the data from both files
features_1 = preprocess_data(df1)
features_2 = preprocess_data(df2)

# Save processed data into new CSV files
processed_file_1 = '/home/testuser/logs/processed/processed_features_1.csv'
processed_file_2 = '/home/testuser/logs/processed/processed_features_2.csv'

# Save the processed features as CSV
pd.DataFrame([features_1]).to_csv(processed_file_1, index=False)
pd.DataFrame([features_2]).to_csv(processed_file_2, index=False)

print(f"Processed data saved to {processed_file_1} and {processed_file_2}")
