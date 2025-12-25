# CHEM501_Digital_Portfolio

# Project Overview

The Stuffy Study investigates the ventilation and learning environment in student study spaces using real-time environmental sensing and interactive data visualisation.

This repository contains:

* arduino code for data aquisition, including wireless transmission using mqtt

* python architecture, which connects the project's cloud data stream, buffer incoming sensor readings from the MKR WiFi 1010, displays live metrics to the console and persists the full dataset to both a session-specific CSV file and a master SQL database. 

* a Streamlit dashboard for data exploration, cleaning, visualisation, and reporting

* a modular Python architecture separating data handling, plotting, theming, reporting, and reference information

* support for live sensor data, uploaded CSV datasets, and simulated fallback data

The dashboard is designed to be robust, reproducible, and extendable, following best practice in scientific data workflows.

# Required Libraries
This project utilises a number of external as well as built-in libraries. Please read through the following and ensure that they are installed on your device to be able to run the code packages. 

### For data acquisition (Python & Hardware):

1. **Built-in Python Modules**
The following libraries are included with Python by default and do not require separate installation:
* `csv`
* `os`
* `sqlite3`
* `datetime`

2. **External Python Packages**
The Python data logger requires the Paho MQTT client to receive wireless sensor data. Install it using:
```bash
pip install paho-mqtt
```
4. **Arduino Libraries**
To compile and upload the firmware to the microcontrollers, the following libraries must be installed via the Arduino IDE Library Manager:
* `Arduino_BHY2` Required for the Nicla Sense ME
* `WiFiNINA` Required for the MKR WiFi 1010
* `ArduinoMqttClient` Required for MQTT wireless transmission


### For running data visualisation:

1. Pandas - Used for loading, cleaning, manipulating, and analysing tabular sensor data (CSV files).
```bash
pip install pandas
```
3. Matplotlib - Used for generating time-series plots, comparison charts, and cleaned versus raw data visualisations.
```bash
pip install matplotlib
```
4. streamlit - The core framework used to build the interactive dashboard interface, including tabs, sliders, and live updates.
```bash
pip install streamlit
```
4. numpy - Provides numerical operations used for calculations, simulations, and data processing.
```bash
pip install numpy
```
5. scipy - Required for signal processing functions such as Savitzky–Golay smoothing.
```bash
pip install scipy
```
6. fpdf - Used to generate downloadable PDF reports directly from the dashboard.
```bash
pip install fpdf
```
7. Pillow (PIL) - Handles image processing when embedding plots into PDF reports.
```bash
pip install pillow
```
8. streamlit-autorefresh - Enables automatic dashboard refresh when monitoring live sensor data from a continuously updating CSV file.
```bash
pip install streamlit-autorefresh
```
9. openpyxl - Required for exporting cleaned data to Excel (.xlsx) format.
```bash
pip install openpyxl
```


# Data Acquisition & System Design

The project utilises two microcontrollers to handle separate tasks: high-frequency environmental sensing and wireless data transmission.

### 1. Hardware Communication 
* Sensing Node: An Arduino Nicla Sense ME captures raw environmental data via the Bosch BME688 AI-integrated sensor.
* Connectivity Gateway: Data is transmitted to an Arduino MKR WiFi 1010 via the ESLOV (I2C) interface.
* Sampling Rate: Firmware is configured to sample at 1Hz, providing high-resolution detail to capture rapid changes in indoor air quality.

### 2. Data Flow & Storage
The MKR WiFi 1010 acts as an MQTT client, sending data payloads to the server. A background Python logger monitors to these streams and saves the data in two ways:
* Session Logging: Data is added to a session-specific .csv file for immediate processing and visualisation by the Streamlit dashboard.
* Master Archiving: Records are simultaneously committed to a Master SQL Database ('Stuffy_Study_Master.db'). This ensures data is safely stored and allows for more efficient historical querying compared to flat text files.

### 3. Database Management & Data Retrieval
To inspect the historical archives, it is recommended to use DB Browser for SQLite.

* File Name: Stuffy_Study_Master.db
* Viewing Tables: Navigate to the Browse Data tab and select the desired table from the drop-down menu.
* Database Structure: Use the Database Structure tab for a general overview of the table schemas.
* Finding Specific Data: 
    * To find a specific location, time, or sensor value, use Ctrl+F (or Cmd+F on macOS) within the Browse Data tab.
    * For more advanced searches, click the binoculars icon to open the filter menu. This allows you to type in specific values to isolate data points from particular experimental sessions or environmental conditions.
 
### 4. Setup and Usage
Follow these steps to configure the hardware and start the logging process:

* **Configure Credentials**: Open `arduino_secrets.h` and enter your WiFi and MQTT broker details. These credentials are required for the MKR WiFi 1010 to connect to the network.
* **Upload Firmware**: Use the Arduino IDE to upload `Nicla_Sense_ME_Sensor_Reader.ino` to the Arduino Nicla Sense ME and `MKR_WiFi_Data_Transmitter.ino` to the Arduino MKR WiFi 1010.
* **Start Data Logging**: Once the boards are connected and powered, run the `Stuffy_Study_Data_Logger.py` script to begin recording data to the dashboard files.

# Streamlit Dashboard
This repository contains a modular Streamlit dashboard development for **The Stuffy Study**. 

The dashboard allows the user to visualise, analyse, clean and export environmental sensor data collected from student study spaces.

## Module Overview 
The Streamlit dashboard is organised into multiple Python modules to improve readability and maintainability of the code. Each module is responsible for a specific part of the dashboard functionality and they are all collated and called in the main `dashboard.py` file. 

`dashboard.py`
This is the main entry point for the application.
* It orchastrates all the modules and renders the Streamlit interface.
* It handles sidebar controls, tab layout and user interaction.
* It connects data loading, plotting, statistics, live tracking and reporting into a single dashboard.
* Should be run using `streamlit run dashboard.py` (see notes below in `Starting the Dashboard`).

`data_utils.py`
Handles all data-related operations. 
* Loads and standardises CSV files produced by the data acquisition system.
* Builds the `data_dict` structure used throughout the dashboard.
* Provides simulated data when no CSV is available.
* Defines thresholds and IAQ reference limits.
* Implements anomaly detection logic.
* Contains data cleaning and smoothing functions such as:
  * Outlier removal.
  * Moving average smoothing.
  * Savitzky–Golay filtering.
* Includes utilities for reading a growing live CSV file.

`plot_utils.py`
Responsible for all visualisation. 
* Generates time-series plots for individual variables.
* Supports overview plots with multiple variables.
* Adds anomaly markers and threshold lines to graphs.
* Handles comparison plots for multiple variables.
* Produces raw vs cleaned data comparison figures.
* Keeps all Matplotlib logic separate from Streamlit layout code.

`theme_toggle.py`
Manages visual styling and themes.
* Provides a sidebar theme selector (Light / Dark).
* Applies Matplotlib styling to match the selected theme.
* Injects custom CSS to override Streamlit defaults when required.
* Works alongside the `config.toml` file for consistent appearance.

`data_reports.py`
Handles all data export and reporting functionality.
* Generates downloadable PDF reports containing:
  * Data tables.
  * Summary statistics.
  * Graphs and comparison plots.
* Provides CSV, Excel, and JSON export options.
* Uses `FPDF` and temporary images to format reports cleanly.
* Keeps reporting logic separate from the dashboard UI.

`live_tracking.py`
Implements real-time data visualisation logic.
* Reads the latest values from a live CSV data source.
* Updates sidebar metrics automatically.
* Applies colour coding based on thresholds and IAQ levels.
* Displays anomaly warnings for out-of-range values.
* Designed to support future direct MQTT integration.

`stats_util.py`
Provides statistical calculations and summaries.
* Computes mean, minimum, maximum, and standard deviation.
* Centralises statistics logic used in the dashboard tabs.
* Ensures consistent calculations across visualisations and reports.

`reference_tables.py`
Contains reference and literature data tables.
* Makes the IAQ reference table with colour-coded rows.
* Displays qualitative air quality categories and recommended actions.
* Keeps static reference content separate from dynamic data logic.

`.streamlit/config.toml`
Defines global Streamlit configuration.
* Controls default theme settings (colours, fonts, background).  
* Ensures consistent appearance across devices and deployments.
* Must be placed inside a `.streamlit` folder in the main folder of the project (see below).

## Running the Dashboard 

Ensure that the required Python libraries are installed before running the dashboard (see above).

### Starting the Dashboard

1. Navigate to the directory containing `dashboard.py`.

You can do so by selecting Copy Relative Path on the dashboard file and removing the filename from the end

```bash
cd "Your path directory"
```

2. Launch the Streamlit app with either: 

```bash
streamlit run "dashboard.py"
```
or 
```bash
python -m streamlit run Dashboard_App/dashboard.py
```

This will take you to a localhost:8501 link where you can open your dashboard. If this doesn't open you can try to manually type in: 

```arduino
http://localhost:8501
```

### Configuration file
Streamlit theme settings are controlled using a config.toml file as well as the theme_toggle file. 
To ensure the theme loads correctly: 
* Create a folder names `.streamlit` in the main folder
* Place the `config.toml` file within this folder
* The `.streamlist` folder must be in the same directory as `dashboard.py`


### Data Input 
The dashboard supports: 
* CSV file upload (in the sidebar).
* Local CSV path loading (developer mode).
* Simulated data fallback if no file is provided.

Uploaded CSV files are automatically standardised and split into individual sensor datasets for visualisation. 

## Common Issues 
### Dashboard does not start 
* Ensure you are running `streamlit run dashboard.py` from the correct directory.
* Check that all required Python packages are installed.

### ModuleNotFoundError: No module named 'streamlit'
* Go to Anaconda Prompt
* Activate the enviornment by writing in
 ```bash
 conda activate streamlitenv
```
* Install packages written above or copy-paste the following:
 ```bash
pip install streamlit pandas numpy matplotlib scipy fpdf openpyxl pillow streamlit-autorefresh
```
* Run the dashboard:
```bash
cd path\to\CHEM501_Digital_Portfolio\streamlit
streamlit run dashboard.py
```

or  with 
```bash
-m streamlit run dashboard.py
```

### Theme not applying correctly 
* Confirm `config.toml` is inside `.streamlit` folder.
* Ensure the folder name is exactly `.streamlit`, which includes the dot.

### No data is visible 
* Upload a CSV file using the sidebar
* Enable simulated data fallback if nothing else works. 

## Development Notes

* All visualisation logic is isolated in plot_utils.py
* All data logic is isolated in data_utils.py
* The dashboard script acts only as an orchestrator
* Modules can be extended independently without breaking the app


# Authors 
### K. A. Dabrowska and J. Waddington 

CHEM501 Digital Chemistry

University of Liverpool

Licence: MIT

December 2025
