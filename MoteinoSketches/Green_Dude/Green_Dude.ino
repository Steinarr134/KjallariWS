
// for the temperature sensor:
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 6 
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        11    //unique for each node on same network   
#define NETWORKID     7  //the same on all nodes that talk to each other
//Match frequency to the hardware version of the radio on your Moteino (uncomment one):
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define SERIAL_BAUD   9600
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network
typedef struct {
  unsigned int Command;
  byte Lights[7];
  byte Temperature;
  byte PassCode[7];
} Payload;
Payload OutgoingData;
Payload IncomingData;
byte DataLen = 10;
byte BaseID = 1;

// operating variables
const int CorrectPassCode = 1103;
const int Status = 99;
const int Disp = 1101;
const int SetPassCode = 1102;

byte CorrectSwitchState[] = { -1, -1, -1, -1, -1, -1, -1};

static byte RedLedFeadBackPos = 7;
static byte GreenLedFeadBackPos = 15;
static byte RedLedPos[] = {14, 0, 1, 2, 3, 4, 5};
static byte GreenLedPos[] = {6, 13, 8, 9, 10, 11, 12};
static byte SwitchPin[] = {A0, A1, A2, A3, A4, A5, A6};
byte InputPin = 3;
byte ClockPin = 5;
byte LatchPin = 4;
boolean Register[] = {0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,} ;

byte SimaPin = 7;



void setup() {
  sensors.begin();
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
  for (byte i = 0; i < 7; i++)
  {
    pinMode(SwitchPin[i], INPUT);
  }
  pinMode(ClockPin, OUTPUT);
  pinMode(LatchPin, OUTPUT);
  pinMode(InputPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("Here We GO!!");
  for (byte i = 0; i < 16; i++)
  {
    Register[i] = 0;
  }
  writeRegister();
  // put your setup code here, to run once:
  pinMode(SimaPin, INPUT);

}
byte CurrentSwitchState[] = {0, 0, 0, 0, 0, 0, 0};
byte OldSwitchState[] = {0, 0, 0, 0, 0, 0, 0};
unsigned long LastCheckTime = 0;
int CheckInterval = 25;
unsigned long LastCheckPhoneTime = 0;
int CheckPhoneInterval = 150;
unsigned long LastSendCorrectTime = 0;

void loop()
{
  if (millis() - LastCheckTime > CheckInterval)
  {
    checkOnSwitches();
    if (!currentAndOldAreTheSame())
    {
      //Serial.println("SomeThingChanged!");
      write2Leds();
      for (byte i = 0; i < 7; i++)
      {
        //      Serial.print(CurrentSwitchState[i]);
        //      Serial.print("  ");
        OldSwitchState[i] = CurrentSwitchState[i];
        //Serial.println(OldSwitchState[i]);
      }
      //Serial.println();
      //printRegister();
      /*
        if (currentAndCorrectAreTheSame())
        {
         sendMessageAboutCorrect();
        }*/

    }

    LastCheckTime = millis();
  }
  if (digitalRead(SimaPin) == LOW && millis() - LastCheckPhoneTime > CheckPhoneInterval)
  {
    int a = Register[GreenLedFeadBackPos] + Register[RedLedFeadBackPos];
    if (currentAndCorrectAreTheSame())
    {
      Register[GreenLedFeadBackPos] = 1;
      Register[RedLedFeadBackPos] = 0;
      sendMessageAboutCorrect();
    } else {
      Register[GreenLedFeadBackPos] = 0;
      Register[RedLedFeadBackPos] = 1;
    }
    if (a != 1)
    {
      writeRegister();
    }
    else
    {
      //sendStatus();
    }
    LastCheckPhoneTime = millis();
  } else if (millis() - LastCheckPhoneTime > CheckPhoneInterval + 250) {
    int a = Register[GreenLedFeadBackPos] + Register[RedLedFeadBackPos];
    Register[GreenLedFeadBackPos] = 0;
    Register[RedLedFeadBackPos] = 0;
    if (a != 0)
    {
      writeRegister();
    }
    LastCheckPhoneTime = millis();
  }
  checkOnRadio();
}

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
        case SetPassCode:
          setPassCode();
          break;
      }
    }
  }
}

void disp()
{
  for (byte i = 0; i < 7; i++)
  {
    CurrentSwitchState[i] = IncomingData.Lights[i];
  }
  write2Leds();
}

void setPassCode()
{
  for (byte i = 0; i < 7; i++)
  {
    CorrectSwitchState[i] = IncomingData.PassCode[i];
  }
}

void sendStatus()
{
  Serial.println("sending status");
  OutgoingData.Command = Status;
  for (byte i = 0; i < 7; i++)
  {
    OutgoingData.Lights[i] = CurrentSwitchState[i];
    OutgoingData.Passcode[i] = CorrectSwitchState[i];
  }
  OutgoingData.Temperature = getTemperature();
  if (!sendOutgoing())
    Serial.println("No ack recieved");
}

int getTemperature()
{
  sensors.requestTemperatures();
  delay(20);
  return sensors.getTempCByIndex(0);
}

void sendMessageAboutCorrect()
{
  if (millis() - LastSendCorrectTime > 5000)
  {
    OutgoingData.Command = CorrectPassCode;
    Serial.println("correct");
    if (!sendOutgoing())
      Serial.println("No ack");
    LastSendCorrectTime = millis();
    Serial.println("message about correct sent");
  }
}

bool sendOutgoing()
{
  return radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), DataLen);
}

void writeRegister()
{
  digitalWrite(LatchPin, LOW);
  for (byte i = 0; i < 16; i++)
  {
    digitalWrite(ClockPin, LOW);
    digitalWrite(InputPin, Register[i]);
    digitalWrite(ClockPin, HIGH);
  }
  digitalWrite(LatchPin, HIGH);
}

void printRegister()
{
  for (byte i = 0; i < 16; i++)
  {
    Serial.print(Register[i]);
    Serial.print("  ");
  }
  Serial.println();


}

void write2Leds()
{
  for (byte i = 0; i < 7; i++)
  {
    if (CurrentSwitchState[i] == 255)

    {
      Register[RedLedPos[i]] = 1;
      Register[GreenLedPos[i]] = 0;
    }
    else if (CurrentSwitchState[i] == 0)
    {
      Register[RedLedPos[i]] = 0;
      Register[GreenLedPos[i]] = 0;
    }
    else if (CurrentSwitchState[i] == 1)
    {
      Register[RedLedPos[i]] = 0;
      Register[GreenLedPos[i]] = 1;
    }
    else if (CurrentSwitchState[i] == 2)
    {
      Register[RedLedPos[i]] = 1;
      Register[GreenLedPos[i]] = 1;
    }
  }
  writeRegister();
}

boolean currentAndCorrectAreTheSame()
{
  for (byte i = 0; i < 7; i++)
  {
    if (CurrentSwitchState[i] != CorrectSwitchState[i])
    {
      return 0;
    }
  }
  return 1;
}

boolean currentAndOldAreTheSame()
{
  //Serial.print(" Checking: ");
  for (byte i = 0; i < 7; i++)
  {
    //    Serial.print(CurrentSwitchState[i]);
    //    Serial.print("  ");
    //    Serial.print(OldSwitchState[i]);
    //    Serial.print("  ");
    if (CurrentSwitchState[i] != OldSwitchState[i])
    {
      return 0;
    }
  }
  return 1;
}

void checkOnSwitches()
{
  //Serial.print("Switches:  ");
  for (byte i = 0; i < 7; i++)
  {
    int value = analogRead(SwitchPin[i]);
    if (value < 250)
    {
      CurrentSwitchState[i] = 1;
    }
    else if (value < 750)
    {
      CurrentSwitchState[i] = 0;
    }
    else
    {
      CurrentSwitchState[i] = 255;
    }
    //    Serial.print(CurrentSwitchState[i]);
    //    Serial.print("  ");
  }
  //Serial.println();
}

