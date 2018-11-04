/*
Mogulegar framtidarvidbaetur:
Bæta við "Self check", þ.e. rulla i gegnum alla pinna og mæla takkana fyrir og eftir, tekka hvort their virki.
Annadhvort i startup eda ad beidni pafa.

*/
#include <RFM69.h>
#include <SPI.h>
#define NODEID        176    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define resetDelay    45000   // reset eftir 45 sek inactivity
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network


// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct {
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
const int setActive = 17604;
const int setInactive = 17605;
const int testPins = 17606;

const int _outputPins[] = {3, 4, 5, 6, 7, 14};
const int NUMBER_OF_OUTPUTS = 6;
const int _inputPins[] = {15, 16, 17, 18, 19, A6};
const int _doorPin = 9;
const int builtinLed = 9;   // status blikkari, debug
const int NUMBER_OF_INPUTS = 6;
boolean _pinsStatus[] = {false, false, false, false, false, false};
int _pickOrder[] = {0, 1, 2, 3, 4, 5};
int _pinsPicked = 0;
const int analogThreshold = 400;

unsigned long int lastActive = 0;      // timabreyta, geymir millis() sidustu virkni, f auto reset
unsigned long int lastLight = 1000;    // debug, built-in led blink
unsigned long int now = 0;

boolean ledState = true;

// "active" er 'mode' thrautarinnar. Ef 0, tekkar ekki a pinnum, haldast ekki uppi. Byrjar i 1.
boolean active = 1;               
int blinkDelay = 1000;

void setup() {
  // initiate Serial port:
  Serial.begin(115200);
  Serial.println("Serial begin");

  // initiate radio:
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  DeclareOutputs();
  LockDoor();
}

void loop()
{
  checkOnRadio();
  now = millis();

  // brown-out check, debug. built-in led blikkar hratt ef pinni er uppi, haegt ef allir nidri
  // commented ut tvi hurdin er a pinna 9
  /*if ((now - lastLight) >= blinkDelay) {
    digitalWrite(builtinLed, ledState);
    lastLight = now;
    ledState = !ledState;
  }
  */

  if (active) {
    CheckForChange();

    if (IsLockPicked()) {
      OpenDoor();
      SendInfoAboutLockPick();
      active = 0;
      delay(10000);    // bida i 1 sek med ad resetta pinna
      ResetPins();
    }

    // Ef einhver pinni er uppi og 90 sek lida an activity -> ResetPins
    if (checkActivity()) {
      blinkDelay = 100;  // debug
      if ((now - lastActive) > resetDelay) {
        lastActive = now;
        blinkDelay = 1000;
        ResetPins();
      }
    }
  }  // ## --- if(active), close --- ## //
}  // ## --- LOOP CLOSE --- ## //


void ResetPins() {
  _pinsPicked = 0;
  for (int i = 0; i < NUMBER_OF_OUTPUTS; i++) {
    _pinsStatus[i] = false;
    digitalWrite(_outputPins[i], LOW);
    delay(5);   // naudsynlegt delay()
  }
}

void pinTest(){
  for (int i = 0; i < NUMBER_OF_OUTPUTS; i++) {
    digitalWrite(_outputPins[i], HIGH);
    delay(100);   // naudsynlegt delay()
    digitalWrite(_outputPins[i], LOW);
    delay(50);
  }
}

boolean checkActivity()  // ef einhver pinnanna er true ("picked"), skila true
{
  boolean activity = false;
  for (int i = 0; i < NUMBER_OF_OUTPUTS; i++) {
    if (_pinsStatus[i] == true) {
      activity = true;
    }
  }
  return activity;
}

void CheckForChange() {
  for (int i = 0; i < NUMBER_OF_INPUTS; i++) {

    if (!IsPinHigh(i)) {
      continue;
    }

    if (_pinsStatus[i]) {
      continue;
    }

    if (i != _pickOrder[_pinsPicked]) {
      delay(50);
      ResetPins();
      break;
    }
    PullUpPin(i);
    Serial.print("pin ");
    Serial.print(i);
    Serial.println(" pulled up");
  }
}

boolean IsLockPicked() {
  for (int pin = 0; pin < NUMBER_OF_INPUTS; pin++) {
    if (_pinsStatus[pin] == false) {
      return false;
    }
  }
  return true;
}

boolean IsPinHigh(int pin) {
  if (pin != 5) {
    int digitalSensorValue = digitalRead(_inputPins[pin]);
    return digitalSensorValue == HIGH;
  }

  int analogSensorValue = analogRead(_inputPins[pin]);
  return analogSensorValue > 800;
}

void PullUpPin(int pin) {
  digitalWrite(_outputPins[pin], HIGH);
  _pinsPicked++;
  lastActive = millis();
  _pinsStatus[pin] = true;
}



void DeclareOutputs() {
  for (int i = 0; i < NUMBER_OF_OUTPUTS; i++) {
    pinMode(_outputPins[i], OUTPUT);
    digitalWrite(_outputPins[i], LOW);
  }
}

void DeclareInputs() {
  for (int i = 0; i < NUMBER_OF_INPUTS; i++) {
    pinMode(_inputPins[i], INPUT);
  }
}

void LockDoor() {
  digitalWrite(_doorPin, HIGH);
}

void OpenDoor() {
  analogWrite(_doorPin, 0);
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
      case setActive:
        active = 1;
        break;
      case setInactive:
        active = 0;
        break;
      case testPins:
        pinTest();
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
  return radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), sizeof(OutgoingData));
}
