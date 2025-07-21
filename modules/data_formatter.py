# modules/data_formatter.py
class DataFormatter:
    def format_csv_string(self, processed):
        return f"{processed['x_axis']:.2f},{processed['y_axis']:.2f},{processed['z_axis']:.2f},{processed['timestamp']:.2f}"
