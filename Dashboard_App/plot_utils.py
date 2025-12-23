# plot_utils.py
# All plotting logic for the dashboard

from click import option
import matplotlib.pyplot as plt
import pandas as pd

from data_utils import thresholds, iaq_thresholds, DISPLAY_TO_SENSOR, is_anomaly


def plot_main_chart(
    selected_data,
    option,
    y_col,
    thresholds,
    iaq_thresholds,
    threshold_value=None,
    time_point=None
):
    """
    Plot main time-series chart with anomaly detection, optional threshold
    line, and optional time-point marker.
    """
    fig, ax = plt.subplots()
    # Resolve sensor key
    sensor_key = DISPLAY_TO_SENSOR.get(option, option)

    # ---------------------------------------------
    # Main plot of data
    # ---------------------------------------------
    if option == "Overview":
        for col in selected_data.columns[1:]:
            ax.plot(
                selected_data["Time (s)"],
                selected_data[col],
                label=col,
                markersize=2
            )
        ax.legend()
    else:
        ax.plot(
            selected_data["Time (s)"],
            selected_data[y_col],
            linewidth=1.5
        )

# --------------------------------------------------
# Drawing both threshold lines
# --------------------------------------------------
    if sensor_key:
        if sensor_key == "IAQ":
            low, high = iaq_thresholds[0], iaq_thresholds[2]
        elif sensor_key in thresholds:
            low, high = thresholds[sensor_key]
        else:
            low, high = None, None

        if low is not None and high is not None:
            ax.axhline(low, linestyle="--", linewidth=1, color="gray")
            ax.axhline(high, linestyle="--", linewidth=1, color="gray")

        # -----------------------------------------
        # Anomaly detection
        # -----------------------------------------
    anomaly_x = []
    anomaly_y = []

    if option != "Overview" and sensor_key in thresholds:

        low, high = thresholds[sensor_key]

        for _, row in selected_data.iterrows():
            time = row["Time (s)"]
            val = row[y_col]

            if val < low or val > high:
                anomaly_x.append(time)
                anomaly_y.append(val)

    elif option == "IAQ":

        for _, row in selected_data.iterrows():
            time = row["Time (s)"]
            val = row[y_col]

            if val > iaq_thresholds[-1]:
                anomaly_x.append(time)
                anomaly_y.append(val)

    if anomaly_x:
        ax.scatter(
        anomaly_x,
        anomaly_y,
        color="#9D00FF",
        s=5,
        zorder=10,
        label="Anomaly"
    )


    # ---------------------------------------------
    # Time-point marker
    # ---------------------------------------------
    if time_point is not None:
        ax.axvline(
            time_point,
            color="blue",
            linestyle="--",
            linewidth=1
        )

    # ---------------------------------------------
    # Labels
    # ---------------------------------------------
    ax.set_xlabel("Time (s)", weight="bold", size=15)
    ax.set_ylabel(
        "Values" if option == "Overview" else y_col,
        weight="bold",
        size=15
    )

    if option != "Overview" and sensor_key:
        if sensor_key == "IAQ":
            low, high = iaq_thresholds[0], iaq_thresholds[2]
        elif sensor_key in thresholds:
            low, high = thresholds[sensor_key]
        else:
            low, high = None, None

        if low is not None and high is not None:
            ax.axhline(low, linestyle="--", linewidth=1, color="gray")
            ax.axhline(high, linestyle="--", linewidth=1, color="gray")

    return fig


def plot_comparison(data_dict, compare_variables):
    """
    Plot comparison chart for multiple variables.
    """
    fig, ax = plt.subplots()

    for var in compare_variables:
        df = data_dict[var]
        y_col = df.columns[1]

        ax.plot(
            df["Time (s)"],
            df[y_col],
            label=var,
            marker="o",
            markersize=3
        )

    ax.set_xlabel("Time (s)", weight="bold", size=15)
    ax.set_ylabel("Values", weight="bold", size=15)
    ax.legend()

    return fig


def plot_raw_vs_cleaned(df_raw, df_clean, y_col):
    """
    Plot raw vs cleaned data comparison.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        df_raw["Time (s)"],
        df_raw[y_col],
        label="Raw",
        marker="o",
        markersize=3
    )
    ax.plot(
        df_clean["Time (s)"],
        df_clean[y_col],
        label="Cleaned",
        marker="o",
        markersize=3
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(y_col)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    return fig
