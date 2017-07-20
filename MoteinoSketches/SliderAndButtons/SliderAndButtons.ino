byte SliderPin = A2;
byte Button1Pin = A0;
byte Button2Pin = A1;

void setup() {
  // put your setup code here, to run once:
  pinMode(SliderPin, INPUT);
  pinMode(Button1Pin, INPUT);
  pinMode(Button2Pin, INPUT);
  Serial.begin(38400);
}

void hexprint(byte b)
{
  if (b < 16)
  {
    Serial.print('0');
  }
  Serial.print(b, HEX);
}

void loop() {
  
  // print slider position in 8-bit resolution
  hexprint(analogRead(SliderPin)/4);
  
  // print button states
  Serial.print(digitalRead(Button1Pin));
  Serial.print(digitalRead(Button2Pin));
  
  // newline character
  Serial.println();

  delay(75);
}
