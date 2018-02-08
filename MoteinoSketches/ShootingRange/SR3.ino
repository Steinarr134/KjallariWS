// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        31    //unique for each node on same network
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
  int Time;
  int Target;
  byte Colors[5];
  int Sequence[5];
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Reset = 98;
const int Status = 99;
const int SetTime = 3101;
const int TargetHit = 3102;
const int dispColor = 3103;
const int WrongTarget = 3104;
const int MissionComplete = 3105;
const int NewSequence = 3106;
const int PuzzleFinished = 3107;


// Led pinnar
const int G0 = 0;
const int R0 = 1;
const int G1 = 12;
const int R1 = 13;
const int G2 = 18;
const int R2 = 19;
const int G3 = 20;
const int R3 = 21;
const int G4 = 22;
const int R4 = 23;

unsigned int b = 3;
int start = 0;
int Threshold = 500;
const int InitTime = millis();
unsigned long LastChange = 0;
unsigned long Time2Change = 2000;

byte InitLed[] = {1,1,1,1,1};
byte TurnLedOff[] = {0,0,0,0,0};
byte CompleteLed[] = {2,2,2,2,2};
int TargetRead[] = {A0,A1,A2,A3,A4};
int RedLed[] = {R0,R1,R2,R3,R4};
int GreenLed[] = {G0,G1,G2,G3,G4};
int TargetVal[5];
int Sequence[5] = {2,4,3,1,0};
int TargetIndex = 0;
void setup() {
  // initiate radio
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if(HIGH_POWER)
    radio.setHighPower(); // only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
  for(int i=0;i<5;i++)
  {
    pinMode(TargetRead[i], INPUT);
    pinMode(RedLed[i], OUTPUT);
    pinMode(GreenLed[i], OUTPUT);
  }

  displayColors(InitLed);

  Serial.begin(115200);

}

void loop() {
  checkOnRadio();
  for(int i=0;i<5;i++)
  {
      TargetVal[i] = analogRead(TargetRead[i]);
  }
  int maxx = 0;
  int Target = 0;
  for(int i=0;i<5;i++)
  {
    if(TargetVal[i]>maxx){
      maxx = TargetVal[i];
      Target = i;
    }
  }
  if(maxx>Threshold)
  {
    if(Target == Sequence[TargetIndex])
    {
      OutgoingData.Command = TargetHit;
      OutgoingData.Target = Target;
      sendOutgoingData();
      TargetIndex += 1;
      digitalWrite(RedLed[Target],LOW);
      digitalWrite(GreenLed[Target],HIGH);
      delay(200);
    }
    else
    {
      OutgoingData.Command = WrongTarget;
      OutgoingData.Target = Target;
      sendOutgoingData();
      TargetIndex = 0;
      displayColors(TurnLedOff);
      for(int i=0;i<3;i++)
      {
          checkOnRadio();
          digitalWrite(RedLed[Target],HIGH);
          delay(200);
          checkOnRadio();
          digitalWrite(RedLed[Target],LOW);
          delay(200);
      }
      displayColors(InitLed);
    }
  }
  if(TargetIndex == 5)
    {
      for(int i=0;i<10;i++)
      {
        checkOnRadio();
        for(int j=0;j<5;j++)
        {
          digitalWrite(GreenLed[j],HIGH);
        }
        delay(200);
        checkOnRadio();
        for(int j=0;j<5;j++)
        {
          digitalWrite(GreenLed[j],LOW);
          }
        delay(200);
      }
      OutgoingData.Command = MissionComplete;
      sendOutgoingData();
      displayColors(CompleteLed);
      TargetIndex = 0;
      while(true)
        checkOnRadio();
    }
}
// Extra

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
      case SetTime:
        Time2Change=IncomingData.Time;
        break;
      case dispColor:
        displayColors(IncomingData.Colors);
        break;
      case PuzzleFinished:
        haveFun();
        break;
      case Reset:
        asm volatile(" jmp 0");
      case NewSequence:
        for(int i = 0; i<5;i++)
        {
          Sequence[i] = IncomingData.Sequence[i];
        }
        break;
      default:
        Serial.print("Received unknown Command: ");
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

void displayColors(byte colors[])
{
  for(int i=0;i<5;i++)
  {
    if(colors[i] == 0)
    {
      digitalWrite(RedLed[i], LOW);
      digitalWrite(GreenLed[i], LOW);
    }
    if(colors[i] == 1)
    {
      digitalWrite(RedLed[i], HIGH);
      digitalWrite(GreenLed[i], LOW);
    }
    if(colors[i] == 2)
    {
      digitalWrite(RedLed[i], LOW);
      digitalWrite(GreenLed[i], HIGH);
    }
    if(colors[i] == 3)
    {
      digitalWrite(RedLed[i], HIGH);
      digitalWrite(GreenLed[i], HIGH);
    }
  }
}

void haveFun()
{
  displayColors(InitLed);
  while(true)
  {
    checkOnRadio();
    for(int i=0;i<5;i++)
    {
      TargetVal[i] = analogRead(TargetRead[i]);
    }
    int maxx = 0;
    int Target = 0;
    for(int i=0;i<5;i++)
    {
      if(TargetVal[i]>maxx){
        maxx = TargetVal[i];
        Target = i;
      }
    }
    if(maxx>Threshold)
    {
      displayColors(TurnLedOff);
      for(int i=0;i<3;i++)
      {
          checkOnRadio();
          digitalWrite(GreenLed[Target],HIGH);
          delay(200);
          checkOnRadio();
          digitalWrite(GreenLed[Target],LOW);
          delay(200);
      }
      displayColors(InitLed);
    }
  }
}

