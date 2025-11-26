import streamlit as st 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

st.title("Our project")

#sidebar for choice of variable displayed 
st.sidebar.header("Controls")
option = st.sidebar.selectbox(
    "Select a variable",
    ["Air Pressure", "BSEC Temperature", "CO2 Levels", "Humidity", "IAQ", "Temperature", "Overview"]
)

st.write(f"You selected: {option}")

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

# this will only show data for the selected value 
selected_data = data_dict[option] 
y_col = selected_data.columns[1]

# we want to display the table 
st.subheader(f"{option} Table")
st.dataframe(selected_data)

# and to display a chart: 
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