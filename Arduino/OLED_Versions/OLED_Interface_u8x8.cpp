/**
* Interface for the 0.96" OLED Screen and ArdMeter
**/

#include "OLED_Interface_u8x8.h"

U8X8_SSD1306_128X64_NONAME_4W_SW_SPI display(OLED_CLK, OLED_MOSI, OLED_CS, OLED_DC, OLED_RST);
int CURSOR_Y = 0;

/* initialization function */
void OLED_Interface::init() {
	// temporary, allows VCC to be powered by dpin2
	pinMode(2, OUTPUT);
	digitalWrite(2, HIGH);

	display.begin();
	display.setPowerSave(0);

  display.setFont(u8x8_font_5x8_r);
	//display.setFont(u8x8_font_pxplustandynewtv_n);
}

/* displays given measurements in a nice way */
void OLED_Interface::displayValues(const float voltage, const float current, const float power, const long time) {
	display.clearDisplay(); // clear buffer
	display.setCursor(0, 0);
  CURSOR_Y = 0;
  
  float* units = new float[3];
  long* whime = new long[1];
  units[0] = voltage;
  units[1] = current;
  units[2] = power;
  whime[0] = time;
  
  display.print("Voltage: ");
  this->printValue(units[0], VOLTAGE_UNIT);
  
	display.print("Current: ");
	this->printValue(units[1], CURRENT_UNIT);

	display.print("Power: ");
	this->printValue(units[2], POWER_UNIT);

	display.print("Time: ");
	this->printValue(whime[0], TIME_UNIT);
}

/* prints a user-friendly version of any value-unit pair */
void OLED_Interface::printValue(float value, const char* ctype) {
	ScaledValue scaled_value = this->scaleValue(value);
 
	char print_value[10];
	dtostrf(scaled_value.value, MAX_DIGITS_DISPLAYED, this->getNumDecimals(scaled_value.value), print_value);

	// strip zeros from end of string
	this->stripZeros(print_value);
	
	//display.setCursor(SSD1306_LCDWIDTH - VALUE_SCREEN_OFFSET, CURSOR_Y);
	display.print(print_value);
	//display.setCursor(SSD1306_LCDWIDTH - UNIT_SCREEN_OFFSET, CURSOR_Y);
	display.print(this->scaleChar(scaled_value));
	this->println(ctype);
	this->println(" ");
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

/* Print a new line at the end of the message */
void OLED_Interface::println(char* msg) {
	CURSOR_Y++;

  display.print(msg);
	display.setCursor(0, CURSOR_Y);
}
