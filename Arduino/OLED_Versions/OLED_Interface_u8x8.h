#ifndef OLED_INTERFACE_H

#define OLED_INTERFACE_H	
#include <Arduino.h>
#include <U8x8lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif

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
#define	CURRENT_UNIT "A"
#define	VOLTAGE_UNIT "V"
#define	POWER_UNIT "W"
#define	TIME_UNIT "s"

#define	NANO_UNIT "n"
#define	MICRO_UNIT "u"
#define	MILLI_UNIT "m"
#define	KILO_UNIT "k"
#define	MEGA_UNIT "M"

// Misc
#define MAX_DIGITS_DISPLAYED 5
#define UNIT_SCREEN_OFFSET 20
#define VALUE_SCREEN_OFFSET 75
#define SSD1306_LCDWIDTH 128
#define SSD1306_LCDHEIGHT 64

struct ScaledValue {
	float value;
	int type;
};

class OLED_Interface {
public:
	void init(void);
	void displayValues(const float voltage, const float current, const float power, const long time);
private:
	ScaledValue scaleValue(float value);
	void printValue(float value, const char* ctype);
	char scaleChar(ScaledValue scaled_value);
	void stripZeros(char* print_value);
	int getNumDecimals(float value);
	void println(char* msg);
};

#endif
