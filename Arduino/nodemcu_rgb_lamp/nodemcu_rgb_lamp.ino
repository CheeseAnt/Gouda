/*************************************************************
 *************************************************************/

/* Comment this out to disable prints and save space */
#define BLYNK_PRINT Serial

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <EEPROM.h>

// Blynk Auth Token
char auth[] = "09eebc0c6c574c3c85ff912858cf6b94";

// WiFi Credentials
char ssid[] = "HUAWEI-B535-B4B7";
char pass[] = "4QQF79BDBBG";

// EEPROM Byte locations
int RED_EE = 0x00;
int GREEN_EE = 0x04;
int BLUE_EE = 0x08;
int BRGHT_EE = 0x0c;
int SWITCH_EE = 0x10;

// Output pins
int RED_OUT = D0;
int GREEN_OUT = D1;
int BLUE_OUT = D2;

// Light values
int red = 0;
int green = 0;
int blue = 0;
int brightness = 0;
bool on_state = true;

/*
 * Update a single colour by analog writing to the pin
 * Takes into account brightness and on state
 */
void updateC(int pin, int colour) {
  float value = on_state ? (float(brightness) / 1023.0) * colour : 0.0;

  analogWrite(pin, int(value));
}

/*
 * Updates all colour values
 */
void updateAll() {
  updateC(RED_OUT, red);
  updateC(GREEN_OUT, green);
  updateC(BLUE_OUT, blue);
}

/*
 * Writes a single value as an int to the given address in EEPROM memory
 */
void writeEE(int addr, int val) {
  int oldval;

  // try to save some SRAM writes by checking if value same as before, which it shouldn't be
  EEPROM.get(addr, oldval);

  if(val != oldval) {
    EEPROM.put(addr, val);
    EEPROM.commit();
  }
}

/**
 * Get and set ON/OFF switch value
 */
BLYNK_WRITE(V0)
{
  int pinValue = param.asInt();

  // on when equal to 1
  on_state = param.asInt() == 1;

  // write to EEPROM and update all values
  writeEE(SWITCH_EE, on_state);
  updateAll();
} 

/*
 * Receive and set new red value 
 */
BLYNK_WRITE(V1)
{
  int pinValue = param.asInt();

  red = param.asInt();

  // save new value to EEPROM and update red colour
  writeEE(RED_EE, red);
  updateC(RED_OUT, red);
}

/*
 * Receive and set new green value 
 */
BLYNK_WRITE(V2)
{
  int pinValue = param.asInt();

  green = param.asInt();

  // save new value to EEPROM and update green colour
  writeEE(GREEN_EE, green);
  updateC(GREEN_OUT, green);
}

/*
 * Receive and set new blue value 
 */
BLYNK_WRITE(V3)
{
  int pinValue = param.asInt();

  blue = param.asInt();

  // save new value to EEPROM and update blue colour
  writeEE(BLUE_EE, blue);
  updateC(BLUE_OUT, blue);
}

/*
 * Receive and set new brightness value
 */
BLYNK_WRITE(V4)
{
  int pinValue = param.asInt();
  
  brightness = param.asInt();

  // save new value to EEPROM and update all colours
  writeEE(BRGHT_EE, brightness);
  updateAll();
}

/*
 * Read all saved values from EEPROM
 */
void readEEPROM() {
  EEPROM.get(RED_EE, red);
  EEPROM.get(GREEN_EE, green);
  EEPROM.get(BLUE_EE, blue);
  EEPROM.get(BRGHT_EE, brightness);
  EEPROM.get(SWITCH_EE, on_state);
}

void setup()
{
  Blynk.begin(auth, ssid, pass);

  // set up pins
  pinMode(RED_OUT, OUTPUT);
  pinMode(GREEN_OUT, OUTPUT);
  pinMode(BLUE_OUT, OUTPUT);

  // initialise eeprom, 4 ints and 1 bool
  EEPROM.begin(17);

  // read all saved values and display them
  readEEPROM();
  updateAll();
}

void loop()
{
  Blynk.run();
}
