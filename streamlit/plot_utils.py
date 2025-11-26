import matplotlib.pyplot as plt

def plot_cleaned(df_raw, df_clean, y_col):
    """
    Generate a matplotlib figure comparing raw vs cleaned data.

    Parameters:
        df_raw (pd.DataFrame): Original data
        df_clean (pd.DataFrame): Cleaned/smoothed data
        y_col (str): Name of the column to plot

    Returns:
        fig: Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_raw["Time (s)"], df_raw[y_col], label="Raw", marker='o', markersize=3)
    ax.plot(df_clean["Time (s)"], df_clean[y_col], label="Cleaned", marker='o', markersize=3)
    ax.set_xlabel("Time (s)", weight='bold', size=15)
    ax.set_ylabel(y_col, weight='bold', size=15)
    ax.legend()
    return fig


def plot_live(data_dict, live_variables, thresholds=None, iaq_thresholds=None):
    """
    Generate figures for live tracking values with coloring based on thresholds.

    Parameters:
        data_dict (dict): Dictionary of dataframes for each variable
        live_variables (list): Variables to display in live tracking
        thresholds (dict, optional): Thresholds for each variable
        iaq_thresholds (tuple, optional): IAQ-specific thresholds

    Returns:
        dict: {variable: (value, color)}
    """
    live_values = {}
    for var in live_variables:
        df = data_dict[var]
        val = df.iloc[-1, 1]

        # determine color based on thresholds
    if var == "IAQ":
        match val: 
            case v if v <= iaq_thresholds[0]:
                color = "#66FF00"  # bright green
            case v if v <= iaq_thresholds[1]:
                color = "#61E160"  # green
            case v if v <= iaq_thresholds[2]: 
                color = "#FFFF00"  # yellow
            case v if v <= iaq_thresholds[3]: 
                color = "#FFA500" # orange
            case v if v <= iaq_thresholds[4]: 
                color = "#FF0000" # red
            case v if v <= iaq_thresholds[5]: 
                color = "#800080" # purple#
            case _:
                color = "#A52A2A"   # brown
    else:   
        low, high = thresholds.get(var, (0, 100))         
        if val < low:
            color = "#61E160"  # green
        elif val < high:
            color = "#FFA500"  # orange
        else:
            color = "#FF0000"  # red

        live_values[var] = (val, color)
    return live_values
