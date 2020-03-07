// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        5    //unique for each node on same network
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
  byte ActiveDoor;
  byte PassCode1[4];
  byte PassCode2[4];
  unsigned long Uptime;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Reset = 98;
const int SetPassCode = 501;
const int SolveDoor1 = 503;
const int SolveDoor2 = 504;
const int OpenDoors = 505;
const int SetActiveDoor = 506;
const int Solved = 507;
const int PlayHint1 = 511;
const int PlayHint2 = 512;
const int PlayHint3 = 513;

byte passcode1[4] =  {4,1,3,2}; //{1,2,3,4}; //
byte passcode2[4] = {1,3,4,1}; 
byte code[4]; 

const int takki1 = 4; //8;//5
const int takki2 = 5; //9;//6
const int takki3 = 6; //10;//7
const int takki4 = 7; //11;//8

const int greenled = A3; // 14;//11
const int redled = A2;  ;//10
const int las1 = 19;//3 laus apels
const int las2 = 16;//13
const int motor = A0; //20;//4 hvit laus
const int hljod = A1;

const int hint1 = 9;
const int hint2 = A4;
const int hint3 = A5;

boolean takki1_OldState;
boolean takki2_OldState;
boolean takki3_OldState;
boolean takki4_OldState;

boolean door1active = true;
boolean door2active = false;

byte state;
unsigned long resetdoorstime = 0;
boolean resetdoorsflag = false;

//debug
//int count = 0;
//

void setup(){
//Serial.begin(9600);

pinMode(takki1, INPUT_PULLUP);
pinMode(takki2, INPUT_PULLUP);
pinMode(takki3, INPUT_PULLUP);
pinMode(takki4, INPUT_PULLUP);

pinMode(greenled, OUTPUT);
pinMode(redled, OUTPUT);
pinMode(motor, OUTPUT);
pinMode(hljod, OUTPUT);
pinMode(hint1, OUTPUT);
pinMode(hint2, OUTPUT);
pinMode(hint3, OUTPUT);

digitalWrite(hljod, HIGH);
digitalWrite(hint1, HIGH);
digitalWrite(hint2, HIGH);
digitalWrite(hint3, HIGH);
digitalWrite(redled, HIGH);
digitalWrite(greenled, LOW);
digitalWrite(motor, LOW);


takki1_OldState = false;
takki2_OldState = false;
takki3_OldState = false;
takki4_OldState = false;

// initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

}

void delayWithRadio(unsigned long t){
  unsigned long now = millis();
  while (millis() - now < t)
  {
    checkOnRadio();
  }
}

void solve(byte las){
  sendInfoAboutSolved(las);
  opna(las);
}

void opna(byte las){
  digitalWrite(redled, LOW);
  digitalWrite(greenled, HIGH);  
    
  digitalWrite(motor, HIGH); // motor ON
  
  digitalWrite(hljod, LOW);
  delay(250);
  digitalWrite(hljod, HIGH);
  
  delayWithRadio(7000);
  digitalWrite(motor, LOW);
  delayWithRadio(2000);
  digitalWrite(hljod, HIGH);
  
  delayWithRadio(2000);
  digitalWrite(motor, LOW);
  delayWithRadio(3000);
  //digitalWrite(las, HIGH);
  
  resetdoorstime = millis();
  resetdoorsflag = true;

}

void resetDoors(){
  if (resetdoorsflag && millis() - resetdoorstime > 5000){
    resetdoorsflag = false;
    _resetDoors();
  }
}
void _resetDoors(){
  //digitalWrite(las1, LOW);
  //digitalWrite(las2, LOW);
  digitalWrite(greenled, LOW);       
  digitalWrite(redled, HIGH);
  digitalWrite(motor, LOW);
}


boolean checkCode1()
{
  for(int i = 0; i<4; i++)
    if(code[i]!=passcode1[i]) return 0;
   return 1;
}
boolean checkCode2()
{
  for(int i = 0; i<4; i++)
    if(code[i]!=passcode2[i]) return 0;
   return 1;  
}

boolean takki1Pressed(){
  boolean event;
  int takki1_pressed = !digitalRead(takki1); // pin low -> pressed

  event = takki1_pressed && !takki1_OldState;
  takki1_OldState = takki1_pressed;
  return event;
}
boolean takki2Pressed(){
  boolean event;
  int takki2_pressed = !digitalRead(takki2); // pin low -> pressed

  event = takki2_pressed && !takki2_OldState;
  takki2_OldState = takki2_pressed;
  return event;
}
boolean takki3Pressed(){
  boolean event;
  int takki3_pressed = !digitalRead(takki3); // pin low -> pressed

  event = takki3_pressed && !takki3_OldState;
  takki3_OldState = takki3_pressed;
  return event;
}
boolean takki4Pressed(){
  boolean event;
  int takki4_pressed = !digitalRead(takki4); // pin low -> pressed

  event = takki4_pressed && !takki4_OldState;
  takki4_OldState = takki4_pressed;
  return event;
}
byte takkiPressed()
{
  if(takki1Pressed()) return 1;
  if(takki2Pressed()) return 2;
  if(takki3Pressed()) return 3;
  if(takki4Pressed()) return 4;
  return 0;
}

unsigned long last_check_time = 0;

void loop(){

  if (millis() - last_check_time > 20){
    last_check_time = millis();
    byte takki = takkiPressed();
    if( (takki != 0) && ( (takki == passcode1[state]) || (takki == passcode2[state]) ) ){
      code[state] = takki;
      state++;
    }
    else if(takki != 0)
    	state = 0;
    
    if(state == 4){
      state = 0;
      if(checkCode1() && door1active) solve(las1);
      if(checkCode2() && door2active) solve(las2);
    }
  }
  //
  resetDoors();
  checkOnRadio();
  //
   //debug
//   count++;
//   if(count%10 == 0){
//     Serial.println(state);
//   }
//

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

//const int Status = 99;
//const int Reset = 98;
//const int SetPassCode = 501;
//const int OpenDoor1 = 503;
//const int OpenDoor2 = 504;
//const int OpenBothDoors = 505;
//const int SetActiveDoor = 506;
    switch (IncomingData.Command)
    {
      case Status:
        sendStatus();
        break;
      case SolveDoor1:
        opna(las1);
        break;
      case SolveDoor2:
        opna(las2);
        break;
      case SetPassCode:
        for (byte i = 0; i < 4; i++)
        {
          passcode1[i] = IncomingData.PassCode1[i];
          passcode2[i] = IncomingData.PassCode2[i];
        }
      case SetActiveDoor:
        if (IncomingData.ActiveDoor == 1)
        {
          door1active = true;
          door2active = false; 
        }
        if (IncomingData.ActiveDoor == 2)
        {
          door1active = false;
          door2active = true; 
        }
        break;
      case PlayHint1:
        digitalWrite(hint1, LOW);
        delay(500);
        digitalWrite(hint1, HIGH);
        break;
      case PlayHint2:
        digitalWrite(hint2, LOW);
        delay(500);
        digitalWrite(hint2, HIGH);
        break;
      case PlayHint3:
        digitalWrite(hint3, LOW);
        delay(500);
        digitalWrite(hint3, HIGH);
        break;
      case Reset:
        asm volatile (" jmp 0"); 
        break;
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
  if (door1active) OutgoingData.ActiveDoor = 1;
  else if (door2active) OutgoingData.ActiveDoor = 2;
  else OutgoingData.ActiveDoor = 0;
  for (byte i = 0; i < 4; i++)
  {
    OutgoingData.PassCode1[i] = passcode1[i];
    OutgoingData.PassCode2[i] = passcode2[i];
  }
  sendOutgoingData();
}

void sendInfoAboutSolved(byte las)
{
  OutgoingData.Command = Solved;
  if (las == las1) OutgoingData.ActiveDoor = 1;
  else OutgoingData.ActiveDoor = 2;
  sendOutgoingData(); 
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
