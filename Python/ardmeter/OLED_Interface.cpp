/**
* Interface for the 0.96" OLED Screen and ArdMeter
**/

#include "OLED_Interface.h"

void OLED_Interface::init() {
	// temporary, allows VCC to be powered by dpin2
	pinMode(2, OUTPUT);
	digitalWrite(2, HIGH);

	Adafruit_SSD1306 display(OLED_MOSI, OLED_CLK, OLED_DC, OLED_RST, OLED_CS);

	display.begin(SSD1306_SWITCHCAPVCC);
	display.display();

	display.setTextSize(2);
	display.setTextColor(WHITE);
}

void OLED_Interface::displayValues(int current) {
	display.clearDisplay(); // clear buffer

	display.print("Current: %d");
	display.println(current);

	display.display();
}