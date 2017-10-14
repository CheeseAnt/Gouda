int tempIn = 15;
double R25 = 100000;
float B25 = 3450;
float T25 = 298.15;
float kelv = 293.15;
long R2 = 120100;
float V = 5;
  
void setup() {
  // put your setup code here, to run once:
  pinMode(tempIn, INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  double tempV = analogRead(tempIn);
  tempV = tempV*0.0048828;
  double R1 = -(tempV*R2)/(tempV-V);
  double temp = (1/((log(R1/R25)/B25)+1/T25))-273.15;
  Serial.print("temp: ");
  Serial.print(temp);
  Serial.print("read: ");
  Serial.println(tempV);
  Serial.println(analogRead(tempIn));
  delay(1000);
}
