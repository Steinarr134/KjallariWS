/*
 * 
 * comunication is on the form: '(SliderPosition)(ButtonStates)\n'
 * 
 * encoded in hex, for example:
 * 
 * '6C01\n'  means slider is in position 6C=108 out of 255 button 1 is 0 and button 2 is 1
 * 
 * 
 * 
 */



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

  // slow it down a bit
  delay(10);
  
  // print slider position in 8-bit resolution
  hexprint(analogRead(SliderPin)/4);
  
  // print button states
  Serial.print(digitalRead(Button1Pin));
  Serial.print(digitalRead(Button2Pin));
  
  // newline character
  Serial.println();
}
