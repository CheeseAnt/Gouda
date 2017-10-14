#include <iostream>
#include <wiringPi.h>
#include <math.h>

#define DELAYTIME 1	/* in micro s */
#define VAL_INTERVAL 300 /* in ms */

using namespace std;

void newBit(int, int);

int main(void) {
	wiringPiSetupPhys();
	
	int RPin = 16, RPOut = 18, RPnew = 12;
	int temperIn = 0, i = 0;

	pinMode(RPOut, OUTPUT);
	pinMode(RPin, INPUT);
	pinMode(RPnew, INPUT);

	while(1) {

		if(digitalRead(RPnew) == HIGH) { /* if new number, reset values */
			i = 0;
			temperIn = 0;
			newBit(RPOut, DELAYTIME);
		}

		while(digitalRead(RPnew) == LOW) { /* while not a new value */
			delay(DELAYTIME); /* request new, then read and add accordingly to bit pos */
			temperIn += digitalRead(RPin)*pow(2, i);

			#ifdef DEBUG
				cout << digitalRead(RPin) << "   ";
			#endif

			i++;
			if(digitalRead(RPnew) == LOW)
				newBit(RPOut, DELAYTIME);

		}

		delay(VAL_INTERVAL); /* delay between values */
		
		if(temperIn != 0)
			cout << (float)temperIn/100 << " Degrees" << endl;
	}


	return 0;
}

void newBit(int RPin, int delayT) {
	digitalWrite(RPin, HIGH);
	delay(delayT);
	digitalWrite(RPin, LOW);
}
