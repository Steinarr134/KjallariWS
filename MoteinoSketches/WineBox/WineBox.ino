#include <Wire.h>
#include <TroykaIMU.h>
Accelerometer accel;

// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        10    //unique for each node on same network
#define NETWORKID     1  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "0123456789abcdef" //exactly the same 16 characters/bytes on all nodes!
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network


// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  byte Numbers[8];
  long Uptime;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Demo1 = 23;



int LED = 9;
long Time2Solve = 15000;

boolean can_be_solved = true;

byte Sesam = 3;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Wire.begin();
  accel.begin();
  pinMode(Sesam, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  delay(500);
  digitalWrite(LED, LOW);

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
}



byte isUpsideDown()
{
  float z = accel.readAZ();
  if (z > 8)
  {
    can_be_solved = true;
  }
  return (z < -8);
}

unsigned long last_check_time = 0;
unsigned long last_time_not_upside_down = 0;
void checkOnSensor()
{
  if (millis() - last_check_time > 20)
  {
    if (!isUpsideDown())
    {
      last_time_not_upside_down = millis();
    }
    else if (can_be_solved && (millis() - last_time_not_upside_down > Time2Solve))
    {
      problemSolved();
    }
  }
}

unsigned long stop_opening_time = 0;
boolean stop_opening_flag = false;

void stopOpeningLid()
{
  if (stop_opening_flag)
  {
    if (millis() - stop_opening_time > 200)
    {
      stop_opening_flag = false;
      digitalWrite(Sesam, LOW);
    }
  }
}

void problemSolved()
{
 Serial.println("SOLVED"); 
 digitalWrite(Sesam,HIGH);
 stop_opening_time = millis();
 stop_opening_flag = true;
 can_be_solved = false;
}




void loop() {
  // put your main code here, to run repeatedly:

  checkOnSensor();
  stopOpeningLid();
  checkOnRadio();
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
      case Reset:
        arm volatile (" jmp 0");
        break;
      case SetTime2Solve:

        
        break;
      case Open:
        
        break;
      case :
        
        break;
      case Reset:
        
        
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
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
