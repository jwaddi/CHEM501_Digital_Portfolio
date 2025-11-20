#include <Arduino_BHY2Host.h>

SensorBSEC bsec(SENSOR_ID_BSEC);

unsigned long lastPrint = 0;
const int printInterval = 1000;

void setup() {
  Serial.begin(115200);
  BHY2Host.begin();
  bsec.begin();
  // Updated header to include Accuracy
  Serial.println("Timestamp(ms),Temperature(C),Humidity(%),CO2(ppm),IAQ,Accuracy");
}

void loop() {
  BHY2Host.update();

  if (millis() - lastPrint >= printInterval) {
    lastPrint = millis();
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
    Serial.println(bsec.accuracy()); // 0 = Warming up, 3 = Best
  }
}