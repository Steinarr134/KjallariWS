// --- ALARM
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        64    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!

RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network

byte LED = 9;

// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  byte Trigger;
  unsigned long Uptime;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Reset = 98;
const int Triggered = 6401;
const int MonitorTrigger = 6402;
const int StopMonitoring = 6403;


byte TriggerPin = 7;


void setup() {
  // initiate Serial port:
  Serial.begin(115200);

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  pinMode(TriggerPin, INPUT);

  Serial.println("Started");
}

bool MonitorTriggerActive = false;
unsigned long LastTimeTriggerCheck = 0;

void loop()
{
  // the loop has to check on the radio and act to commands received. The radio receives in the
  // background but doesn't send back an ack. The radio also only holds 1 data packet so it will
  // overwrite if it receives a new one. If nothing has been received checkOnRadio() will return
  // immediately.
  checkOnRadio();

  if (MonitorTriggerActive)
  {
    if (millis() - LastTimeTriggerCheck > 10)
    {
      LastTimeTriggerCheck = millis();
      if (digitalRead(TriggerPin))
      {
        sendTriggered();
      }
    }
  }
}

unsigned long LastTimeTriggerSend = 0;

void sendTriggered()
{
  if (millis() - LastTimeTriggerSend > 1000)
  {
    LastTimeTriggerSend = millis();
    OutgoingData.Command = Triggered;
    sendOutgoingData();
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
      case Reset:
        Serial.println("Restarting from sketch");
        delay(50);
        asm volatile (" jmp 0");
        break;
      case MonitorTrigger:
        MonitorTriggerActive = true;
        break;
      case StopMonitoring:
        MonitorTriggerActive = false;
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
}


void sendStatus()
{
  OutgoingData.Command = Status;
  OutgoingData.Uptime = millis();
  OutgoingData.Trigger = digitalRead(TriggerPin);
  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
