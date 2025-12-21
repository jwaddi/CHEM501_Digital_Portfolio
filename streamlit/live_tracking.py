# live_tracking.py
# Real-time live tracking widget for Streamlit

import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh

import data_utils


def render_live_tracking(data_dict):
    """
    Render live tracking metrics in the sidebar with anomaly detection.
    """

    st.sidebar.subheader("Live Tracking")

    live_variables = [v for v in data_dict.keys() if v != "Overview"]

    # Create empty containers
    containers = {
        var: st.sidebar.empty() for var in live_variables
    }

    # Initial display
    for var, container in containers.items():
        df = data_dict[var]
        val = df.iloc[-1, 1]
        container.metric(label=var, value=f"{val}")

    # Auto refresh every 2 seconds
    st_autorefresh(interval=2000, key="live_refresh")

    # Update values
    for var, container in containers.items():
        df = data_dict[var]
        last_val = df.iloc[-1, 1]

        # Simulate new measurement from csv file
        df = pd.read_csv("live_sensor_data.csv")
        new_val = df.iloc[-1, 1]

        # Determine colour
        color = data_utils.get_color(var, new_val)

        # Anomaly detection
        anomaly = data_utils.is_anomaly(var, new_val)
        anomaly_flag = (
            "<div style='color:red; font-size:14px;'>Anomaly detected</div>"
            if anomaly else ""
        )

        container.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:16px; font-weight:bold;">{var}</div>
                <div style="font-size:36px; font-weight:bold; color:{color};">
                    {new_val}
                </div>
            </div>
            {anomaly_flag}
            """,
            unsafe_allow_html=True
        )
