/**
* Interface for the 0.96" OLED Screen and ArdMeter
**/

#include "OLED_Interface.h"

Adafruit_SSD1306 display(OLED_MOSI, OLED_CLK, OLED_DC, OLED_RST, OLED_CS);

/* initialization function */
void OLED_Interface::init() {
	// temporary, allows VCC to be powered by dpin2
	pinMode(2, OUTPUT);
	digitalWrite(2, HIGH);

	display.begin(SSD1306_SWITCHCAPVCC);
	display.display();

	display.setTextSize(1);
	display.setTextColor(WHITE);
}

/* displays given measurements in a nice way */
void OLED_Interface::displayValues(float voltage, float current, float power, long ptime) {
	display.clearDisplay(); // clear buffer
	display.setCursor(0, 0);

  display.print(F("Voltage: "));
  this->printValue(voltage, VOLTAGE_UNIT);
  
	display.print(F("Current: "));
	this->printValue(current, CURRENT_UNIT);

	display.print(F("Power: "));
	this->printValue(power, POWER_UNIT);

	Serial.println("before time");
	display.print(F("Time: "));
	this->printValue((float)millis(), TIME_UNIT);
	Serial.println("after time");

	display.display();
	Serial.println("after display");
}

/* prints a user-friendly version of any value-unit pair */
void OLED_Interface::printValue(float value, const char ctype) {
	ScaledValue scaled_value = this->scaleValue(value);
 
	char print_value[10];
	dtostrf(scaled_value.value, MAX_DIGITS_DISPLAYED, this->getNumDecimals(scaled_value.value), print_value);

	// strip zeros from end of string
	this->stripZeros(print_value);
	
	display.setCursor(SSD1306_LCDWIDTH - VALUE_SCREEN_OFFSET, display.getCursorY());
	display.print(print_value);
	display.setCursor(SSD1306_LCDWIDTH - UNIT_SCREEN_OFFSET, display.getCursorY());
	display.print(this->scaleChar(scaled_value));
	display.println(ctype);
	display.println(F(""));
}

/* Scales a value to being between 1 and 1000, returning the value and scale */
ScaledValue OLED_Interface::scaleValue(float value) {
	// struct holding the float value and type
	ScaledValue scaled_value;

	scaled_value.type = TYPE_MILLI;
	scaled_value.value = value;
 
	if(scaled_value.value != 0) {
		// avoiding ifs by while loop conditions
		// if the value is below 1 currently
		while(abs(scaled_value.value) < LOWER_BOUND) {
			scaled_value.value *= TYPE_SCALE;

			scaled_value.type += TYPE_MILLI;
		}

		// else if the value is above 1000	
		while(abs(scaled_value.value) >= UPPER_BOUND) {
			scaled_value.value /= TYPE_SCALE;

			scaled_value.type += TYPE_KILO;
		}
	}

	return scaled_value;
}

/* Strips unecessary zeros at the end of the float value string */
void OLED_Interface::stripZeros(char* print_value) {
	for(int i = strlen(print_value) - 1; i >= 0; i--) {
		if(print_value[i] == '0')
			print_value[i] = '\0';
		else
			break;
	}

	if(print_value[strlen(print_value) - 1] == '.')
		print_value[strlen(print_value) - 1] = '\0';
}

/* returns the necessary char for scale */
char OLED_Interface::scaleChar(ScaledValue scaled_value) {
	switch(scaled_value.type) {
		case TYPE_NANO: return NANO_UNIT;
		case TYPE_MICRO: return MICRO_UNIT;
		case TYPE_MILLI: return MILLI_UNIT;
		case TYPE_KILO: return KILO_UNIT;
		case TYPE_MEGA: return MEGA_UNIT;
		default: return ' ';
	}
}

/* Find the number of digits before the decimal */
int OLED_Interface::getNumDecimals(float value) {
	int digits = MAX_DIGITS_DISPLAYED;

	while(value >= 1) {
		value /= 10;

		digits--;
	}
	
	return digits;
}
