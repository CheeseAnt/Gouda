#define BITLIM 13
#define PI_HIGH 168
#define DEBUG 0

int piIn = 8, piOut = 9, piNew = 11, tempIn = 15;
int digCount = 0;
bool TX = false, newT = false;
long R25 = 0.98e5, B25 = 3150, R2 = 120700; // maybe B25 3450, R25 1e5
double T25 = 298.15;
double temp;

/*

pinMode(tempIn, INPUT);
  

*/
void PDSetup(int piIn, int piOut, int piNew) {
  // put your setup code here, to run once:
  pinMode(piIn, INPUT);
  pinMode(piOut, OUTPUT);
  pinMode(piNew, OUTPUT);

  if(DEBUG)
    Serial.begin(9600);
  
}

void waitRequest(int piIn) {
  while(digitalRead(piIn) == LOW);
  while(digitalRead(piIn) == HIGH) { // while pi says new value
    TX = true;

    if(DEBUG) {
      Serial.println(digitalRead(piIn));
    }
  }
  	
}
void loop() {
  // put your main code here, to run repeatedly:

  

  if(TX && !newT) { // if new value & send, wait for pi to confirm before sending
    newT = true;
    TX = false;
  }
  else if(TX && newT) { // if all good continue to send number one by one
    TX = false;

    digitalWrite(piOut, bitRead((long)(temp*100), digCount)); // send version of temp to pi, convert back on other end
    digCount++;
    
    if(DEBUG) {
      Serial.print("Bit no ");
      Serial.print(digCount);
      Serial.print(": ");
      Serial.println(bitRead((long)(temp*100), digCount-1)); // debug
      Serial.println((long)(temp*100));
    }
      
    if(digCount == (BITLIM + 1)) { // if done sending number, reset 
      newT = false;
      digCount = 0;
    }
  }

  if(newT && digCount == 0) { // if new value, read in new thing and tell pi
    digitalWrite(piNew, HIGH);
    
    double tempV = analogRead(tempIn);
    tempV = tempV*5/1024;
    double R1 = -(tempV*R2)/(tempV-5);
    temp = (1/((log(R1/R25)/B25)+1/T25))-273.15;
    
  }
  else
    digitalWrite(piNew, LOW);

  if(DEBUG && TX)
    Serial.println("No Signal.");
  
  
}
