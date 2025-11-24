/*
Project: THE STUFFY STUDY POD (CHEM501)
Experiment: An Investigation into the Ventilation and Learning Environment in Student Study Spaces
Device: Nicla Sense ME | Role: Sensor Reader
Description:
  Acquires environmnetal metrics (CO2, IAQ, VOCs, Temp, Humidity)
  for the "POD" investigation into study space air quality.
  Acts as a slave device to the main controller (MKR WiFi 1010).
Hardware Requirements:
  1. OPERATION: Must connect to Arduino MKR WiFi 1010 via black ESLOV cable (I2C).
  2. UPLOAD: Connect via micro-USB to PC only to flash this code initially.
Authors: Josh and Kinga
Date: November 2025
License: MIT
*/

#include "Arduino.h"
#include "Arduino_BHY2.h"

void setup(){
  Serial.begin(115200);
  // Initialise I2C connection for the ESLOV cable
  BHY2.begin(NICLA_I2C, NICLA_VIA_ESLOV);
}

void loop(){
  // Update sensor values for the MKR board to read
  BHY2.update(1);
}