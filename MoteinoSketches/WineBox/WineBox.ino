#include <Wire.h>
#include <TroykaIMU.h>
Accelerometer accel;

// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        24    //unique for each node on same network
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
  unsigned long Uptime;
  int BatteryStatus;
  int X;
  int Y;
  int Z;
  int Time2Solve;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Reset = 98;
const int OpenYourself = 2401;
const int IWasSolved = 2402;
const int SetTime2Solve = 2403;

int LED = 9;
long Time2Solve = 10000;

boolean can_be_solved = true;

byte Sesam = 4;
byte BatteryPin = A2;

const bool OPEN = HIGH;
const bool CLOSED = LOW;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Wire.begin();
  accel.begin();
  pinMode(Sesam, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(BatteryPin, INPUT);
  digitalWrite(LED, HIGH);
  digitalWrite(Sesam, CLOSED);
  
  delay(500);
  digitalWrite(LED, LOW);

  

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  Serial.println("Hello, let's get started");
}


float zthresh = -9.7;
float xthresh = 0.50;
float ythresh = 0.50;


bool isUpsideDown()
{
  //Serial.println("1");
  float z = accel.readAZ();
  //Serial.println("2");
  float x = accel.readAX();
  float y = accel.readAY();
  //Serial.println(z);
  return ((z < zthresh) && (abs(x) < xthresh) && (abs(y) < ythresh));
}

unsigned long last_check_time = 0;
unsigned long last_time_not_upside_down = 0;
boolean has_been_turned_back;
void checkOnSensor()
{
  if (millis() - last_check_time > 100)
  {
    last_check_time = millis();
    if (can_be_solved && isUpsideDown() && capsCharged())
    {
      problemSolved();
    }
  }
}

unsigned long stop_opening_time = 0;
boolean stop_opening_flag = false;

bool capsCharged()
{
  return analogRead(BatteryPin) > 900;
}

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
 OutgoingData.Command = IWasSolved;
 sendOutgoingData();
 can_be_solved = false;
  open_lid();
}

void open_lid()
{
 digitalWrite(Sesam, OPEN);
 delayWithRadio(500);
 digitalWrite(Sesam, CLOSED);
 
}
void delayWithRadio(unsigned long t){
  unsigned long now = millis();
  while (millis() - now < t)
  {
    checkOnRadio();
  }
}

long blinkt = -4000;
bool ledstate = 0;

void loop() {
  // put your main code here, to run repeatedly:

  if (millis() - blinkt > 500)
  {
    ledstate = !ledstate;
    digitalWrite(9, ledstate);
  }
  checkOnSensor();
  stopOpeningLid();
  checkOnRadio();
  checkOnSerial();
}

void checkOnSerial()
{
  if (Serial.available())
  {
    char c = Serial.read();
    if (c == 'z')
    {
      Serial.print("X  -  ");
      Serial.println(accel.readAX());
      Serial.print("Y  -  ");
      Serial.println(accel.readAY());
      Serial.print("Z  -  ");
      Serial.println(accel.readAZ());
    }
    else if (c == 's')
    {
      Serial.print("BatteryStatus: ");
      Serial.println(analogRead(BatteryPin));
      Serial.print("has_been_tured_back:");
      Serial.println(has_been_turned_back);
      Serial.print("time_until_solved: ");
      Serial.println(millis() - last_time_not_upside_down);
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
    //Serial.print("Received: command: ");
    //Serial.println(IncomingData.Command);

    switch (IncomingData.Command)
    {
      case Status:
        sendStatus();
        break;
      case Reset:
        asm volatile (" jmp 0");
        break;
      case SetTime2Solve:
        Time2Solve = IncomingData.Time2Solve;
        break;
      case OpenYourself:
        open_lid();
        break;
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
}


void sendStatus()
{
  OutgoingData.Time2Solve = Time2Solve;
  OutgoingData.X = (int)(accel.readAX()*100);
  OutgoingData.Y = (int)(accel.readAY()*100);
  OutgoingData.Z = (int)(accel.readAZ()*100);
  OutgoingData.BatteryStatus = analogRead(BatteryPin);
  OutgoingData.Uptime = millis();
  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
