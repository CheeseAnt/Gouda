#include "OLED_Interface.h"
#include "DataSource.h"
#include <Adafruit_INA219.h>

void(* reset) (void) = 0;

OLED_Interface oled;
Adafruit_INA219 ina219;
DataSource ds;

float voltage, current, power;
unsigned long ptime;

void setup() {
  oled.init();
  
  ina219.begin();
}

void loop() {
  voltage = ina219.getBusVoltage_V()*1000; // voltage in mV
  current = ina219.getCurrent_mA(); // current in mA
  power = ina219.getPower_mW(); // power in mW
  ptime = millis(); // system time in ulong

  // display on oled
  oled.displayValues(voltage, current, power, ptime);

  // trickle to serial
  ds.trickle(voltage, current, power, ptime);

  delay(5); // just in case we need a tiny delay
}
