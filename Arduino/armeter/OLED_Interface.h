#ifndef OLED_INTERFACE_H

#define OLED_INTERFACE_H	
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// software SPI

#define OLED_CLK 3
#define OLED_MOSI 4
#define OLED_RST 5
#define OLED_DC 6
#define OLED_CS 12 // this is unused

// Unit scales
enum {
	TYPE_NANO = -3,
	TYPE_MICRO = -2,
	TYPE_MILLI = -1,
	TYPE_NORMAL = 0,
	TYPE_KILO = 1,
	TYPE_MEGA = 2,
	TYPE_SCALE = 1000,
	UPPER_BOUND = 1000,
	LOWER_BOUND = 1
};

// Unit Types
enum {
	CURRENT_UNIT = 'A',
	VOLTAGE_UNIT = 'V',
	POWER_UNIT = 'W',
	TIME_UNIT = 's',

	NANO_UNIT = 'n',
	MICRO_UNIT = 'u',
	MILLI_UNIT = 'm',
	KILO_UNIT = 'k',
	MEGA_UNIT = 'M'
};

// Misc
#define MAX_DIGITS_DISPLAYED 5
#define UNIT_SCREEN_OFFSET 20
#define VALUE_SCREEN_OFFSET 75

struct ScaledValue {
	float value;
	int type;
};

class OLED_Interface {
public:
	void init(void);
	void displayValues(float voltage, float current, float power, long time);
private:
	ScaledValue scaleValue(float value);
	void printValue(float value, const char ctype);
	char scaleChar(ScaledValue scaled_value);
	void stripZeros(char* print_value);
	int getNumDecimals(float value);
};

#endif
