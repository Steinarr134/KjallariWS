// --- ALARM
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        37    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
int maxAlarmTime = 2*60*1000 ;    // 2 min

RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network

byte LED = 9;

// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  int Milliseconds;
  long Uptime;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Reset = 98;
const int TogglePin1 = 3701;
const int TogglePin2 = 3702;   // <-- nota thessa skipun
const int SetPin1High = 3703;
const int SetPin1Low = 3704;
const int SetPin2High = 3705;  // <-- og thessar tvaer, hi og lo.
const int SetPin2Low = 3706;   // <--

byte Pin1 = 9;
byte Pin2 = 7;      // PIN 7 --> base á npn darlington. 7.high== sirena ON, 7.low==sirena OFF

byte State[2] = {0};
byte Pins[] = {Pin1, Pin2};

// Fail-safe: til ad alarm festist ekki i gangi. maxAlarmTime skilgreint i #define efsts
boolean alarmOn = false;
unsigned long int alarmOnTime = 0;     

void setup() {
  // initiate Serial port:
  Serial.begin(115200);

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  pinMode(Pin1, OUTPUT);
  pinMode(Pin2, OUTPUT);
  digitalWrite(Pin1, LOW);
  digitalWrite(Pin2, LOW);


//  digitalWrite(Pin1, HIGH);
//  delay(250);
//  digitalWrite(Pin1, LOW);
//  digitalWrite(Pin2, HIGH);
//  delay(250);
//  digitalWrite(Pin2, LOW);
  Toggle(0, 2000);
  Toggle(1, 2000);
  Serial.println("Started");

}

void loop()
{

  ////////////////// put your code here as well


  // the loop has to check on the radio and act to commands received. The radio receives in the
  // background but doesn't send back an ack. The radio also only holds 1 data packet so it will
  // overwrite if it receives a new one. If nothing has been received checkOnRadio() will return
  // immediately.
  checkOnRadio();


  // Baett vid eftira. Fail-safe, maxAlarmTime:
  if(State[1] && !alarmOn)
  {
    alarmOn = true;
    alarmOnTime=millis();
  }
  if(alarmOn && (millis() - alarmOnTime >= maxAlarmTime))
  {
    digitalWrite(Pins[1], LOW);   // slökkva a alarm
    alarmOnTime = 0;
    alarmOn = false;
  }

}

void _Toggle(byte pin)
{
  State[pin] = !State[pin];
  /*Serial.print("Flipping pin: ");
  Serial.print(Pins[pin]);
  Serial.print(" to ");
  Serial.println(State[pin]);
  delay(100);*/
  digitalWrite(Pins[pin], State[pin]);
}

void Toggle(byte pin, int t)
{
  _Toggle(pin);
  delay(t);
  _Toggle(pin);
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
        delay(100);
        asm volatile (" jmp 0");
        break;
      case TogglePin1:
        Toggle(0, IncomingData.Milliseconds);
        break;
      case TogglePin2:
        Toggle(1, IncomingData.Milliseconds);
        break;
      case SetPin1High:
        digitalWrite(Pins[0], HIGH);
        break;
      case SetPin1Low:
        digitalWrite(Pins[0], LOW);
        break;
      case SetPin2High:
        digitalWrite(Pins[1], HIGH);
        break;
      case SetPin2Low:
        digitalWrite(Pins[1], LOW);
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
  OutgoingData.Uptime = millis();
  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
