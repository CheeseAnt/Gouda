#include "OLED_Interface.h"
#include <Adafruit_INA219.h>

OLED_Interface oled;
Adafruit_INA219 ina219;

void(* reset) (void) = 0;

void setup() {
  Serial.begin(9600);
  
  oled.init();
  
  ina219.begin();
}

void loop() {
  /*
  v = ina219.getBusVoltage_V(); c = ina219.getCurrent_mA(); p = ina219.getPower_mW();
  
  Serial.println(v);
  Serial.println(c);
  Serial.println(p);
  Serial.println(millis());
  */
  oled.displayValues(ina219.getBusVoltage_V()*1000, ina219.getCurrent_mA(), ina219.getPower_mW(), millis());

  //Serial.println("After display");
  delay(200);
}
