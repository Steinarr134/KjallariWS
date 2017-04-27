
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        176    //unique for each node on same network
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
  byte PickOrder[6];
  int Temperature;
  long Uptime;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int Reset = 98;
const int SetCorrectPickOrder = 17601;
const int LockWasPicked = 17602;
const int OpenYourSelf = 17603;

const int _outputPins[] = {3, 4, 5, 6, 7, 14};
const int NUMBER_OF_OUTPUTS = 6;
const int _inputPins[] = {15, 16, 17, 18, 19, A6};
const int _doorPin = 9;
const int NUMBER_OF_INPUTS = 6;
boolean _pinsStatus[] = {false, false, false, false, false, false};
int _pickOrder[] = {0,1,2,3,4,5};
int _pinsPicked = 0;
const int analogThreshold = 400;

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

  DeclareOutputs();
  LockDoor();
}

void loop()
{
  ////////////////// put your code here as well

  // the loop has to check on the radio and act to commands received. The radio receives in the
  // background but doesn't send back an ack. The radio also only holds 1 data packet so it will
  // overwrite if it receives a new one. If nothing has been received checkOnRadio() will return
  // immediately.

  CheckForChange();
  checkOnRadio();

  if (IsLockPicked())
  {
    ResetPins();
    OpenDoor();
    SendInfoAboutLockPick();
  }
}

void SendInfoAboutLockPick()
{
  OutgoingData.Command = LockWasPicked;
  sendOutgoingData();
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
        asm volatile(" jmp 0");
        break;
      case SetCorrectPickOrder:
        ResetPins();
        for (int i = 0; i < NUMBER_OF_INPUTS; i++)
        {
          _pickOrder[i] = IncomingData.PickOrder[i];
        }
        break;
      case OpenYourSelf:
        OpenDoor();
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
  OutgoingData.Temperature = (int)radio.readTemperature(0);
  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}


void CheckForChange(){
  for(int i = 0; i < NUMBER_OF_INPUTS; i++){

      if(!IsPinHigh(i)){
        continue;
      }
      
      if(_pinsStatus[i]){
        continue;
      }
      
      if(i != _pickOrder[_pinsPicked]){
        ResetPins();
        break;
      }

      PullUpPin(i);
  }
}

boolean IsLockPicked(){
  for(int pin = 0; pin < NUMBER_OF_INPUTS; pin++){
    if(_pinsStatus[pin] == false){
      return false;
    }
  }
  return true;
}

boolean IsPinHigh(int pin){
  if(pin != 5){
    int digitalSensorValue = digitalRead(_inputPins[pin]);
    return digitalSensorValue == HIGH;
  }
  
  int analogSensorValue = analogRead(_inputPins[pin]);
  return analogSensorValue > 800;
}

void PullUpPin(int pin){
  digitalWrite(_outputPins[pin], HIGH);
  _pinsPicked++;
  _pinsStatus[pin] = true; 
}

void ResetPins(){
  for(int i = 0; i < NUMBER_OF_OUTPUTS; i++){
    digitalWrite(_outputPins[i], LOW);
    _pinsStatus[i] = false;
  }
  _pinsPicked = 0;
}

void DeclareOutputs(){
  for(int i = 0; i < NUMBER_OF_OUTPUTS; i++){
    pinMode(_outputPins[i], OUTPUT);
    digitalWrite(_outputPins[i],LOW);
  }
}

void DeclareInputs(){
  for(int i = 0; i < NUMBER_OF_INPUTS; i++){
    pinMode(_inputPins[i], INPUT);
  }
}

void LockDoor(){
  digitalWrite(_doorPin, HIGH);
}

void OpenDoor(){
  analogWrite(_doorPin, 0);
}



