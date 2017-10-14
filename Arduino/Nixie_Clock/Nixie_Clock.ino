  // Arduinix 6 Bulb - Also supports Hour and Min. time set.
// 
// This code runs a six bulb setup and displays a prototype clock setup.
// NOTE: the delay is setup for IN-17 nixie bulbs.
//
// original code by Jeremy Howa
// Edited by Anton Shmatov to include RTC module

// www.robotpirate.com
// www.arduinix.com
// 2008 - 2009
// code modified by Andrea Biffi www.andreabiffi.com to work with only one SN74141
//
// Last Edit Nov 2013
//

// SN74141 : True Table
//D C B A #
//L,L,L,L 0
//L,L,L,H 1
//L,L,H,L 2
//L,L,H,H 3
//L,H,L,L 4
//L,H,L,H 5
//L,H,H,L 6
//L,H,H,H 7
//H,L,L,L 8
//H,L,L,H 9
#include <DS1302.h>

#define DEBUG_ON false
#define TEST_MODE false

// RTC MODULE SECTION

namespace {
  const int kCePin   = A4;  // Chip Enable
  const int kIoPin   = A3;  // Input/Output
  const int kSclkPin = A2;  // Serial Clock

  //creates a DS1302 object
  DS1302 rtc(kCePin, kIoPin, kSclkPin);
}

// Buttons

int hourButton = 14;
int minButton = 15;

// SN74141
int ledPin_0_a = 2;                
int ledPin_0_b = 3;
int ledPin_0_c = 4;
int ledPin_0_d = 5;
             
// anod pins
int ledPin_a_1 = 8;
int ledPin_a_2 = 9;
int ledPin_a_3 = 10;
int ledPin_a_4 = 11;
int ledPin_a_5 = 12;
int ledPin_a_6 = 13;

#ifdef TEST_MODE
  int dispVal[6] = {0,0,0,0,0,0};
  long int counter = 0;
#endif

// timekeeping

  int buttonHold = 0;
  
void setup() 
{
  pinMode(ledPin_0_a, OUTPUT);      
  pinMode(ledPin_0_b, OUTPUT);      
  pinMode(ledPin_0_c, OUTPUT);      
  pinMode(ledPin_0_d, OUTPUT);    
  
  pinMode(ledPin_a_1, OUTPUT);      
  pinMode(ledPin_a_2, OUTPUT);      
  pinMode(ledPin_a_3, OUTPUT); 
  pinMode(ledPin_a_4, OUTPUT);    
  pinMode(ledPin_a_5, OUTPUT);      
  pinMode(ledPin_a_6, OUTPUT);  
 
  // NOTE:
  // Grounding on pins analog0 and analog input 1 will set the Hour and Mins.
  pinMode(A0, INPUT ); // set the virtual pin analog0 (pin 0 on the analog inputs ) 
  digitalWrite(A0, HIGH); // set pin analog input 0 as a pull up resistor.

  pinMode(A1, INPUT ); // set the virtual pin analog input 1 (pin 1 on the analog inputs ) 
  digitalWrite(A1, HIGH); // set pin analog input 1 as a pull up resistor.
  
  if( DEBUG_ON )
  {
    Serial.begin(9600);
  }
  Serial.begin(9600);
}

////////////////////////////////////////////////////////////////////////
//
// DisplayNumberSet
// Use: Passing anod number, and number for bulb, this function
//      looks up the truth table and opens the correct outs from the arduino
//      to light the numbers given to this funciton.
//      On a 6 nixie bulb setup.
//
////////////////////////////////////////////////////////////////////////
void DisplayNumberSet( int anod, int num1)
{
  int anodPin;
  int a,b,c,d;
  
  // set defaults.
  a=0;b=0;c=0;d=0; // will display a zero.
  anodPin =  ledPin_a_1;     // default on first anod.
  
  // Select what anod to fire.
  switch( anod )
  {
    case 0:    anodPin =  ledPin_a_1;    break;
    case 1:    anodPin =  ledPin_a_2;    break;
    case 2:    anodPin =  ledPin_a_3;    break;
    case 3:    anodPin =  ledPin_a_4;    break;
    case 4:    anodPin =  ledPin_a_5;    break;
    case 5:    anodPin =  ledPin_a_6;    break;
  }  
  
  // Load the a,b,c,d to send to the SN74141 IC (1)
  switch( num1 )
  {
    case 0: a=0;b=0;c=0;d=0;break;
    case 1: a=1;b=0;c=0;d=0;break;
    case 2: a=0;b=1;c=0;d=0;break;
    case 3: a=1;b=1;c=0;d=0;break;
    case 4: a=0;b=0;c=1;d=0;break;
    case 5: a=1;b=0;c=1;d=0;break;
    case 6: a=0;b=1;c=1;d=0;break;
    case 7: a=1;b=1;c=1;d=0;break;
    case 8: a=0;b=0;c=0;d=1;break;
    case 9: a=1;b=0;c=0;d=1;break;
  }  
  
  // Write to output pins.
  digitalWrite(ledPin_0_d, d);
  digitalWrite(ledPin_0_c, c);
  digitalWrite(ledPin_0_b, b);
  digitalWrite(ledPin_0_a, a);
  //delay(2);
  // Turn on this anod.
  digitalWrite(anodPin, HIGH);   

  // Delay
  // NOTE: With the difference in Nixie bulbs you may have to change
  //       this delay to set the update speed of the bulbs. If you 
  //       dont wait long enough the bulb will be dim or not light at all
  //       you want to set this delay just right so that you have 
  //       nice bright output yet quick enough so that you can multiplex with
  //       more bulbs (2ms is standard).
  delay(2);                       // ################################################################################
  
  // Shut off this anod.
  digitalWrite(anodPin, LOW);
}

////////////////////////////////////////////////////////////////////////
//
// DisplayNumberString
// Use: passing an array that is 6 elements long will display numbers
//      on a 6 nixie bulb setup.
//
////////////////////////////////////////////////////////////////////////
void DisplayNumberString( int* array )
{
  // bank 1 (bulb 1)
  DisplayNumberSet(0,array[0]);   
  // bank 2 (bulb 2)
  DisplayNumberSet(1,array[1]);   
  // bank 3 (bulb 3)
  DisplayNumberSet(2,array[2]);   
  // bank 4 (bulb 4)
  DisplayNumberSet(3,array[3]);   
  // bank 5 (bulb 5)
  DisplayNumberSet(4,array[4]);   
  // bank 6 (bulb 6)
  DisplayNumberSet(5,array[5]);   
}

// to de-poison any tubes or try and prevent it

void cleanTubes() {
	for(int currNum = 0; currNum < 10; currNum++) {
		long currentTime = millis();
		while((millis() - currentTime) < 100) {
			DisplayNumberSet(0, currNum);
      DisplayNumberSet(1, currNum);
      DisplayNumberSet(2, currNum);
      DisplayNumberSet(3, currNum);
      DisplayNumberSet(4, currNum);
      DisplayNumberSet(5, currNum);
		}
	}
}

// Defines
long MINS = 60;         // 60 Seconds in a Min.
long HOURS = 60 * MINS; // 60 Mins in an hour.
long DAYS = 24 * HOURS; // 24 Hours in a day. > Note: change the 24 to a 12 for non millitary time.

long runTime = 0;       // Time from when we started.

// default time sets. clock will start at 12:59:00 ------------------------setting time

// NOTE: We start seconds at 0 so we dont need a clock set
//       The values you see here would be what you change 
//       if you added a set clock inputs to the board.

Time initial = rtc.time();

long clockHourSet = initial.hr;
long clockMinSet  = initial.min;
long clockSecSet = initial.sec;
  


int hourButtonPressed = false;
int minButtonPressed = false;
int secButtonPressed = false;

int tillCleanse = 0;

////////////////////////////////////////////////////////////////////////
//
//
////////////////////////////////////////////////////////////////////////
void loop()     
{
  // Get milliseconds.
  runTime = millis();

  // Get time in seconds.
  long currTime = (runTime) / 1000; ///change this value to speed up or slow down the clock, set to smaller number such as 10, 1, or 100 for debugging
  
  int hourInput = digitalRead(hourButton);  
  int minInput  = digitalRead(minButton);
  
  if(DEBUG_ON) {
    Serial.println(hourInput);
    Serial.print(" ");
    Serial.print(buttonHold);
    Serial.print(" ");
    Serial.print(clockMinSet);
    Serial.print(" ");
    Serial.println(clockHourSet);
  }
    
  if(hourInput == 0)
    hourButtonPressed = true;
  
  if(minInput == 0) 
    minButtonPressed = true;

  if(hourButtonPressed || minButtonPressed)
    buttonHold++;
  else
    buttonHold = 0;
  
  if(hourButtonPressed && minButtonPressed) {
  	  tillCleanse++;

  	  if(tillCleanse > 200) {
  	  	cleanTubes();
  	    cleanTubes();
  	  }

      hourButtonPressed = false;
      minButtonPressed = false;
  }
  else {
  	  if((tillCleanse < 200) && tillCleanse) {
  	  	clockSecSet++;
  	    buttonHold = 0;
        
        secButtonPressed = true;
  	  }

  	  else if(!secButtonPressed) {
  		  
  		  if(hourButtonPressed && hourInput) { 
  		    clockHourSet++;
  		    hourButtonPressed = false;
  		  }
  		  else if(hourButtonPressed && (buttonHold > 69)) {
  		    if(buttonHold%9 == 0)
  		      clockHourSet++;
           
  		    hourButtonPressed = false;
  		  }
  		  
  		  if(minButtonPressed && minInput) {
  		    clockMinSet++;
  		    minButtonPressed = false;
  		  }
  		  else if(minButtonPressed && (buttonHold > 69)) {
  		    if(buttonHold%9 == 0) 
  		      clockMinSet++;
            
          minButtonPressed = false;
  		  }
		}

		tillCleanse = 0;
  }

  if(hourInput && minInput) {
    secButtonPressed = false;
    minButtonPressed = false;
    hourButtonPressed = false;
  }
    
  // Set time based on offset..
  
  long hbump = 60*60*clockHourSet;
  long mbump = 60*clockMinSet;
  currTime += mbump + hbump + clockSecSet;

  // Convert time to days,hours,mins,seconds
  long days  = currTime / DAYS;    currTime -= days  * DAYS; 
  long hours = currTime / HOURS;   currTime -= hours * HOURS; 
  long minutes  = currTime / MINS;    currTime -= minutes  * MINS; 
  long seconds  = currTime; 
  
  // Check if current times matches time on RTC, if not then update it
  Time current = rtc.time();
  
  if(hourInput == 1 || minInput == 1) {
    current.min = minutes;
    current.hr = hours;
    current.sec = seconds;
    rtc.writeProtect(false);
    rtc.time(current);
    rtc.writeProtect(true);
  }
  
 /*   
if(DEBUG_ON) {
  Serial.print(hours);
  Serial.print(":");
  Serial.print(minutes);
  Serial.print(":");
  Serial.print(seconds);
  Serial.print("\n");
  Serial.print(current.hr);
  Serial.print(":");
  Serial.print(current.min);
  Serial.print(":");
  Serial.print(current.sec);
  Serial.print("\n\n");
  Serial.print(clockSecSet);
  Serial.print("\n");
  delay(1000);
}
  */
  // Get the high and low order values for hours,min,seconds. 
  int lowerHours = hours % 10;
  int upperHours = hours - lowerHours;
  int lowerMins = minutes % 10;
  int upperMins = minutes - lowerMins;
  int lowerSeconds = seconds % 10;
  int upperSeconds = seconds - lowerSeconds;
  if( upperSeconds >= 10 )   upperSeconds = upperSeconds / 10;
  if( upperMins >= 10 )      upperMins = upperMins / 10;
  if( upperHours >= 10 )     upperHours = upperHours / 10;

  // Fill in the Number array used to display on the tubes.
  int NumberArray[6]={0,0,0,0,0,0};
  NumberArray[0] = upperHours;
  NumberArray[1] = lowerHours;
  NumberArray[2] = upperMins;
  NumberArray[3] = lowerMins;
  NumberArray[5] = upperSeconds;
  NumberArray[4] = lowerSeconds;

  /*if(DEBUG_ON) {
    Serial.print(upperHours);
    Serial.print(lowerHours);
  Serial.print(":");
  Serial.print(upperMins);
  Serial.print(lowerMins);
  Serial.print(":");
  Serial.print(upperSeconds);
  Serial.print(lowerSeconds);
  Serial.print("\n");
  Serial.print(current.hr);
  Serial.print(":");
  Serial.print(current.min);
  Serial.print(":");
  Serial.print(current.sec);
  Serial.print("\n\n");
  Serial.print(clockSecSet);
  Serial.print("\n");
  delay(1000);
  }
   */


  // Display.
  if(TEST_MODE) {
    counter++;
    dispVal[0] = 1;//(int)counter%1000;
    dispVal[1] = 2;//(int)counter%10000;
    dispVal[2] = 3;//(int)counter%100000;
    dispVal[3] = 4;//(int)counter%1000000;
    dispVal[4] = 5;//(int)counter%10000000;
    dispVal[5] = 6;//(int)counter%100000000;
    DisplayNumberString(dispVal);
  }
  else
    DisplayNumberString( NumberArray );

  if((current.hr%10 == 0) && (current.min == 3) && (current.sec == 2)) {
  	cleanTubes();
    cleanTubes();
  }
}


