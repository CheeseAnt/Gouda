void setup() {
  // put your setup code here, to run once:
pinMode(13, INPUT);
pinMode(12, INPUT);
//pinMode(10, INPUT);
pinMode(11, INPUT);
Serial.begin(9600);

}

void loop() {
  int a = digitalRead(11);
int b = digitalRead(12);
int c = digitalRead(13);
//int d = digitalRead(11);
  Serial.print(a);
  Serial.print(" ");
  Serial.print(b);
  Serial.print(" ");
  Serial.print(c);
 // Serial.print(" ");
 // Serial.print(d);
  Serial.print("\n");
  delay(1000);
  
  
  // put your main code here, to run repeatedly:

}
