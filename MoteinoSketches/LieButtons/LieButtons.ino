
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        51    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network


const byte PassCodeLength = 4;
byte PassCode[] = {6, 3, 6, 4};

// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  byte PassCode[PassCodeLength];
  byte Lights[7];
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int CorrectPassCode = 5101;
const int ChangePassCode = 5102;
const int Disp = 5103;



byte Lights[] = {A0, 9, 7, 6, 5, 4, 3};
byte Buttons[] = {A7, A6, A5, A4, A3, A2, A1};
const byte N = 7;
byte ON = LOW;
byte OFF = HIGH;
byte IN = LOW;
byte OUT = HIGH;

byte Pressed[N] = {false};
bool dispOn = false;

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

  OutgoingData.Command = 100;
  sendOutgoingData();

  for (int i = 0; i< N; i++)
  {
    pinMode(Lights[i], OUTPUT);
    pinMode(Buttons[i], INPUT);
  }
}


byte ButtonPresses[] = {-1, -1, -1, -1};

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
      Serial.print(" pressed, ButtonPresses=");
      for (int i= 0; i<4; i++)
      {
        Serial.print(ButtonPresses[i]);
        Serial.print(", ");
      }
      Serial.println();
      acceptButtonPress(i);
      checkIfCorrectPassCode();
      Pressed[i] = false;
      dispOn = false;
    }
    //Serial.print(analogRead(Buttons[i]));
    //Serial.print('\t');
  }
  //Serial.println();
}

void checkIfCorrectPassCode()
{
  for (int i=0; i<PassCodeLength; i++)
  {
    if ((PassCode[i]-1) != ButtonPresses[i])
    {
      return;
    }
  }
  Serial.println("Correct!, informing Pope");
  OutgoingData.Command = CorrectPassCode;
  sendOutgoingData();
}

void acceptButtonPress(byte button)
{
  for (int i = 0; i<(PassCodeLength-1); i++)
  {
    ButtonPresses[i] = ButtonPresses[i+1];
  }
  ButtonPresses[PassCodeLength-1] = button;
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
      if (!dispOn)
      {
        digitalWrite(Lights[i], state);
      }
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
    Serial.print("Received: command: ");
    Serial.println(IncomingData.Command);

    switch (IncomingData.Command)
    {
      case Status:
        sendStatus();
        break;
      case Disp:
        disp();
        break;
      case ChangePassCode:
        for (int i=0; i<PassCodeLength; i++)
        {
          PassCode[i] = IncomingData.PassCode[i];
        }
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
}


void disp()
{
  dispOn = true;
  for (int i = 0; i<7; i++)
  {
    digitalWrite(Lights[i], IncomingData.Lights[i]);
  }
}

void sendStatus()
{
  OutgoingData.Command = Status;
  for (int i=0; i<PassCodeLength; i++)
  {
    OutgoingData.PassCode[i] = PassCode[i];
  }

  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
