# modules/feature_extractor.py
class FeatureExtractor:
    def convert_to_g(self, raw_data):
        return {
            "x_axis": raw_data["x_axis"] / 9.81,
            "y_axis": raw_data["y_axis"] / 9.81,
            "z_axis": raw_data["z_axis"] / 9.81,
            "timestamp": raw_data["timestamp"]
        }
