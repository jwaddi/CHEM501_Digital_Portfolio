# data_utils.py
# Data loading, cleaning, thresholds, anomaly detection

import pandas as pd
import numpy as np
import Dashboard_App as st

# --------------------------------------------------
# 1. Adding Live Data Tracking from CSV file
# ---------------------------------------------------
def read_latest_csv(csv_path, tail=200):
    """
    Read the most recent rows from a growing CSV file.
    Skips metadata header automatically.
    """
    try:
        df = pd.read_csv(csv_path, skiprows=4)
        if len(df) > tail:
            df = df.tail(tail)
        df = df.rename(columns={"Elapsed_Seconds": "Time (s)"})
        return df
    except Exception:
        return None

# --------------------------------------------------
# 2. CSV LOADING + STANDARDISATION
# --------------------------------------------------

def load_and_standardise_csv(path_or_buffer):
    """
    Load CSV file and standardise column names and types.
    Matches behaviour of original dashboard script.
    """
    # Skip metadata rows
    df = pd.read_csv(path_or_buffer, skiprows=4)

    expected_columns = [
        "Elapsed_Seconds",
        "Location_Note",
        "CO2_ppm",
        "VOC_ppm",
        "IAQ",
        "Gas_Res_Ohms",
        "Temp_Raw_C",
        "Temp_Comp_C",
        "Hum_Raw_pct",
        "Hum_Comp_pct",
        "Accuracy"
    ]

    missing = [c for c in expected_columns if c not in df.columns]
    if missing:
        print(f"Warning: missing columns in CSV: {missing}")

    # Standardise time column
    df = df.rename(columns={"Elapsed_Seconds": "Time (s)"})

    numeric_cols = [
        "Time (s)",
        "CO2_ppm",
        "VOC_ppm",
        "IAQ",
        "Gas_Res_Ohms",
        "Temp_Raw_C",
        "Temp_Comp_C",
        "Hum_Raw_pct",
        "Hum_Comp_pct",
        "Accuracy"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def build_data_dict_from_csv(csv_df):
    """
    Convert CSV dataframe into the data_dict structure used by the dashboard.
    """
    data_dict = {}

    for col in csv_df.columns:
        if col not in ["Time (s)", "Location_Note"]:
            data_dict[col] = csv_df[["Time (s)", col]].copy()

    numeric_cols = [c for c in csv_df.columns if c not in ["Time (s)", "Location_Note"]]
    data_dict["Overview"] = csv_df[["Time (s)"] + numeric_cols].copy()

    return data_dict

# -------------------------------------------------------------------
# 3. SIMULATED DATA (fallback in case no CSV file has been uploaded) 
# -------------------------------------------------------------------

def generate_data():
    data_dict = {
        "Air Pressure (atm)": pd.DataFrame({
            "Time (s)": np.arange(100),
            "Air Pressure (atm)": np.random.randint(20, 100, 100)
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
        })
    }
    return data_dict

# --------------------------------------------------
# 4. THRESHOLDS + ANOMALY DETECTION
# --------------------------------------------------

thresholds = {
    "CO2_ppm": (600, 1200),
    "VOC_ppm": (0, 5),
    "Temp_Comp_C": (18, 26),
    "Hum_Comp_pct": (30, 60),
    "IAQ": (50, 150),
}

iaq_thresholds = (50, 100, 150, 200, 250, 300, 1000)


def is_anomaly(var, val):
    if var == "IAQ":
        return val > iaq_thresholds[-1]
    if var in thresholds:
        low, high = thresholds[var]
        return val < low or val > high
    return False
