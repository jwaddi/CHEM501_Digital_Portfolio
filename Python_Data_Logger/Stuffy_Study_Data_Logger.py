"""
Project: THE STUFFY STUDY (CHEM501)
Experiment: An Investigation into the Ventilation and Learning Environment in Student Study Spaces
Module: Python Data Acquisition Monitor | Role: Real-Time Monitor, CSV Logger & SQL Database
Description:
    This script acts as the main receiver for the wireless sensor system.
    It connects to the project's cloud data stream, buffers incoming sensor readings
    from the MKR WiFi 1010, displays live metrics to the console, and persists 
    the full dataset to both a session-specific CSV file and a cumulative master SQLite database.
    Session metadata (Start Time, Location) is stored efficiently in headers and 
    tables, not repeated on every row. It also maintains a master 'Data Catalog' log.
System Requirements:
    1. NETWORK: Active internet connection (Mobile Hotspot recommended)
    2. ACCESS: An active MQTT server to receive the data stream.
Authors: Josh and Kinga
Date: November 2025
License: MIT
"""

import paho.mqtt.client as mqtt
import csv
import os
import sqlite3 
from datetime import datetime

# SYSTEM CONFIGURATION

# Server address for the project's dedicated cloud instance (Cedalo).
MQTT_SERVER = "pf-uyp85ksb0tbt7jocc1qo.cedalo.cloud" 
MQTT_PORT = 1883

# Topic hierarchy matches the structure defined in the Arduino firmware.
TOPIC_BASE = "chem501/josh_kinga/stuffy_study"

# Capture precise start time once at the beginning of the session.
SESSION_START_DT = datetime.now()
SESSION_START_STR = SESSION_START_DT.strftime('%Y-%m-%d %H:%M:%S')
FILE_DATE_STR = SESSION_START_DT.strftime('%Y-%m-%d_%H-%M-%S')

# Dynamic Filenames: CSV is unique per session. DB is a single master file.
CSV_FILENAME = f"Stuffy_Study_{FILE_DATE_STR}.csv"
DB_FILENAME = "Stuffy_Study_Master.db"
CATALOG_FILENAME = "_Experiment_Data_Catalog.csv"

class StudySpaceLogger:
    """
    Manages the network interface, data aggregation, and structured logging.
    Ensures asynchronous MQTT payloads are synchronised into coherent 
    time-series data points using a sequential counter before display and storage.
    """
    
    def __init__(self):
        # Client initialised with CallbackAPIVersion.VERSION2 to ensure 
        # compatibility with modern paho-mqtt library standards.
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        # Bind event handlers
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Temporary buffer for assembling fragmented sensor packets
        self.current_reading = {}
        # Internal sequential counter for elapsed session seconds
        self.elapsed_seconds = 0
        
        # SESSION SETUP (Blocking Input)
        print("\n========================================")
        print("      THE STUFFY STUDY: DATA LOGGER      ")
        print(f"   Session Start: {SESSION_START_STR}")
        print("========================================")
        user_input = input("ENTER LOCATION NAME (e.g. 'POD_1'): ")
        
        if user_input.strip() == "":
            self.location_label = "Unspecified"
        else:
            self.location_label = user_input.strip()
            
        print("----------------------------------------")
        print(f"LOCATION SET: {self.location_label}")
        print(f"LOGGING CSV: {CSV_FILENAME}")
        print(f"MASTER DB:   {DB_FILENAME}")
        print("----------------------------------------\n")
        
        # Initialise Storage Systems
        self.init_csv()
        self.init_db()
        self.update_catalog()

    def init_csv(self):
        """Creates the new CSV log file and writes session metadata headers."""
        if not os.path.exists(CSV_FILENAME):
            with open(CSV_FILENAME, mode='w', newline='') as f:
                writer = csv.writer(f)
                # Write metadata header
                writer.writerow(["# SESSION METADATA"])
                writer.writerow(["# Start Time", SESSION_START_STR])
                writer.writerow(["# Location", self.location_label])
                writer.writerow([]) # Blank line for readability before data table
                
                # Write data table header
                writer.writerow([
                    "Elapsed_Seconds", "Location_Note",
                    "CO2_ppm", "VOC_ppm", "IAQ", "Gas_Res_Ohms", 
                    "Temp_Raw_C", "Temp_Comp_C", "Hum_Raw_pct", "Hum_Comp_pct", "Accuracy"
                ])

    def init_db(self):
        """Connects to the master SQLite database and ensures tables exist."""
        # Connects to existing file or creates it if it's the first run ever.
        self.conn = sqlite3.connect(DB_FILENAME)
        self.cursor = self.conn.cursor()
        
        # 1. Metadata Table: Stores single-entry session details
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_metadata (
                start_time TEXT,
                location TEXT
            )
        ''')
        # Append this new session's details to the metadata table
        self.cursor.execute('INSERT INTO session_metadata VALUES (?, ?)', 
                            (SESSION_START_STR, self.location_label))
        
        # 2. Sensor Data Table: Optimised schema for time-series data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                elapsed_seconds INTEGER,
                location_note TEXT,
                co2_ppm INTEGER,
                voc_ppm REAL,
                iaq INTEGER,
                gas_res_ohms INTEGER,
                temp_raw_c REAL,
                temp_comp_c REAL,
                hum_raw_pct REAL,
                hum_comp_pct REAL,
                accuracy INTEGER
            )
        ''')
        self.conn.commit()

    def update_catalog(self):
        """Appends this session's metadata to the Master Data Catalog file."""
        file_exists = os.path.exists(CATALOG_FILENAME)
        
        with open(CATALOG_FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
            # Write header only if file is new
            if not file_exists:
                writer.writerow(["Session_Start_Time", "Location", "CSV_Filename", "Master_Database"])
            
            # Write the session log entry
            writer.writerow([
                SESSION_START_STR,
                self.location_label,
                CSV_FILENAME,
                DB_FILENAME
            ])

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Event handler for connection acknowledgement from the server."""
        if rc == 0:
            print(f"STATUS: Connected to Server: {MQTT_SERVER}")
            
            # Subscribe to the project wildcard topic to capture all sensor streams
            full_topic = f"{TOPIC_BASE}/#"
            client.subscribe(full_topic)
            print(f"STATUS: Listening on topic tree: {full_topic}")
        else:
            print(f"ERROR: Connection failed. Return Code: {rc}")

    def on_message(self, client, userdata, msg):
        """
        Event handler for incoming telemetry.
        Buffers data until the 'accuracy' metric is received, which serves as the 
        synchronisation trigger for the current second's data point.
        """
        try:
            # 1. Extract metric type from the topic suffix (e.g., .../co2)
            metric = msg.topic.split("/")[-1]
            value = float(msg.payload.decode('utf-8'))
            
            # 2. Update buffer with the received value
            self.current_reading[metric] = value
            
            # 3. Synchronisation Trigger (Resilient Logic)
            # The Arduino sends 'accuracy' last in its cycle. Use receipt of this
            # metric to trigger the save operation for the current second.
            if metric == 'accuracy':
                self.save_and_display()

        except Exception as e:
            print(f"ERROR: Parsing payload failed: {e}")

    def save_and_display(self):
        """Writes the buffered dataset to CSV, SQL, and renders to console."""
        
        # 1. Define timebase for this row using internal sequential counter
        current_time_seq = self.elapsed_seconds
        
        # 2. Data Extraction from Buffer
        # Defaulting to 0 ensures log integrity if specific packets are lost in transit
        co2 = int(self.current_reading.get('co2', 0))
        voc = self.current_reading.get('voc', 0)
        iaq = int(self.current_reading.get('iaq', 0))
        gas = int(self.current_reading.get('gas_raw', 0))
        
        # Physical Sensors
        t_raw = self.current_reading.get('temp_raw', 0)
        t_comp = self.current_reading.get('comp_t', 0)
        h_raw = self.current_reading.get('hum_raw', 0)
        h_comp = self.current_reading.get('hum_comp', 0)
        
        acc = int(self.current_reading.get('accuracy', 0))
        
        # Use the fixed location label set at startup
        location_note = self.location_label

        # 3. Save to CSV Row (Unique file per session)
        with open(CSV_FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                current_time_seq, location_note, 
                co2, voc, iaq, gas, 
                t_raw, t_comp, h_raw, h_comp, acc
            ])

        # 4. Save to SQL DB Row (Appends to the master database)
        self.cursor.execute('''
            INSERT INTO sensor_data (
                elapsed_seconds, location_note,
                co2_ppm, voc_ppm, iaq, gas_res_ohms,
                temp_raw_c, temp_comp_c, hum_raw_pct, hum_comp_pct, accuracy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_time_seq, location_note, co2, voc, iaq, gas, t_raw, t_comp, h_raw, h_comp, acc))
        self.conn.commit()

        # 5. Console Output & Counter Increment
        print(f"T={current_time_seq}s | CO2: {co2} ppm | IAQ: {iaq} | Acc: {acc} | SQL: Saved")
        
        # Reset buffer and advance time counter for the next sampling interval
        self.current_reading = {}
        self.elapsed_seconds += 1

    def start(self):
        """Establishes the connection and begins the blocking listening loop."""
        print(f"STATUS: Connecting to {MQTT_SERVER}...")
        
        try:
            self.client.connect(MQTT_SERVER, MQTT_PORT, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
        except KeyboardInterrupt:
            print("\nSTATUS: Monitor Stopped by User.")
            self.conn.close() # Ensure clean database closure

# MAIN EXECUTION BLOCK

if __name__ == "__main__":
    # Initialise acquisition engine
    logger = StudySpaceLogger()
    
    # Begin monitoring
    logger.start()
