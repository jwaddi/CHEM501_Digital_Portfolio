"""
Project: THE STUFFY STUDY (CHEM501)
Experiment: An Investigation into the Ventilation and Learning Environment in Student Study Spaces
Module: Python Data Acquisition Monitor | Role: Real-Time Monitor, CSV Logger & SQL Database
Description:
	This script acts as the main receiver for the wireless sensor system.
	It connects to the project's cloud data stream, buffers incoming sensor readings
	from the MKR WiFi 1010, displays live metrics to the console, and persists 
	the full dataset to both a timestamped CSV file and an SQLite database.
	It also maintains a master 'Data Catalog' log to track all session files in one place.
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
# Note: External replication requires updating this to a valid MQTT server URL.
MQTT_SERVER = "test.mosquitto.org" 
MQTT_PORT = 1883

# Topic hierarchy matches the structure defined in the Arduino firmware.
TOPIC_BASE = "chem501/josh_kinga/stuffy_study"

# Dynamic Filenames: Ensures every session is uniquely identifiable.
start_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
CSV_FILENAME = f"Stuffy_Study_{start_str}.csv"
DB_FILENAME = "Stuffy_Study_Master.db" 
CATALOG_FILENAME = "_Experiment_Data_Catalog.csv" # The Master Registry

class StudySpaceLogger:
	"""
	Manages the network interface, data aggregation, and dual-format logging.
	Ensures asynchronous MQTT payloads are synchronised into coherent 
	time-series data points before display and storage in CSV and SQL formats.
	"""
	
	def __init__(self):
		self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
		
		# Bind event handlers
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		
		# Temporary buffer for assembling fragmented sensor packets
		self.current_reading = {}
		self.reading_counter = 0
		
		# SESSION SETUP (Blocking Input)
		print("\n========================================")
		print("      THE STUFFY STUDY: DATA LOGGER      ")
		print("========================================")
		user_input = input("ENTER LOCATION NAME (e.g. 'POD_1'): ")
		
		if user_input.strip() == "":
			self.location_label = "Unspecified"
		else:
			self.location_label = user_input.strip()
			
		print("----------------------------------------")
		print(f"LOCATION SET: {self.location_label}")
		print(f"SESSION START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		print(f"LOGGING CSV: {CSV_FILENAME}")
		print(f"LOGGING SQL: {DB_FILENAME}")
		print(f"UPDATING CATALOG: {CATALOG_FILENAME}")
		print("----------------------------------------\n")
		
		# Initialize Storage Systems
		self.init_csv()
		self.init_db()
		self.update_catalog()

	def init_csv(self):
		"""Creates the new CSV log file and writes the standard header row."""
		if not os.path.exists(CSV_FILENAME):
			with open(CSV_FILENAME, mode='w', newline='') as f:
				writer = csv.writer(f)
				# Column structure includes all Raw and Compensated metrics
				writer.writerow([
					"Real_Time", "Time_ms", "Location_Note",
					"CO2", "VOC", "IAQ", "Gas_Res", 
					"Temp_Raw", "Temp_Comp", "Hum_Raw", "Hum_Comp", "Accuracy"
				])

	def init_db(self):
		"""Creates the SQLite database and the master table schema if required."""
		self.conn = sqlite3.connect(DB_FILENAME)
		self.cursor = self.conn.cursor()
		
		# Schema definition matches the CSV structure
		self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS sensor_data (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				timestamp_str TEXT,
				time_ms INTEGER,
				location_note TEXT,
				co2 REAL,
				voc REAL,
				iaq INTEGER,
				gas_res INTEGER,
				temp_raw REAL,
				temp_comp REAL,
				hum_raw REAL,
				hum_comp REAL,
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
				writer.writerow(["Session_Start_Time", "Location", "CSV_Filename", "SQL_Database"])
			
			# Write the session log entry
			writer.writerow([
				datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
		Logic: Packets arrive asynchronously on separate topics. They are buffered 
		until the 'accuracy' metric is received, which serves as the 
		end-of-transmission flag for the current second.
		"""
		try:
			# 1. Extract metric type from the topic suffix (e.g., .../co2)
			metric = msg.topic.split("/")[-1]
			value = float(msg.payload.decode('utf-8'))
			
			# 2. Update buffer with the received value
			self.current_reading[metric] = value
			
			# 3. Check for synchronization trigger (Accuracy metric)
			if metric == "accuracy":
				self.save_and_display()

		except Exception as e:
			print(f"ERROR: Parsing payload failed: {e}")

	def save_and_display(self):
		"""Writes the buffered dataset to CSV, SQL, and renders to console."""
		
		# 1. Timestamp Generation
		real_time = datetime.now().strftime('%H:%M:%S')
		full_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		
		# 2. Data Extraction
		# Defaulting to 0 ensures log integrity if specific packets are lost in transit
		millis = self.current_reading.get('time_ms', 0)
		co2 = self.current_reading.get('co2', 0)
		voc = self.current_reading.get('voc', 0)
		iaq = self.current_reading.get('iaq', 0)
		gas = self.current_reading.get('gas_raw', 0)
		
		# Physical Sensors
		t_raw = self.current_reading.get('temp_raw', 0)
		t_comp = self.current_reading.get('comp_t', 0)
		h_raw = self.current_reading.get('hum_raw', 0)
		h_comp = self.current_reading.get('hum_comp', 0)
		
		acc = self.current_reading.get('accuracy', 0)
		
		# Use the fixed location label set at startup
		location_note = self.location_label

		# 3. Save to CSV (Session File)
		with open(CSV_FILENAME, mode='a', newline='') as f:
			writer = csv.writer(f)
			writer.writerow([
				full_timestamp, millis, location_note, 
				co2, voc, iaq, gas, 
				t_raw, t_comp, h_raw, h_comp, acc
			])

		# 4. Save to SQL (Master Database)
		self.cursor.execute('''
			INSERT INTO sensor_data (
				timestamp_str, time_ms, location_note,
				co2, voc, iaq, gas_res, 
				temp_raw, temp_comp, hum_raw, hum_comp, accuracy
			) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		''', (full_timestamp, millis, location_note, co2, voc, iaq, gas, t_raw, t_comp, h_raw, h_comp, acc))
		self.conn.commit()

		# 5. Console Output
		self.reading_counter += 1
		print(f"[{real_time}] #{self.reading_counter} | Loc: {location_note} | CO2: {int(co2)} | VOC: {voc:.2f} | T_Comp: {t_comp:.1f} C | SQL: Saved")
		
		# Reset buffer for the next sampling interval
		self.current_reading = {}

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
	# Initialize acquisition engine
	logger = StudySpaceLogger()
	
	# Begin monitoring
	logger.start()
