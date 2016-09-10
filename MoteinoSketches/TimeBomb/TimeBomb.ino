
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
int _LedBlinkSpeed = 1000;

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
}


unsigned long XplosionTime = -1;
unsigned long ChestOpeningTime = 0;


void loop()
{
  if (chestHaseBeenOpened())
  {
    checkOnBananaPins();
    controlLeds();
  }
  checkOnRadio();
}


unsigned long _controlLedsLastBlinkTime = 0;
bool _controlLedsBlinkerLed = false;
void controlLeds()
{
  unsigned long t = millis();
  if ((t -_controlLedsLastBlinkTime) > _LedBlinkSpeed)
  {
    byte leds_remaining = (t - ChestOpeningTime)*NofLeds/(XplosionTime - ChestOpeningTime + 1);
    for (int i = 0; i < NofLeds; i++)
    {
      _Register[LightPos[i]] = (i < leds_remaining);
    }
    _controlLedsBlinkerLed = !_controlLedsBlinkerLed;
    _Register[leds_remaining] = _controlLedsBlinkerLed;
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
        return
    }
    bombDiffused();
  }
}


bool _chestIsOpen = false;
unsigned long chestHaseBeenOpenedLastCheckTime = 0;
void chestHaseBeenOpened()
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
  for (int i = 0; i < 8; i++)
  {
    OutgoingData.Numbers[i] = i*i;
  }
  OutgoingData.Uptime = millis();

  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
