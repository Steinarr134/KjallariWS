//=========RAdio=========================================
// for the radio
#include <RFM69.h>    
#include <SPI.h>
#define NODEID        170    //unique for each node on same network   
#define NETWORKID     7  //the same on all nodes that talk to each other
//Match frequency to the hardware version of the radio on your Moteino (uncomment one):
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define SERIAL_BAUD   9600
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network
typedef struct{
  int Command;
  int TimeLeft;
  int Temperature;
} Payload;
Payload OutgoingData;
Payload IncomingData;
byte DataLen = sizeof(IncomingData);
byte BaseID = 1;

// operating variables
const int Status = 99;
const int BombIsDiffused = 17001;
const int BombTotallyExploded = 17002;
const int PleaseSendTimeInfo = 17003;

//===========================================================================================



////Pin connected to DS of 74HC595
int dataPin = 3;
//Pin connected to ST_CP of 74HC595
int latchPin = 4;
//Pin connected to SH_CP of 74HC595
int clockPin = 5;


int janei=1;
int piezoPin = 7;

const int buttonPin = 6;
int buttonState = 0;
//=========Banana tengi=========================================
int analogPin1 = 0;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin2 = 1;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin3 = 2;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin4 = 3;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin5 = 4;     // potentiometer wiper (middle terminal) connected to analog pin 3

int val1,val2,val3,val4,val5;           // variable to store the value read

//beint á móti
// 685 882 402 93 829

//Eftirfarandi gildi segja til um hvaða samsetning niðri er rétt ___________________________________________________________________________________________________________________________________
int rett1=89;
int rett2=896;
int rett3=931;
int rett4=92;
int rett5=882;
//==============================================================
unsigned long TimeLeft;  // timinn sem vid faum ur pafanum
unsigned long Timibyrjar, Timataka;

//i er fjoldi pera sem er kveikt 'a
int i = 10;
int fjoldiPera = 10;
int tempTimataka = 0;
void setup() {
  // ================RADIO==================
  //VIRKAR EKKI MEÐ ARDUINO
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
  //========================================
  
  //set pins to output so you can control the shift register
  Serial.begin(9600);  
  pinMode(latchPin, OUTPUT);

  
}

int getTimeLeftFromPope(){
 /* OutgoingData.Command = PleaseSendTimeLeft;
  bool success = sendData();
  if (success){
    while(!radio.receiveDone())
    IncomingData = *(Payload*)radio.DATA;
    return radio.TimeLeft;
  }
  else{
    return 30;
  }*/

  Serial.flush();
  Serial.println("what is TimeLeft?");
  delay(100);
  while (!Serial.available())
  delay(50);
  int a = Serial.parseInt();
  Serial.print("Starting with Timeleft: ");
  Serial.println(a);
  delay(500);
  return a;
}

void loop() {
  // count from 0 to 255 and display the number 
  // on the LEDs
  buttonState = digitalRead(buttonPin);
  //if using button:  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
  if(buttonState == 1){

  //fá tíma sem er eftir frá páfa _________________________________________________________________________________________________________________________________________________
  TimeLeft = getTimeLeftFromPope();
    //TimeLeft=90;
  Timibyrjar= millis();
  
  while(i>0){
  Timataka=floor((millis() - Timibyrjar)/1000);

  //BANANATENGI======================================
  val1 = analogRead(analogPin1);    // read the input pin
  val2 = analogRead(analogPin2);    // read the input pin
  val3 = analogRead(analogPin3);    // read the input pin
  val4 = analogRead(analogPin4);    // read the input pin
  val5 = analogRead(analogPin5);    // read the input pin
  //=====================================================

  i = ceil((1 - float(Timataka)/float(TimeLeft)) * fjoldiPera) ;
  
  Serial.print(i);
  Serial.print("        ");
  Serial.print(Timataka);
  Serial.println("        ");
  

  if(rett1-10< val1 && val1 <rett1+10 && val2>rett2-10 && val2<rett2+10
      && val3>rett3-10 && val3<rett3+10 && val4>rett4-10 && val4<rett4+10
      && val5>rett5-10 && val5<rett5+10 )
  {
    // senda a pafa ad buid se ad aftengja sprengju_____________________________________________________________________________________________________________________________________________
    tellPopeWin();
    while(true)
    {
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
// senda a pafa ad timinn se buinn og sprengjan springur_____________________________________________________________________________________________________________________________________________
  tellPopeLose();

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
// if using button:
}





























//forrit sem þarf ekki að hugsa um
//samt nauðsynleg

// =====================útvarpsföll============RADIO==============================
void checkOnRadio()
{
   if (radio.receiveDone())
  {
    if (radio.SENDERID == BaseID)
    {
      IncomingData = *(Payload*)radio.DATA;
      if (radio.ACKRequested())
      {
        radio.sendACK();
      }
      //Serial.print("Received: command: ");
      //Serial.println(IncomingData.Command);
      switch (IncomingData.Command) 
      {
        case Status:
          sendStatus();
          break;

      }
    }
  }
}

void sendStatus()
{
  //Serial.println("sending statuts");
  OutgoingData.Command = Status;
  OutgoingData.Temperature = getTemperature();
  radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),DataLen);
}
bool sendData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),DataLen);
}

byte getTemperature()
{
  return 0; /// vantar
}

void tellPopeWin()
{
  //do something
  //kalla a thetta thegar vid vinnum
  Serial.println("u win");
//  OutgoingData.Command = BombIsDiffused;
//  sendData();
}

void tellPopeLose()
{
  //do something
  //kalla a thetta thegar vid vinnum
  Serial.println("u lose");
//  OutgoingData.Command = BombIsDiffused;
//  sendData();
}
//=====================================================================================


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
