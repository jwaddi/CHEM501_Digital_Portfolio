/*
Project: THE STUFFY STUDY (CHEM501)
Experiment: An Investigation into the Ventilation and Learning Environment in Student Study Spaces
Device: Arduino MKR WiFi 1010 | Role: Main Controller (Wireless Gateway)
Description:
  This firmware coordinates data acquisition from the Nicla Sense ME and performs
  real-time telemetry transmission to the MQTT cloud server at 1Hz.
  The system is configured for standalone operation (independent of USB connection),
  by using an external battery power and a mobile hotspot.
Hardware Requirements:
  1. SENSOR LINK: Must connect to Nicla Sense ME via black ESLOV cable (I2C).
  2. POWER: Requires external battery power (Power Bank).
Authors: Josh and Kinga
Date: November 2025
License: MIT
 */


// CORE LIBRARIES

#include <ArduinoMqttClient.h> 
#include <WiFiNINA.h>
#include <Arduino_BHY2Host.h>
#include "arduino_secrets.h"  // Sensitive credentials are secured here (not shared on GitHub)


// NETWORK CONFIGURATION

// The defined secrets are used to prevent sensitive WiFi credentials from being shared publicly on the repository.
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;


// MQTT Server Settings (Cloud Instance)

// This server address is specific to the authors' cloud account and must be replaced by any user attempting to replicate the project.
const char server[] = "test.mosquitto.org";
int port = 1883;

// Topics are structured hierarchically for streamlined database filtering.
const char topic_base[] = "chem501/josh_kinga/stuffy_study"; 


// OBJECT INITIALISATION

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

// Initialise Sensor Objects
SensorBSEC bsec(SENSOR_ID_BSEC);    // AI-Compensated IAQ Sensors
Sensor temp(SENSOR_ID_TEMP);        // Raw Temperature Sensor
Sensor humidity(SENSOR_ID_HUM);     // Raw Humidity Sensor
Sensor gas(SENSOR_ID_GAS);          // Raw Gas Sensor


// TIMING CONTROL

const long INTERVAL_MS = 1000; // 1.0 Hz Sampling Rate
unsigned long last_transmission = 0;


// SETUP ROUTINE

void setup() {
  Serial.begin(115200);

  delay(10000); // Short delay to ensure stable voltage on startup

  Serial.println("DEBUG: System Booting and Initialising Wireless Mode...");

  // 1. Initialise Sensor Link
  init_nicla_connection();

  // 2. Initialise Wireless Link
  connect_to_wifi();

  // 3. Initialise Cloud Link
  connect_to_server();

  Serial.println("STATUS: System Online. Beginning Wireless Data Stream.");
}

void loop() {
  // Maintain active connections
  mqttClient.poll();
  BHY2Host.update();

unsigned long currentMillis = millis();

// Run the data collection loop every 1000ms
  if (currentMillis - last_transmission >= INTERVAL_MS) {
    last_transmission = currentMillis;
    read_and_transmit_data();
  }
}


// FUNCTION DETAILS

void init_nicla_connection() {
  Serial.print("STATUS: Initialising Nicla Sense ME... ");
  // Attempt to establish I2C handshake with Nicla Sense ME
  if (BHY2Host.begin()) {
    Serial.println("[SUCCESS]");
  } else {
    Serial.println("[FAILED]");
    Serial.println("ERROR: Check ESLOV connection. System Halted.");
    while (1); // Halt to prevent operation with no sensor data
  }

  // Activate Sensor Streams for both raw and compensated metrics
  bsec.begin();
  bsec.configure(1.0, 0); // Set BSEC sampling rate to 1Hz
  temp.begin();
  humidity.begin();
  gas.begin();
}

void connect_to_wifi() {
  Serial.print("STATUS: Connecting to WiFi (");
  Serial.print(ssid);
  Serial.print(")... ");

  // The system is configured to retry indefinitely until a connection is secured.
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    delay(5000); // Wait 5 seconds before retrying
  }
  Serial.println("[CONNECTED]");
}

void connect_to_server() {
  Serial.print("STATUS: Connecting to MQTT Server... ");
  if (!mqttClient.connect(server, port)) {
    Serial.print("[FAILED] Error: ");
    Serial.println(mqttClient.connectError());
    // Halt to prevent data being lost or transmitted incorrectly.
    while (1);
  }
  Serial.println("[CONNECTED]");
}

void read_and_transmit_data() {

  // DATA ACQUISITION

  // Acquire all sensor readings
  float raw_t = temp.value();
  float raw_h = humidity.value();
  float raw_g = gas.value();
  float comp_t = bsec.comp_t();
  float comp_h = bsec.comp_h();
  float co2 = bsec.co2_eq();
  float voc = bsec.b_voc_eq();
  float iaq = bsec.iaq();
  int accuracy = bsec.accuracy();
  unsigned long timestamp = millis();

  // DATA TRANSMISSION
  // Each metric is published to a unique topic for simplified database organisation.

  // Topic: chem501/josh_kinga/stuffy_study/time_ms
  mqttClient.beginMessage(String(topic_base) + "/time_ms");
  mqttClient.print(timestamp);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/co2
  mqttClient.beginMessage(String(topic_base) + "/co2");
  mqttClient.print(co2);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/voc
  mqttClient.beginMessage(String(topic_base) + "/voc");
  mqttClient.print(voc);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/iaq
  mqttClient.beginMessage(String(topic_base) + "/iaq");
  mqttClient.print(iaq);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/gas_raw
  mqttClient.beginMessage(String(topic_base) + "/gas_raw");
  mqttClient.print(raw_g);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/temp_raw
  mqttClient.beginMessage(String(topic_base) + "/temp_raw");
  mqttClient.print(raw_t);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/comp_t
  mqttClient.beginMessage(String(topic_base) + "/comp_t");
  mqttClient.print(comp_t);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/hum_raw
  mqttClient.beginMessage(String(topic_base) + "/hum_raw");
  mqttClient.print(raw_h);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/hum_comp
  mqttClient.beginMessage(String(topic_base) + "/hum_comp");
  mqttClient.print(comp_h);
  mqttClient.endMessage();

  // Topic: chem501/josh_kinga/stuffy_study/accuracy
  mqttClient.beginMessage(String(topic_base) + "/accuracy");
  mqttClient.print(accuracy);
  mqttClient.endMessage();

  // DIAGNOSTIC PRINT (USB ONLY)
  Serial.print("[RAW] Temp: ");
  Serial.print(raw_t, 2);
  Serial.print(" C | Hum: ");
  Serial.print(raw_h, 2);
  Serial.print(" % | Gas: ");
  Serial.print(raw_g, 0);
  Serial.print(" Ohms");

  Serial.print("  ||  [BSEC] Temp: ");
  Serial.print(comp_t, 2);
  Serial.print(" C | Hum: ");
  Serial.print(comp_h, 2);
  Serial.print(" % | CO2: ");
  Serial.print(co2, 0);
  Serial.print(" ppm | VOC: ");
  Serial.print(voc, 2);
  Serial.print(" ppm | IAQ: ");
  Serial.print(iaq, 0);
  Serial.print(" | Acc: ");
  Serial.println(accuracy);
}
