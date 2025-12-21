# plot_utils.py
# All plotting logic for the dashboard

import matplotlib.pyplot as plt
import pandas as pd


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

    # ---------------------------------------------
    # Main plot
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
            marker="o",
            markersize=3
        )

        # -----------------------------------------
        # Anomaly detection
        # -----------------------------------------
        for _, row in selected_data.iterrows():
            val = row[y_col]
            t = row["Time (s)"]

            if option in thresholds:
                low, high = thresholds[option]
                if val < low or val > high:
                    ax.plot(
                        t, val,
                        marker="o",
                        linestyle="None",
                        markersize=4,
                        color="#9D00FF"
                    )

            if option == "IAQ" and val > iaq_thresholds[-1]:
                ax.plot(
                    t, val,
                    marker="o",
                    linestyle="None",
                    markersize=4,
                    color="#9D00FF"
                )

    # ---------------------------------------------
    # Threshold line
    # ---------------------------------------------
    if threshold_value is not None:
        ax.axhline(
            threshold_value,
            color="gray",
            linestyle="--",
            linewidth=1
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
