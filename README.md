# CHEM501_Digital_Portfolio


A good README should include a brief overview section with a paragraph or two explaining what the software does, how it works, and who made it.

# Project Overview

The Stuffy Study investigates the ventilation and learning environment in student study spaces using real-time environmental sensing and interactive data visualisation.

This repository contains:

* SOMETHING ABOUT DATA COLLECTION

* SOMETHING ABOUT DATA COLLECTION #2

* a Streamlit dashboard for data exploration, cleaning, visualisation, and reporting

* a modular Python architecture separating data handling, plotting, theming, reporting, and reference information

* support for live sensor data, uploaded CSV datasets, and simulated fallback data

The dashboard is designed to be robust, reproducible, and extendable, following best practice in scientific data workflows.




# Streamlit Dashboard

## Common Issues

1. Ensure you are running your dashboard code in the correct file directory

You can do this by selecting 'Copy Relative Path' of the dashboard file and deleting the file from the end.

'''bash
cd "Your path directory"
'''

Followed by 

streamlit run "dashboard.py"

This will take you to a localhost:8501 link where you can open your dashboard. 

2. When downloaded, ensure the config.toml file is in a separate folder named '.steamlit' in the same directory as the dashboard. 



Data: 
To view Stuffy_Study_Master.db please download the DB browser for SQLite. 


## Development Notes

* All visualisation logic is isolated in plot_utils.py

* All data logic is isolated in data_utils.py

* The dashboard script acts only as an orchestrator

* Modules can be extended independently without breaking the app


# Required Libraries
This project uses a number of external libraries. Please read through the following and ensure that they are installed on your device to be able to run the code packages. 

### For data aquisiton: 
1. ssssss

     pip install ssssssss

2. kkkkkkkkkkkkk

     pip install kkkkkkkkkkkk

3. zzzzzzzzzzzzz

     pip install zzzzzzzz


### For running data visualisation:

1. Pandas - Used for loading, cleaning, manipulating, and analysing tabular sensor data (CSV files).
'''python
pip install pandas
'''
3. Matplotlib - Used for generating time-series plots, comparison charts, and cleaned versus raw data visualisations.

     pip install matplotlib
   
4. streamlit - The core framework used to build the interactive dashboard interface, including tabs, sliders, and live updates.

pip install streamlit

4. numpy - Provides numerical operations used for calculations, simulations, and data processing.

     pip install numpy

5. scipy - Required for signal processing functions such as Savitzky–Golay smoothing.

     pip install scipy

6. fpdf - Used to generate downloadable PDF reports directly from the dashboard.

     pip install fpdf

7. Pillow (PIL) - Handles image processing when embedding plots into PDF reports.

     pip install pillow

8. streamlit-autorefresh - Enables automatic dashboard refresh when monitoring live sensor data from a continuously updating CSV file.

     pip install streamlit-autorefresh

# Academic Context 
* Idk point one
* Point Two
* Point THree
* Point Four
* <3

# Authors 
### J. Waddington and K. A. Dabrowska 
CHEM501 Digital Chemistry
University of Liverpool
December 2025
