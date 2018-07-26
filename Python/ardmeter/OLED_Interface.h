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

class OLED_Interface {
public:
	OLED_Interface(void);
	void init(void);
	void displayValues(int);
private:
	Adafruit_SSD1306 display;
};

#endif