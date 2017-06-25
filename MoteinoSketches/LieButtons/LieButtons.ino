
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        7    //unique for each node on same network
#define NETWORKID     51  //the same on all nodes that talk to each other
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
  byte Lights[8];
  long Uptime;
  
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Disp = 5101;


byte Lights[] = {3, 4, 5, 6, 7, 9, A0};
byte Buttons[] = {A1, A2, A3, A4, A5, A6, A7};
const byte N = 7;
byte ON = LOW;
byte OFF = HIGH;
byte IN = LOW;
byte OUT = HIGH;

byte Pressed[N] = {false};

void setup() {
  // initiate Serial port:
  Serial.begin(115200);

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);


  ////////////////// put your code here

  for (int i = 0; i< N; i++)
  {
    pinMode(Lights[i], OUTPUT);
    pinMode(Buttons[i], INPUT);
  }
}

void loop()
{
  checkOnButtons();
  checkOnRadio();
  //delay(100);
  for (int i = 0; i< N; i++)
  {
    if (Pressed[i])
    {
      Serial.print("Button ");
      Serial.print(i);
      Serial.println(" pressed");
      Pressed[i] = false;
    }
    //Serial.print(analogRead(Buttons[i]));
    //Serial.print('\t');
  }
  //Serial.println();
}


byte laststate[N] = {OUT};
unsigned lastbuttontime = 0;
byte havenotified[N] = {false};

void checkOnButtons()
{
  if (millis() - lastbuttontime > 20)
  {
    lastbuttontime = millis();
    for (int i = 0; i< N; i++)
    {
      byte state = (analogRead(Buttons[i]) > 1000);
      if (state == laststate[i])
      {
        if (state == IN)
        {
          if (!havenotified[i])
          {
            Pressed[i] = true;
            havenotified[i] = true;
          }
        }
        else
        {
          havenotified[i] = false;
        }
      }
      
     laststate[i] = state;
      
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
      case Disp:
        disp();
        break;
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
}


void disp()
{
  Serial.println("demo1");
}

void sendStatus()
{
  OutgoingData.Command = Status;
  OutgoingData.Uptime = millis();

  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
