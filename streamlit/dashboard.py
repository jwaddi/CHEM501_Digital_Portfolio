"""
Project: THE STUFFY STUDY (CHEM501)
Experiment: An Investigation into the Ventilation and Learning Environment in Student Study Spaces
Module: A Dashboard for Visualising and Cleaning Data | Role: Real-Time Data Visualisation, Graphs, Tables and Ability to Download Data in .csv, .json, .pdf and .excel formats. 
Description:
	This script presents the code used to create the dashboard. 
    This includes using Python and HTML to create a visually-appealing, logical and clean space to visualise data collected. 
    The script includes a theme option between light and dark, selection of variable views, multiple tabs with 1. a data table,
    2. a chart, 3. summary statistics, 4. reference data, 5. data cleaning and 6. data download options. 
    There are also additional options of visualising the data for multiple variables at once in a graph, 
    real-time data and anomaly detection. 
System Requirements:
    1. pip install the following packages: 
    streamlit, pandas, numpy, matplotlib, PIL, time, scipy.signal and json. 
Authors: Josh and Kinga
Date: November 2025
License: MIT
"""


import streamlit as st 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import matplotlib as mt
from PIL import Image
import time
from scipy.signal import savgol_filter
import json

# need to figure this out (aka have data to upload)
# uploaded_file = st.sidebar.file_uploader("Upload CSV dataset")

#define class named project title and apply it to your title element
st.markdown('<h1 class="project-title">The Stuffy Study Pod: An Investigation into the Ventilation and Learning Environment in Student Study Spaces</h1>', unsafe_allow_html=True)

#
# CSV Input File
#

st.sidebar.subheader("Data input")

uploaded_file = st.sidebar.file_uploader("Upload CSV dataset (CSV)", type=["csv"])

use_local_path = st.sidebar.checkbox("Load CSV from local path (developer mode)", value=False)
local_path = ""
if use_local_path:
    local_path = st.sidebar.text_input("Enter local CSV path", value="")


def load_and_standardise_csv(path_or_buffer):
    # Skip the metadata lines at the top
    df = pd.read_csv(path_or_buffer, skiprows=4)

    # Ensure all expected sensor columns remain
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
        st.warning(f"Missing columns in CSV: {missing}")

    # Standardise time column name
    df = df.rename(columns={"Elapsed_Seconds": "Time (s)"})

    # Convert numerics safely
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


# Handle CSV loading
csv_df = None
if uploaded_file is not None:
    try:
        csv_df = load_and_standardise_csv(uploaded_file)
        st.sidebar.success("CSV uploaded successfully")
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")

elif use_local_path and local_path:
    try:
        csv_df = load_and_standardise_csv(local_path)
        st.sidebar.success("CSV loaded from path")
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")


# Inject custom CSS to style the title
st.markdown(
    """
    <style>
    .project-title {
        color: #E7E8CB;
        font-size: 2.5em;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#
# Theme toggle
#
theme_choice = st.sidebar.radio("Theme", ["Light", "Dark"], index=0)

def apply_theme(theme):
    if theme == "Dark":
        # matplotlib dark style like dark_background but minimal manual settings
        mt.rcParams.update({
            "axes.facecolor": "#222222",
            "figure.facecolor": "#222222",
            "savefig.facecolor": "#222222",
            "axes.edgecolor": "#E7E8CB",
            "axes.labelcolor": "#E7E8CB",
            "xtick.color": "#E7E8CB",
            "ytick.color": "#E7E8CB",
            "text.color": "#E7E8CB",
            "legend.facecolor": "#333333",
            "grid.color": "#444444"
        })
        # streamlit CSS for dark theme
        st.markdown(
            """
            <style>
            .stApp { background-color: #111111; color: #EEE; }
            .stSidebar { background-color: #121212; color: #EEE; }
            .css-1d391kg { background-color: #121212; } /* input bg - may vary by Streamlit version */
            </style>
            """, unsafe_allow_html=True
        )
    else:
        # revert to light
        mt.rcParams.update({
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.labelcolor": "black",
            "xtick.color": "black",
            "ytick.color": "black",
            "text.color": "black",
            "legend.facecolor": "#FFFFFF",
            "grid.color": "#DDDDDD"
        })

       # full CSS reset to override .toml dark theme
        st.markdown(
            """
            <style>
            /* Reset global colors that .toml applies */
            html, body, .stApp, [class^="st-"], [class*=" st-"] {
                background-color: white !important;
                color: black !important;
            }

            /* Sidebar */
            .stSidebar {
                background-color: #F8F8F8 !important;
                color: black !important;
            }

            /* Inputs */
            input, textarea, select, button,
            .stTextInput input, .stNumberInput input,
            .stTextArea textarea {
                background-color: white !important;
                color: black !important;
            }

            /* Optional recovery for dark-mode widget classes */
            .css-1d391kg {
                background-color: white !important;
                color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# Apply chosen theme
apply_theme(theme_choice)

# Create empty dictionary to store all variables
data_dict = {}

if csv_df is not None:
    st.sidebar.markdown("### Dataset Preview")
    st.sidebar.dataframe(csv_df.head())

    # Add each sensor column as its own dataset, skip time and Location_Note
    for col in csv_df.columns:
        if col not in ["Time (s)", "Location_Note"]:
            df_var = csv_df[["Time (s)", col]].copy()
            data_dict[col] = df_var

    # Build Overview dataset
    numeric_cols = [col for col in csv_df.columns if col not in ["Time (s)", "Location_Note"]]
    overview_df = csv_df[["Time (s)"] + numeric_cols].copy()
    data_dict["Overview"] = overview_df

else:
    st.warning("Upload a CSV to load variables.")
    st.stop()


# Sidebar selector
st.sidebar.header("Controls")

options_list = list(data_dict.keys())   # includes "Overview"
option = st.sidebar.selectbox("Select a variable", options_list, key="variable_selector")

st.write(f"Data for: {option}")

selected_data = data_dict[option]

# Overview has multiple y columns
if option == "Overview":
    y_col = None
else:
    y_col = selected_data.columns[1]

# Default cleaned data
df_clean = selected_data.copy()

#Sidebar variable selector

if len(data_dict) == 0:
    st.sidebar.warning("Upload a CSV file to display variables.")
    st.stop()   # Stops app from crashing before CSV upload

# Sidebar selector
st.write(f"Data for: {option}")
# Overview mode has MANY columns, so it cannot have a single y_col
if option == "Overview":
    y_col = None
else:
    y_col = selected_data.columns[1]  # second column = chosen sensor variable

# Default cleaned data (will be overwritten in cleaning tab)
df_clean = selected_data.copy()


# Thresholds for normal variables
thresholds = {
    "CO2_ppm": (600, 1200),              # typical indoor CO2 thresholds
    "VOC_ppm": (0, 5),                   # depends on sensor scale - adjust if needed
    "Temp_Comp_C": (18, 26),             # typical comfortable room temp
    "Hum_Comp_pct": (30, 60),            # ideal indoor humidity
    "IAQ": (50, 150),                    # but see IAQ thresholds in IAQ table
}
# IAQ thresholds corresponding to IAQ Reference Table
iaq_thresholds =  (50, 100, 150, 200, 250, 300, 1000)

#
# Adding tabs
#

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Table", "Chart", "Statistics", "Literature Values", "Data Cleaning", "Download data"])

with tab1: 
    st.subheader(f"{option} Table")
    st.dataframe(selected_data)

with tab2:
    st.subheader(f"{option} over Time Chart")
    fig, ax = plt.subplots()

    if option == "Overview":
        # Plot all numeric variables
        for col in selected_data.columns[1:]:
            ax.plot(selected_data["Time (s)"], selected_data[col], label=col, markersize=2)
        ax.legend()

    else:
        # Plot single variable
        ax.plot(selected_data["Time (s)"], selected_data[y_col], marker='o', markersize=3)
    #
    # Anomaly detection on graph
    #

    if option != "Overview":
        for i, row in selected_data.iterrows():
            val = row[y_col]
            time = row["Time (s)"]

            if option in thresholds:
                low, high = thresholds[option]
                if val < low or val > high:
                    ax.plot(time, val, marker='o', markersize=2, linestyle='None', color='#9D00FF')
            if option == "IAQ":
                if val > iaq_thresholds[-1]:
                    ax.plot(time, val, marker='o', markersize=2, linestyle='None', color='#9D00FF')

    #
    #
    #


    # labels formatting 
    ax.set_xlabel("Time (s)", weight = 'bold', size = 15)
    ax.set_ylabel("Values" if option == "Overview" else y_col, weight = 'bold', size = 15)

#
# Dynmic threshold slider based on actual y range (inside tab 2)
#

    def is_numeric(series):
        return pd.api.types.is_numeric_dtype(series)

    if option != "Overview" and is_numeric(selected_data[y_col]):
        y_min = float(selected_data[y_col].min())
        y_max = float(selected_data[y_col].max())

        st.sidebar.subheader("Safety Threshold")
        threshold = st.sidebar.slider(
            f"{y_col} Safety Threshold",
            min_value=y_min,
            max_value=y_max,
            value=y_min + (y_max - y_min) / 2
        )

        ax.axhline(threshold, color='gray', linestyle='--', linewidth=1)

#
# Time slider (x axis) (in tab 2)
#

        st.sidebar.subheader("Time Point Control")
        time_point = st.sidebar.slider(
            "Set a time point", 
            min_value = int(selected_data["Time (s)"].min()), 
            max_value = int(selected_data["Time (s)"].max()),
            value = int(selected_data["Time (s)"].max() // 2),
            step = 1
        )

        # Draw a vertical line for the time point 
        ax.axvline(time_point, color = 'blue', linestyle = '--', linewidth = 1)

        # Get value at the selected time point
        row = selected_data[selected_data["Time (s)"] == time_point]
        if not row.empty:
            value_at_time = row.iloc[0, 1]

            if value_at_time < threshold:
                st.success(f"Value at t = {time_point}s: {value_at_time} (Good)")
            elif value_at_time < threshold + 0.25 * (y_max - y_min):
                st.warning(f"Value at t = {time_point}s: {value_at_time} (Moderate)")
            else:
                st.error(f"Value at t = {time_point}s: {value_at_time} (High)")

        else:
            st.info("Selected time has no data point.")


    st.pyplot(fig)

    
#
# Optional Comparison Mode for Data (button on the side, displayed in graph tab)
#
    st.sidebar.subheader("Comparison Mode")
    enable_comparison = st.sidebar.checkbox("Enable Comparison Mode")

    compare_variables = [] 

    if enable_comparison:
        compare_variables = st.sidebar.multiselect(
            "Select variables to compare",
            [v for v in data_dict.keys() if v != "Overview"],
            default=[option] if option != "Overview" else []
        )

        if len(compare_variables) == 0: 
            st.warning("Select at least one variable to display a comparison chart.")
        elif 'Overview' in compare_variables:
            st.warning("Overview cannot be compared with other variables. Please select other variables.")
        else: 
            st.subheader("Comparison Chart")
            fig2, ax2 = plt.subplots()
            for var in compare_variables:
                df = data_dict[var]
                y_col2 = df.columns[1]
                ax2.plot(df["Time (s)"], df[y_col2], label = var, marker = 'o', markersize = 3)

            ax2.set_xlabel("Time (s)", weight = 'bold', size = 15)
            ax2.set_ylabel("Values", weight = 'bold', size = 15)
            ax2.legend()
            st.pyplot(fig2)

#
# Displaying summary statistics 
#
with tab3: 

    if option == "Overview":
        st.info("Summary statistics not available for Overview mode.")
    else: 
        st.subheader(f"{option} Summary Statistics")
        col1, col2, col3, col4= st.columns(4)
        col1.metric("Mean", selected_data[y_col].mean())
        col2.metric("Max", selected_data[y_col].max())
        col3.metric("Min", selected_data[y_col].min())
        col4.metric("Std Dev", f"{selected_data[y_col].std():.3f}")


with tab4:
    st.subheader("IAQ Reference Table")
    IAQ_table = pd.DataFrame({
        "IAQ Index": ["0-50", "51-100", "101-150", "151-200", "201-250", "251-300", "301+"],
        "Air Quality": ["Excellent", "Good", "Lightly Polluted", "Moderately Polluted", "Heavily Polluted", "Severely Polluted", "Extremely Polluted"],
        "Impact": ["Pure air; healthy", "No irritation or impact on well-being", "Reduction of well-being possible", "More siginificant irritation possible", 
                   "Exposure might lead to effects like headac he depending on type of VOCs", "More sever health issues possible if harmful VOC present", "Headaches, additional neurotoxic effects possible"],
        "Suggested Action": ["No action required", "No action required", "Ventilation suggested", "Increase ventilation with clean air", "Optimize ventilation", 
                             "Contamination should be identified if level is reached even without presence of people; maximize ventilation", "Contamination needs to be identified; avoid presence in room and maximize ventilation"]
                            

    })

    # Defining different colours for each row
    row_colors = [
        "#66FF00",  # bright green
        "#61E160",  # green
        "#FFFF00",  # yellow
        "#FFA500",  # orange
        "#FF0000",  # red
        "#800080",  # purple
        "#A52A2A"   # brown
    ]

    def highlight_rows(row):
        idx = row.name
        return [f"background-color: {row_colors[idx]}; color: black;"] * len(row)

    styled = IAQ_table.style.apply(highlight_rows, axis=1)

    st.dataframe(styled, use_container_width=True)

    st.write("Source: https://www.sorel.de/en/indoor-air-quality-index-in-hvac-applications/, (accessed November 2025)")

    st.write("Sources for VOC and CO2 and Temp")

#
# Interactive Data CLeaning Tools
#
with tab5:
    st.subheader("Data Cleaning Options")

    # Select a variable to clean
    var = st.selectbox("Select variable to clean", [v for v in data_dict.keys() if v != "Overview"], key = "cleaning_selector")
    df = data_dict[var].copy()
    y_col2 = df.columns[1]

    #outlier removal toggle
    remove_outliers = st.checkbox("Remove Outliers")
    if remove_outliers: 
        z_scores = (df[y_col2] - df[y_col2].mean()) / df[y_col2].std()
        df_clean = df[np.abs(z_scores) < 3]
    else: 
        df_clean = df.copy()

    # smoothing graphs 
    st.subheader("Smoothing Filter")
    smoothing_method = st.selectbox("Select method", ["None", "Moving Average", "Savitzky-Golay"])

    window_size = st.slider("Window size / polynomial order", min_value = 3, max_value = 21, step = 2, value = 5)

    if smoothing_method == "Moving Average":
        df_clean[y_col2] = df_clean[y_col2].rolling(window=window_size, center=True, min_periods=1).mean()
    elif smoothing_method == "Savitzky-Golay":
        if len(df_clean[y_col2]) >= window_size:
            df_clean[y_col2] = savgol_filter(df_clean[y_col2], window_length = window_size, polyorder = 2)
        else: 
            st.warning("Window size is too large for Savitzky-Golay filter, skipping.")

    # Plot raw vs cleaned data
    st.subheader("Raw against Cleaned Data Plot")
    fig, ax = plt.subplots(figsize = (10, 5))
    ax.plot(df["Time (s)"], df[y_col2], label="Raw", marker='o', markersize=3)
    ax.plot(df_clean["Time (s)"], df_clean[y_col2], label="Cleaned", marker='o', markersize=3)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(y_col2)
    ax.legend(loc = "upper left", bbox_to_anchor = (1, 1))
    st.pyplot(fig)

    st.success("Data cleaning complete! Adjust the sliders and toggles to see the effect.")

with tab6:
    st.subheader("Download Data")
#
# Generate a PDF report (raw data, cleaned image, scaled, includes comparison graph and data summary)
#
    mt.use("Agg") 

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", "B", 16) 
    pdf.cell(0, 10, f"{option} Report", ln = True, align = 'C')

# Adding a table as text
    pdf.set_font("Times", "", 12)
    col = selected_data.columns[1]
    pdf.cell(0, 8, f"Time (s), {option}", ln = True)
    for i, row in selected_data.iterrows():
        pdf.cell(0, 5, f"{row['Time (s)']}, {row[col]}", ln = True)

# Add summary statistics 
    pdf.ln(5)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 8, "Summary Statistics", ln = True)
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 5, f"Mean: {selected_data[col].mean(): .2f}", ln = True)
    pdf.cell(0, 5, f"Max: {selected_data[col].max(): .2f}", ln = True)
    pdf.cell(0, 5, f"Min: {selected_data[col].min(): .2f}", ln = True)

# Save a plain graph to image and add to PDF
    fig_pdf, ax_pdf = plt.subplots()

    if option == 'Overview':
        for c in selected_data.columns[1:]:
            ax_pdf.plot(selected_data["Time (s)"], selected_data[c], label = c)
        ax_pdf.legend()
    else:
        ax_pdf.plot(selected_data["Time (s)"], selected_data[col], marker = 'o', markersize = 3)

    ax_pdf.set_xlabel("Time (s)", weight = 'bold', size = 15)
    ax_pdf.set_ylabel("Values" if option == "Overview" else col, weight = 'bold', size = 15)

# save chart as image
    fig_pdf.savefig("temp_plot.png", bbox_inches = 'tight')
    plt.close(fig_pdf)

# Scale the image to fit the page width 
    im = Image.open("temp_plot.png")
    img_width, img_height = im.size 
    max_width = 190
    scale = max_width / img_width 
    scaled_height = img_height * scale

# Add new page if image it too tall: 
    if scaled_height > 277: 
        pdf.add_page()
    pdf.image("temp_plot.png", x = 10, y = pdf.get_y() + 5, w = max_width, h = scaled_height)

# Includes comparison chart if it exists 
    try: 
        compare_variables
        if len(compare_variables) > 0:
            fig_comp, ax_comp = plt.subplots()
            for var in compare_variables:
                df = data_dict[var]
                y_col2 = df.columns[1]
                ax_comp.plot(df["Time (s)"], df[y_col2], label = var, marker = 'o', markersize = 3)
            ax_comp.set_xlabel("Time (s)", weight = 'bold', size = 15)
            ax_comp.set_ylabel("Values", weight = 'bold', size = 15)
            ax_comp.legend()

    # Save comparison graph 
        fig_comp.savefig("comparison_plot.png", bbox_inches = 'tight')
        plt.close(fig_comp)

    # Add comparison chart to a new page
        pdf.add_page()
        im_comp = Image.open("comparison_plot.png")
        img_width_comp, img_height_comp = im_comp.size
        scale = max_width / img_width_comp
        scaled_height_comp = img_height_comp * scale
        pdf.image("comparison_plot.png", x = 10, y = pdf.get_y(), w = max_width, h = scaled_height_comp)
    except NameError:
        pass            # if comparison mode was not used then skip

# Export PDF to BytesIO for Streamlit download
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    st.sidebar.download_button(
        label = "Download PDF Report",
        data = pdf_output,
        file_name = f"{option}_report.pdf",
        mime = "application/pdf"
    )

#
# Downloading CSV, Excel and JSON
#
# CSV
    csv_data = df_clean.to_csv(index = False).encode("utf-8")
    st.download_button(
        label = "Download Data in CSV Format",
        data=csv_data,
        file_name = f"{option}_cleaned.csv",
        mime="text/csv"
    )

# Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_clean.to_excel(writer, index = False)
    excel_buffer.seek(0)

    st.download_button(
        label = "Download Data in Excel Format",
        data = excel_buffer,
        file_name = f"{option}_cleaned.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
 
# JSON
    json_data = df_clean.to_json(orient = "records")
    st.download_button(
        label = "Download Data in JSON Format",
        data = json_data,
        file_name = f"{option}_cleaned.json",
        mime = "application/json"
    )

#
# Live Tracking Widget
#
st. sidebar.subheader("Live Tracking")

# Making containers for each variable
live_containers = {
    var: st.sidebar.empty() for var in data_dict.keys() if var != "Overview"
}

#Initialise with the latest value from your dataset 
for var, container in live_containers.items():
    df = data_dict[var]
    latest_value = df.iloc[-1, 1]
    container.metric(label = f"{var}", value = f"{latest_value}")
                     
# from a live data source#
from streamlit_autorefresh import st_autorefresh
update_interval = 2             # seconds

for _ in range(10):             # run 10 iterations to start with
    for var, container in live_containers.items():
        # Simulate new measurement
        df = data_dict[var]
        new_value = np.random.randint(df.iloc[-1, 1] - 5, df.iloc[-1, 1] + 5)
        container.metric(label=f"{var}", value=f"{new_value}")
st_autorefresh(interval=2000, limit=None, key="live_refresh_1")


# colour coding the value based on thresholds defined earlier
# IAQ thresholds corresponding to IAQ Reference Table defined earlier


#
# Real time amnomaly detection
#
def is_anomaly(var, val):
    if var in thresholds:
        low, high = thresholds[var]
        return val < low or val > high
    if var == "IAQ":
        return val > iaq_thresholds[-1]
    return False

#
#
#

# loop through live containers to update with colour coding
for var, container in live_containers.items():
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

    # compute anomaly
    anomaly = is_anomaly(var, val)
    anomaly_flag = "<div style='color:red; font-size:14px;'>Anomaly detected</div>" if anomaly else ""
   

  # Use HTML to make number big and colored + anomaly detection
    container.markdown(
        f"""
        <div style="text-align:center;">
            <div style="font-size:16px; font-weight:bold;">{var}</div>
            <div style="font-size:36px; font-weight:bold; color:{color};">{val}</div>
        </div>
        {anomaly_flag}
        """, 
        unsafe_allow_html = True
    )
