//Pin connected to ST_CP of 74HC595
int latchPin = 8;
//Pin connected to SH_CP of 74HC595
int clockPin = 12;
////Pin connected to DS of 74HC595
int dataPin = 11;

int janei=1;
int piezoPin = 6;

const int buttonPin = 2;
int buttonState = 0;
//=========Banana tengi=========================================
int analogPin1 = 0;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin2 = 1;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin3 = 2;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin4 = 3;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin5 = 4;     // potentiometer wiper (middle terminal) connected to analog pin 3

int val1,val2,val3,val4,val5;           // variable to store the value read

//gamalt
//696 898 407 90 993 126,5
//nytt
// 685 882 402 93 829
int rett1=685;
int rett2=882;
int rett3=402;
int rett4=93;
int rett5=829;
//==============================================================
unsigned long TimeLeft = 30;  // timinn sem vid faum ur pafanum
unsigned long TimeToSplit = TimeLeft/ 10; // hofum 2 tvi tad eru adeins t led perur
unsigned long Timibyrjar, Timataka;

int i = 10;
int fjoldiPera = 10;
int tempTimataka = 0;
void setup() {
  //set pins to output so you can control the shift register
  Serial.begin(9600);  
  pinMode(latchPin, OUTPUT);
  //pinMode(clockPin, OUTPUT);
  //pinMode(dataPin, OUTPUT);
  
  Timibyrjar= millis();
}

void loop() {
  // count from 0 to 255 and display the number 
  // on the LEDs
  buttonState = digitalRead(buttonPin);
  if(buttonState == 1)
  
  while(i>0){
  Timataka=floor((millis() - Timibyrjar)/1000);

  //BANANATENGI======================================
  val1 = analogRead(analogPin1);    // read the input pin
  val2 = analogRead(analogPin2);    // read the input pin
val3 = analogRead(analogPin3);    // read the input pin
val4 = analogRead(analogPin4);    // read the input pin
val5 = analogRead(analogPin5);    // read the input pin
//=====================================================
  float bla = Timataka*100;
  float blabla = TimeLeft*100;
  
  
  i = ceil((1 - float(Timataka)/float(TimeLeft)) * fjoldiPera) ;
  
  Serial.print(i);
  Serial.print("        ");
  Serial.print(Timataka);
Serial.print("        ");
  Serial.println(((bla/blabla)));
  

  if(rett1-10< val1 && val1 <rett1+10 && val2>rett2-10 && val2<rett2+10
&& val3>rett3-10 && val3<rett3+10 && val4>rett4-10 && val4<rett4+10
&& val5>rett5-10 && val5<rett5+10 )
{
  while(true){
  Serial.print("meistaraverk");
      digitalWrite(latchPin, LOW);

      shiftOut(dataPin, clockPin, 1); 
      shiftOut(dataPin, clockPin, 0); 

      digitalWrite(latchPin, HIGH);
  }
  break;
}

  if(Timataka % 2 == 0 ){
     if(janei==1){
      tempTimataka = Timataka;
      // tone(piezoPin, 1000, 100);
       janei=0;
     }
     if(abs(tempTimataka - Timataka)> 1){
      tone(piezoPin, 500, 100);
      janei=1;
     }
    if(i>8){
      digitalWrite(latchPin, LOW);
      shiftOut(dataPin, clockPin, ceil(pow(2,i-6)-2)); 
      shiftOut(dataPin, clockPin, ceil(pow(2,i)-1)); 
      digitalWrite(latchPin, HIGH);
    }
    else{
     digitalWrite(latchPin, LOW);
      // shift out the bits:
      shiftOut(dataPin, clockPin, 2); 
      shiftOut(dataPin, clockPin, ceil(pow(2,i)-1)); 
      Serial.println(pow(2,8));
      //take the latch pin high so the LEDs will light up:
      digitalWrite(latchPin, HIGH);
    }
  }
  else{

        if(i>8){
      digitalWrite(latchPin, LOW);

      shiftOut(dataPin, clockPin, ceil(pow(2,i-7)-2)); 
      shiftOut(dataPin, clockPin, ceil(pow(2,i)-1)); 

      digitalWrite(latchPin, HIGH);
    }
    else{
    digitalWrite(latchPin, LOW);
      // shift out the bits:
      
      shiftOut(dataPin, clockPin,  2);  
      shiftOut(dataPin, clockPin, ceil(pow(2,i-1)-1));  
  
      //take the latch pin high so the LEDs will light up:
      digitalWrite(latchPin, HIGH);
    }
  }
  }
  while(i<1){
    Timataka=floor((millis() - Timibyrjar)/1000);

      //BANANATENGI======================================
  val1 = analogRead(analogPin1);    // read the input pin
  val2 = analogRead(analogPin2);    // read the input pin
val3 = analogRead(analogPin3);    // read the input pin
val4 = analogRead(analogPin4);    // read the input pin
val5 = analogRead(analogPin5);    // read the input pin
//=====================================================

if(rett1-10< val1 && val1 <rett1+10 && val2>rett2-10 && val2<rett2+10
&& val3>rett3-10 && val3<rett3+10 && val4>rett4-10 && val4<rett4+10
&& val5>rett5-10 && val5<rett5+10 )
{
  Serial.print("meistaraverk");
      digitalWrite(latchPin, LOW);
      shiftOut(dataPin, clockPin, 1); 
      shiftOut(dataPin, clockPin, 0); 
      digitalWrite(latchPin, HIGH);
      break;
}
    if(Timataka % 2 == 0 ){
      digitalWrite(latchPin, LOW);
      shiftOut(dataPin, clockPin, 14); 
      shiftOut(dataPin, clockPin, 255); 
      digitalWrite(latchPin, HIGH);
  }
  else{
      digitalWrite(latchPin, LOW);
      shiftOut(dataPin, clockPin, 0); 
      shiftOut(dataPin, clockPin, 0); 
      digitalWrite(latchPin, HIGH);
  }  
  }
}

void shiftOut(int myDataPin, int myClockPin, byte myDataOut) {
  // This shifts 8 bits out MSB first, 
  //on the rising edge of the clock,
  //clock idles low

//internal function setup
  int i=0;
  int pinState;
  pinMode(myClockPin, OUTPUT);
  pinMode(myDataPin, OUTPUT);

 //clear everything out just in case to
 //prepare shift register for bit shifting
  digitalWrite(myDataPin, 0);
  digitalWrite(myClockPin, 0);

  //for each bit in the byte myDataOut�
  //NOTICE THAT WE ARE COUNTING DOWN in our for loop
  //This means that %00000001 or "1" will go through such
  //that it will be pin Q0 that lights. 
  for (i=7; i>=0; i--)  {
    digitalWrite(myClockPin, 0);

    //if the value passed to myDataOut and a bitmask result 
    // true then... so if we are at i=6 and our value is
    // %11010100 it would the code compares it to %01000000 
    // and proceeds to set pinState to 1.
    if ( myDataOut & (1<<i) ) {
      pinState= 1;
    }
    else {  
      pinState= 0;
    }

    //Sets the pin to HIGH or LOW depending on pinState
    digitalWrite(myDataPin, pinState);
    //register shifts bits on upstroke of clock pin  
    digitalWrite(myClockPin, 1);
    //zero the data pin after shift to prevent bleed through
    digitalWrite(myDataPin, 0);
  }

  //stop shifting
  digitalWrite(myClockPin, 0);
}
