import streamlit as st 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import matplotlib as mt
from PIL import Image


st.title("Our project")

#sidebar for choice of variable displayed 
st.sidebar.header("Controls")
option = st.sidebar.selectbox(
    "Select a variable",
    ["Air Pressure", "BSEC Temperature", "CO2 Levels", "Humidity", "IAQ", "Temperature", "Overview"]
)

st.write(f"Data for: {option}")

data_dict = {
    "Air Pressure": pd.DataFrame({
        "Time (s)": np.arange(100),
        "Pressure (atm)": np.random.randint(20, 100, 100)
    }),
    "BSEC Temperature": pd.DataFrame({
        "Time (s)": np.arange(100),
        "Temp (\u00b0 C)": np.random.randint(20, 100, 100)
    }),
    "CO2 Levels": pd.DataFrame({
        "Time (s)": np.arange(100),
        "CO2 (ppm)": np.random.randint(300, 600, 100)
    }),
    "Humidity": pd.DataFrame({
        "Time (s)": np.arange(100),
        "Humidity (%)": np.random.randint(20, 80, 100)
    }),
    "IAQ": pd.DataFrame({
        "Time (s)": np.arange(100),
        "IAQ": np.random.randint(0, 150, 100)
    }),
    "Temperature": pd.DataFrame({
        "Time (s)": np.arange(100),
        "Temp (\u00b0 C)": np.random.randint(20, 100, 100)
    }),
    "Overview": pd.DataFrame({
        "Time (s)": np.arange(100),
        "Pressure (atm)": np.random.randint(20, 100, 100),
        "CO2 (ppm)": np.random.randint(300, 600, 100),
        "Humidity (%)": np.random.randint(20, 80, 100),
        "IAQ (AQI)": np.random.randint(0, 150, 100),
        "Temp (\u00b0 C)": np.random.randint(20, 100, 100)
    })

}

# this will only show data for the selected value (single-variable)
selected_data = data_dict[option] 
y_col = selected_data.columns[1]

# we want to display the table 
st.subheader(f"{option} Table")
st.dataframe(selected_data)

# and to display a chart (single-variable)
st.subheader(f"{option} over Time Chart")
fig, ax = plt.subplots()

# overview mode plots
if option == 'Overview':
    for col in selected_data.columns[1:]:
        ax.plot(selected_data["Time (s)"], selected_data[col], label=col)
    ax.legend()
else:
    ax.plot(selected_data["Time (s)"], selected_data[y_col], marker = 'o', markersize = 3)

# adding axis labels
if option == 'Overview': 
    ax.set_xlabel("Time (s)", weight = 'bold', size = 15)
    ax.set_ylabel("Values", weight = 'bold', size = 15)
else: 
    ax.set_xlabel("Time (s)", weight = 'bold', size = 15) 
    ax.set_ylabel(y_col, weight = 'bold', size = 15)


#
# Dynmic threshold slider based on actual y range
#
if option != 'Overview':                        # this will prevent the sliders from appearing when the vairable chosen is Overview
    y_min = int(selected_data[y_col].min())
    y_max = int(selected_data[y_col].max())

    st.sidebar.subheader("Safety Threshold")
    threshold = st.sidebar.slider(
        f"Set {y_col} Safety Threshold", 
        min_value = y_min, 
        max_value = y_max,
        value = y_min + (y_max - y_min) // 2,
        step = 1
)

    # Draw a horizontal line for the threshold
    ax.axhline(threshold, color = 'gray', linestyle = '--', linewidth = 1)


#
# Time slider (x axis)
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

    # Safety classification based on the threshold at the time point
        if value_at_time < threshold:
            st.success(f"Value at t = {time_point}s: {value_at_time} (Good)")
        elif value_at_time < (threshold + (0.25 * (y_max - y_min))):
            st.warning(f"Value at t = {time_point}s: {value_at_time} (Moderate)")
        else:
            st.error(f"Value at t = {time_point}s: {value_at_time} (High)")
    else:
        st.info("Selected time has no data point.")


st.pyplot(fig)


#
# Displaying summary statistics 
#
st.subheader(f"{option} Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Mean", selected_data[y_col].mean())
col2.metric("Max", selected_data[y_col].max())
col3.metric("Min", selected_data[y_col].min())


#
# Optional Comparison Mode for Data
#
st.sidebar.subheader("Comparison Mode")
enable_comparison = st.sidebar.checkbox("Enable Comparison Mode")

if enable_comparison:
    compare_variables = st.sidebar.multiselect(
    "Select variables to compare", 
    ["Air Pressure", "BSEC Temperature", "CO2 Levels", "Humidity", "IAQ", "Temperature", "Overview"],
    default = [option]
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
# Generate a PDF report
#
st.subheader("Generate PDF Report") 
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
