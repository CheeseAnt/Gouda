#include "DataSource.h"

DataSource::DataSource() {
	// ensure we end any prior communications
	Serial.end();

	// start with default rate as specified in header
	Serial.begin(DEFAULT_BAUD_RATE);

	Serial.print(COMMS_BEGIN);
}

/* Trickle the measured data to the serial communications */
void DataSource::trickle(float voltage, float current, float power, unsigned long ptime) {
	Serial.print(VALUE_SEPARATOR);
	Serial.print(VALUE_VOLTAGE);
	Serial.print(voltage);

	Serial.print(VALUE_SEPARATOR);
	Serial.print(VALUE_CURRENT);
	Serial.print(current);

	Serial.print(VALUE_SEPARATOR);
	Serial.print(VALUE_POWER);
	Serial.print(power);

	Serial.print(VALUE_SEPARATOR);
	Serial.print(VALUE_TIME);
	Serial.print(ptime);
}