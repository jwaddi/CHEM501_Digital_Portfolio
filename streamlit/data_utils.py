# data loading, cleaning, smoothing functions

import pandas as pd
import numpy as np

# 
# 1. Simulated Data
# 

# change this to reading data file once we have collected data 
# eg. def load_csv(file_path):
   # """Load CSV into a DataFrame."""
   #return pd.read_csv(file_path)


def generate_data():
    data_dict = {
        "Air Pressure (atm)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "Air Pressure (atm)": np.random.randint(20, 100, 100)
        }),
        "BSEC Temperature (°C)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "Temp (°C)": np.random.randint(20, 100, 100)
        }),
        "CO2 Levels (ppm)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "CO2 (ppm)": np.random.randint(300, 600, 100)
        }),
        "Humidity (%)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "Humidity (%)": np.random.randint(20, 80, 100)
        }),
        "IAQ": pd.DataFrame({
            "Time (s)": np.arange(100),
            "IAQ": np.random.randint(0, 150, 100)
        }),
        "Temperature (°C)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "Temp (°C)": np.random.randint(20, 100, 100)
        }),
        "Volatile Organic Compounds (ppm)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "VOC (ppm)": np.random.randint(0, 10, 100)
        }),
        "Overview": pd.DataFrame({
            "Time (s)": np.arange(100),
            "Air Pressure (atm)": np.random.randint(20, 100, 100),
            "CO2 (ppm)": np.random.randint(300, 600, 100),
            "Humidity (%)": np.random.randint(20, 80, 100),
            "IAQ (AQI)": np.random.randint(0, 150, 100),
            "Temp (°C)": np.random.randint(20, 100, 100),
            "VOC (ppm)": np.random.randint(0, 10, 100)
        })
    }
    return data_dict


# 
# 2. Thresholds
#
thresholds = {
    "CO2 Levels (ppm)": (600, 1200),
    "Air Pressure (atm)": (50, 80), 
    "Humidity (%)": (30, 60),
    "Temperature (°C)": (20, 35),
    "BSEC Temperature (°C)": (20, 35),
    "Volatile Organic Compounds (ppm)": (0, 5)
}

iaq_thresholds = (50, 100, 150, 200, 250, 300, 1000)


#
# 3. Color Coding / Anomaly Detection
# 
def get_color(var, val):
    """Return HTML color string based on thresholds."""
    if var == "IAQ":
        if val <= iaq_thresholds[0]:
            return "#66FF00"
        elif val <= iaq_thresholds[1]:
            return "#61E160"
        elif val <= iaq_thresholds[2]:
            return "#FFFF00"
        elif val <= iaq_thresholds[3]:
            return "#FFA500"
        elif val <= iaq_thresholds[4]:
            return "#FF0000"
        elif val <= iaq_thresholds[5]:
            return "#800080"
        else:
            return "#A52A2A"
    else:
        low, high = thresholds.get(var, (0, 100))
        if val < low:
            return "#61E160"
        elif val < high:
            return "#FFA500"
        else:
            return "#FF0000"


def is_anomaly(var, val):
    """Return True if value is outside thresholds."""
    if var == "IAQ":
        return val > iaq_thresholds[-1]
    elif var in thresholds:
        low, high = thresholds[var]
        return val < low or val > high
    return False


# 
# 4. Data Cleaning / Smoothing
# 
def remove_outliers(df, col):
    z_scores = (df[col] - df[col].mean()) / df[col].std()
    return df[np.abs(z_scores) < 3]

def moving_average(df, col, window=5):
    df[col] = df[col].rolling(window=window, center=True, min_periods=1).mean()
    return df

def savgol_smoothing(df, col, window=5, polyorder=2):
    from scipy.signal import savgol_filter
    if len(df[col]) >= window:
        df[col] = savgol_filter(df[col], window_length=window, polyorder=polyorder)
    return df
