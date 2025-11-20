#include <Arduino_BHY2Host.h>

SensorBSEC bsec(SENSOR_ID_BSEC);

void setup() {
  Serial.begin(115200);
  while(!Serial); // WAIT here until Serial Monitor is opened.

  Serial.println("DEBUG: Serial connected. Initializing BHY2 Host...");

  // If connection fails, it might hang here.
  if (BHY2Host.begin(false)) { // 'false' means don't wait forever
      Serial.println("DEBUG: Nicla found and connected!");
  } else {
      Serial.println("ERROR: Failed to find Nicla! Check black ESLOV cable.");
      while(1); // Stop here forever if failed
  }

  Serial.println("DEBUG: Initializing BSEC sensor...");
  bsec.begin();
  Serial.println("DEBUG: BSEC started. Waiting for first data...");
  Serial.println("Timestamp(ms),Temperature(C),Humidity(%),CO2(ppm),IAQ,Accuracy");
}

void loop() {
  BHY2Host.update();
 
  static unsigned long lastPrint = 0;
  // Print every 1 second
  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();
   
    // Only print if the sensor actually has valid data to send
    // if (bsec.accuracy() >= 0) {
        Serial.print(millis());
        Serial.print(",");
        Serial.print(bsec.comp_t());
        Serial.print(",");
        Serial.print(bsec.comp_h());
        Serial.print(",");
        Serial.print(bsec.co2_eq());
        Serial.print(",");
        Serial.print(bsec.iaq());
        Serial.print(",");
        Serial.println(bsec.accuracy());
    // }
  }
}
