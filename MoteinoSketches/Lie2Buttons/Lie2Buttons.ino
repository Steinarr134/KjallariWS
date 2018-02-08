

//Radio tings
#include <RFM69.h>
#define NODEID 54
#define NETWORKID 7
#define FREQUENCY RF69_433MHZ
#define ENCRYPTKEY "HugiBogiHugiBogi"
#define SERIAL_BAUD 9600
#define BaseID 1
RFM69 radio;

byte b1 = A0;
byte b2 = A1;


typedef struct{
  int Command;
  byte Temperature;
} Payload;

Payload OutgoingData;
Payload IncomingData;

const int DataLen = sizeof(OutgoingData);

// Command Values:
const int Status = 99;
const int Reset = 98;
const int Button1Pressed = 5401;
const int Button2Pressed= 5402;

void setup() {
  pinMode(b1, INPUT);
  pinMode(b2, INPUT);

  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower();
  radio.encrypt(ENCRYPTKEY);

  Serial.begin(115200);
  Serial.println("HELLO");
   
}

void loop() {

  checkOnRadio();
  
  delay(5);
  if (digitalRead(b1))
  {
    OutgoingData.Command = Button1Pressed;
    sendOutgoing();
    delay(50);
    while (digitalRead(b1))
    {
      delay(10);
    }
    delay(100);
  }
  if (digitalRead(b2))
  {
    OutgoingData.Command = Button2Pressed;
    sendOutgoing();
    delay(50);
    while (digitalRead(b2))
    {
      delay(10);
    }
    delay(100);
  }
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
        case Reset:
          reset();
          break;
      }
    }
  }
}

void reset()
{
  asm volatile(" jmp 0");
}


void sendStatus()
{
  
  //Serial.println("sending status");
  OutgoingData.Command = Status;
  OutgoingData.Temperature = getTemperature();
  if (!sendOutgoing())
    Serial.println("No ack recieved");
}

byte getTemperature()
{
  return (byte)radio.readTemperature(0);
}


bool sendOutgoing()
{
  return radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), DataLen);
}
