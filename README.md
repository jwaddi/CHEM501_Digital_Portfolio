# CHEM501_Digital_Portfolio

# Project Overview

The Stuffy Study investigates the ventilation and learning environment in student study spaces using real-time environmental sensing and interactive data visualisation.

This repository contains:

* SOMETHING ABOUT DATA COLLECTION

* SOMETHING ABOUT DATA COLLECTION #2

* a Streamlit dashboard for data exploration, cleaning, visualisation, and reporting

* a modular Python architecture separating data handling, plotting, theming, reporting, and reference information

* support for live sensor data, uploaded CSV datasets, and simulated fallback data

The dashboard is designed to be robust, reproducible, and extendable, following best practice in scientific data workflows.

# Required Libraries
This project utilises a number of external as well as built-in libraries. Please read through the following and ensure that they are installed on your device to be able to run the code packages. 

### For data aquisiton: 
1. ssssss
```python
pip install ssssssss
```
2. kkkkkkkkkkkkk
```python
pip install kkkkkkkkkkkk
```
3. zzzzzzzzzzzzz
```python
pip install zzzzzzzz
```

### For running data visualisation:

1. Pandas - Used for loading, cleaning, manipulating, and analysing tabular sensor data (CSV files).
```python
pip install pandas
```
3. Matplotlib - Used for generating time-series plots, comparison charts, and cleaned versus raw data visualisations.
```python
pip install matplotlib
```
4. streamlit - The core framework used to build the interactive dashboard interface, including tabs, sliders, and live updates.
```python
pip install streamlit
```
4. numpy - Provides numerical operations used for calculations, simulations, and data processing.
```python
pip install numpy
```
5. scipy - Required for signal processing functions such as Savitzky–Golay smoothing.
```python
pip install scipy
```
6. fpdf - Used to generate downloadable PDF reports directly from the dashboard.
```python
pip install fpdf
```
7. Pillow (PIL) - Handles image processing when embedding plots into PDF reports.
```python
pip install pillow
```
8. streamlit-autorefresh - Enables automatic dashboard refresh when monitoring live sensor data from a continuously updating CSV file.
```python
pip install streamlit-autorefresh
```


# Data Aquisition
Data: 
To view Stuffy_Study_Master.db please download the DB browser for SQLite. 



### Database files 
To view the master database file: 
* File name: `Stuffy_Study_Master.db`
* Recommended tool: DB Browser for SQLite

This database contains all recorded sensor data across sessions. 


# Streamlit Dashboard
This repository contains a modular Streamlit dashboard development for **The Stuffy Study**. 

The dashboard allows user to visualise, analyse, clean and export environmental sensor data collected from student study spaces.

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

2. Launch the Streamlit app. 

```bash
streamlit run "dashboard.py"
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
December 2025
