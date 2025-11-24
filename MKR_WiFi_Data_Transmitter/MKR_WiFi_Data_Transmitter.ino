/*
Project: THE STUFFY STUDY (CHEM501)
Experiment: An Investigation into the Ventilation and Learning Environment in Student Study Spaces
Device: Arduino MKR WiFi 1010 | Role: Main Controller (Host)
Description:
 Acts as the I2C Master to the Nicla Sense ME. 
 Initialises the BSEC sensor fusion library (on the Nicla) and requests data 
 (CO2, IAQ, VOCs, Temp, Humidity) at 1Hz.
Hardware Requirements:
 1. SENSOR LINK: Must connect to Nicla Sense ME via black ESLOV cable (I2C).
 2. DATA LOGGING: Must remain connected to PC via USB (Serial @ 115200 baud).
Authors: Josh and Kinga
Date: November 2025
License: MIT
*/

#include <Arduino_BHY2Host.h>

// Create BSEC sensor instance
SensorBSEC bsec(SENSOR_ID_BSEC);

void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait for Serial Monitor
  Serial.println("DEBUG: Serial connected. Initializing BHY2 Host...");

  if (BHY2Host.begin()) {
    Serial.println("DEBUG: Nicla found and connected!");
  } else {
    Serial.println("ERROR: Failed to find Nicla! Check black ESLOV cable.");
    while (1);
  }

  Serial.println("DEBUG: Initializing BSEC sensor...");
  bsec.begin();

  Serial.println("DEBUG: Configuring BSEC virtual sensor for 1 Hz...");
  bsec.configure(1.0, 0);

  Serial.println("DEBUG: BSEC started. Waiting for first data...");
  Serial.println("Timestamp(ms),Temperature(C),Humidity(%),CO2(ppm),IAQ,Accuracy");
}

void loop() {
  // Continuously poll for new data from Nicla
  BHY2Host.update();

  static unsigned long lastPrint = 0;
  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();

    // Read values directly — may start as 0 until BSEC stabilizes
    float temperature = bsec.comp_t();
    float humidity = bsec.comp_h();
    float co2 = bsec.co2_eq();
    float iaq = bsec.iaq();
    int accuracy = bsec.accuracy();

      Serial.print(millis());
      Serial.print(",");
      Serial.print(temperature);
      Serial.print(",");
      Serial.print(humidity);
      Serial.print(",");
      Serial.print(co2);
      Serial.print(",");
      Serial.print(iaq);
      Serial.print(",");
      Serial.println(accuracy);
    }
  }
