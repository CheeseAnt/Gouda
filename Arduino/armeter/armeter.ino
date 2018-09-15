#include "OLED_Interface.h"
#include <Adafruit_INA219.h>

OLED_Interface oled;
Adafruit_INA219 ina219;

void setup() {
  Serial.begin(9600);
  
  oled.init();
  
  ina219.begin();
}

void loop() {
  float v = ina219.getBusVoltage_V(), c = ina219.getCurrent_mA(), p = ina219.getPower_mW();
  v = ina219.getBusVoltage_V(); c = ina219.getCurrent_mA(); p = ina219.getPower_mW();

  Serial.println("before display");
  oled.displayValues(v*1000, c, p, 0);

  Serial.println("After display");
  delay(200);
}
