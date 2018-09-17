#ifndef DATA_SOURCE_H

#define DATA_SOURCE_H

#define DEFAULT_BAUD_RATE 115200

// various protocol units
enum {
	BUNDLE_SEPARATOR = '*',
	VALUE_SEPARATOR = ';',

	VALUE_VOLTAGE = 'v',
	VALUE_CURRENT = 'c',
	VALUE_POWER = 'p',
	VALUE_TIME = 't'
};

class DataSource {
public:
	DataSource();
	void trickle(float, float, float, unsigned long);
}

#endif