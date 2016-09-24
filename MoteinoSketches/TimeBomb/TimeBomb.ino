
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        170    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network


// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  unsigned long TimeLeft;
  int Temperature;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// operating variables
const int Status = 99;
const int BombIsDiffused = 17001;
const int BombTotallyExploded = 17002;
const int Reset = 98;
const int Demo1 = 50;

////Pins
byte DataPin = 3;
byte LatchPin = 4;
byte ClockPin = 5;
byte ButtonPin = 6;
byte PiezoPin = 7;

byte BananaPins[] = {A0, A1, A2, A3, A4};

int CorrectValues[] = {89, 896, 931, 92, 882};

const byte LightPos[] = {1, 2, 3, 4, 5, 6, 7, 8};  //??????????
const byte OtherLight = 9;                         // ??????????
byte _Register[16] = {0};
int LedBlinkSpeed = 1000;
int NofLeds = 10;

void setup() {
  // initiate Serial port:
  Serial.begin(115200);

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  // init pins:
  pinMode(DataPin, OUTPUT);
  pinMode(LatchPin, OUTPUT);
  pinMode(DataPin, OUTPUT);
  pinMode(PiezoPin, OUTPUT);
  pinMode(ButtonPin, OUTPUT);
  for (byte i = 0; i < 5; i++)
    pinMode(BananaPins[i], INPUT);
  Serial.println("started");
}


unsigned long XplosionTime = 60000;
unsigned long ChestOpeningTime = 0;


void loop()
{
  if (chestHaseBeenOpened() && millis() < XplosionTime)
  {
    checkOnBananaPins();
    controlLeds();
  }
  checkOnRadio();
}

void bombDiffused()
{
  Serial.println("BOMB DIFFUSED");
}


unsigned long _controlLedsLastBlinkTime = 0;
bool _controlLedsBlinkerLed = false;
void controlLeds()
{
  unsigned long t = millis();
  if ((t -_controlLedsLastBlinkTime) > LedBlinkSpeed)
  {
    _controlLedsLastBlinkTime = t;
    byte leds_remaining = (t - ChestOpeningTime)*NofLeds/(XplosionTime - ChestOpeningTime + 1);
    Serial.print("Leds remaining:");
    Serial.println(leds_remaining);
    for (int i = 0; i < NofLeds; i++)
    {
      _Register[LightPos[i]] = (i < leds_remaining);
    }
    _controlLedsBlinkerLed = !_controlLedsBlinkerLed;
    _Register[leds_remaining] = _controlLedsBlinkerLed;
    writeRegister();
  }
}


byte _BananaPinCorrectTolerance = 10;
unsigned long _checkOnBananaPinsLastCheckTime = 0;
void checkOnBananaPins()
{
  if (millis() - _checkOnBananaPinsLastCheckTime > 25)
  {
    for (byte i = 0; i<5; i++)
    {
      if (absdiff(analogRead(BananaPins[i]), CorrectValues[i]) > _BananaPinCorrectTolerance)
        return;
    }
    bombDiffused();
  }
}


bool _chestIsOpen = false;
unsigned long chestHaseBeenOpenedLastCheckTime = 0;
bool chestHaseBeenOpened()
{
  if(_chestIsOpen)
  {
    return true;
  }
  else
  {
    if (millis() - chestHaseBeenOpenedLastCheckTime < 25)
    {
      return false;
    }
    else
    {
      chestHaseBeenOpenedLastCheckTime = millis();
      if (digitalRead(ButtonPin))
      {
        _chestIsOpen = true;
        ChestOpeningTime = millis();
        Serial.print("ChestOpened");
        return true;
      }
      else
      {
        return false;
      }
    }
  }
}





void checkOnRadio()
{
    // if nothing was received then we'll return immediately
   if (radio.receiveDone())
  {
    // receive the data into IncomingData
    IncomingData = *(Payload*)radio.DATA;

    // send ack if requested
    if (radio.ACKRequested())
    {
      radio.sendACK();
    }
    // useful for debugging:
//    Serial.print("Received: command: ");
//    Serial.println(IncomingData.Command);

    switch (IncomingData.Command)
    {
      case Status:
        sendStatus();
        break;
      case Demo1:
        demo1();
        break;
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
}

void demo1()
{
  Serial.println("demo1");
}

void sendStatus()
{
  OutgoingData.Command = Status;

  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
void writeRegister()
{
  byte h = 0;
  byte l = 0;
  for (byte i = 0; i<8; i++)
  {
    h += _Register[i]<<i;
    l += _Register[i+8]<<i;
  }
  digitalWrite(LatchPin, LOW);
  shiftOut(DataPin, ClockPin, h);
  shiftOut(DataPin, ClockPin, l);
  digitalWrite(LatchPin, HIGH);
  printRegister();
}

void printRegister()
{
  for (byte i= 0; i<16; i++)
  {
    Serial.print(_Register[i]);
    Serial.print("  "); 
  }
  Serial.println();
}

int absdiff(int a, int b)
{
  if (a > b)
  {
    return a - b;
  }
  return b - a;
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
