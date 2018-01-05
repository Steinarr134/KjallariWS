/*
Framtíðar möguleikar:
- Self-calibrate function: Tengja rétt og láta arduinoinn mæla út réttar spennur og geyma í eeprom. Sækja svo úr eeprom í startup.
eeprom er persistent memory, 1024 byte i atmega328p (sem er a moteino).
https://www.arduino.cc/en/Reference/EEPROM

*/
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        170    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network


// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 * - bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  unsigned long Time;
  unsigned long smokeTime;
  bool smokeOn;
  bool buzzerOn;
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// operating variables
const int Status = 99;
const int BombIsLikeDiffused = 17001;
const int BombTotallyExploded = 17002;
const int Reset = 98;
const int SetXplosionTime = 17003;
const int BombActivated = 17004; 
const int SetOptions = 17005;

////Pins
byte DataPin = 3; //Blue wire
byte LatchPin = 5; //Green wire
byte ClockPin = 4; //Yellow wire
byte PiezoPin = 6; //White wire
byte fanPin = 8; 
byte solenoidPin = 9;

byte BananaPins[] = {A0, A1, A2, A3, A4};

byte PhotoRes = A6;
bool isChestOpen = false;
bool isBombDiffused = false;
bool bombExploded = false;
bool smokeOn = true;
int smokeTime = 100;
const int maxSmokeTime = 10000;
bool buzzerOn = true;

int pin[] = {792, 850, 1015, 785, 685}; // The voltage values for each pin from top to bottom
int CorrectValues[] = {pin[0], pin[1], pin[2], pin[3], pin[4]}; // The solution to the puzzle

const byte LightPos[] = {2, 3, 4, 5, 6, 7, 9, 10, 11, 12};
const byte GreenLight[] = {1,13}; 
byte _Register[16] = {0};
int LedBlinkSpeed = 1000;
int NofLeds = 10;

void setup() {
  // initiate Serial port:
  Serial.begin(115200);

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  // init pins:
  pinMode(DataPin, OUTPUT);
  pinMode(LatchPin, OUTPUT);
  pinMode(PiezoPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(solenoidPin, OUTPUT);
  for (byte i = 0; i < 5; i++)
    pinMode(BananaPins[i], INPUT);
  _Register[GreenLight[0]] = 0;
  _Register[GreenLight[1]] = 0;
  Serial.println("started");
}


unsigned long XplosionTime = 10000;
bool min_remaining = false;
unsigned long ChestOpeningTime = 0;

unsigned long blinkTime = 200;
unsigned long updateRegisterLast = 0;
unsigned long checkOpenLast = 0;
void loop()
{
  while (!isChestOpen){
    if (millis() - checkOpenLast > 50) {
      checkOpenLast = millis();
      chestHasBeenOpened();
    }
    checkOnRadio();
  }
  if (min_remaining) {blinkTime = 100;}
  else {blinkTime = 200;}
  if (!bombExploded && !isBombDiffused && isChestOpen && (millis() - updateRegisterLast > blinkTime))
  {
    updateRegisterLast = millis();
    checkOnBananaPins();
    controlLeds();
  }
  checkOnRadio();
}

void reset() {
  asm volatile (" jmp 0");
}

void bombDiffused()
{
  noTone(PiezoPin);
  digitalWrite(fanPin, LOW);
  Serial.println("BOMB DIFFUSED");
  isBombDiffused = true;
  for (int i; i< 16; i++) {
    _Register[i] = 0;  
  }
  _Register[GreenLight[0]] = 1;
  _Register[GreenLight[1]] = 1;
  writeRegister();
  OutgoingData.Command = BombIsLikeDiffused;
  OutgoingData.Time = millis() - ChestOpeningTime;
  sendOutgoingData();
}

void gameOver() {
  Serial.println("BOMB EXPLODED");
  bombExploded = true;
  OutgoingData.Command = BombTotallyExploded;
  sendOutgoingData();
  if (buzzerOn) {
    tone(PiezoPin, 1000); 
  }
  if (smokeOn) {
    digitalWrite(fanPin, HIGH);
    digitalWrite(solenoidPin, HIGH);
    delay(smokeTime*maxSmokeTime/100);
    digitalWrite(solenoidPin, LOW);
    delay(3000);
    digitalWrite(fanPin, LOW);
  }
  noTone(PiezoPin);
}

unsigned long chestHasBeenOpenedLastCheckTime = 0;
void chestHasBeenOpened() 
{
  if (millis() - chestHasBeenOpenedLastCheckTime < 25) {
    return;
  }
  else {
    Serial.println(analogRead(PhotoRes));
    chestHasBeenOpenedLastCheckTime = millis();
    if (analogRead(PhotoRes)>3) {
      isChestOpen = true;
      ChestOpeningTime = millis();
      Serial.print("ChestOpened");
      OutgoingData.Command = BombActivated;
      sendOutgoingData();
      return;
    }
    else {
      isChestOpen = false;
      return;
    }
  }
}

byte _BananaPinCorrectTolerance = 15;
unsigned long _checkOnBananaPinsLastCheckTime = 0;
void checkOnBananaPins()
{
  if (millis() - _checkOnBananaPinsLastCheckTime > 25)
  { 
    Serial.print("BananaPinState: ");
    for (byte i = 0; i<5; i++) {
      Serial.print(analogRead(BananaPins[i]));
      Serial.print(" ");
    }
    Serial.println();
    for (byte i = 0; i<5; i++)
    {
      if (absdiff(analogRead(BananaPins[i]), CorrectValues[i]) > _BananaPinCorrectTolerance)
        return;
    }
    bombDiffused();
  }
}

unsigned long _controlLedsLastBlinkTime = 0;
bool _controlLedsBlinkerLed = false;
int ledBeep = 0;
void controlLeds()
{
  unsigned long t = millis()-ChestOpeningTime;
  byte leds_remaining = (1-((double) t)/((double) XplosionTime))*NofLeds+1;
  if (leds_remaining < 1 || leds_remaining > 10) {
    gameOver();
    return;
  }
  if (leds_remaining == 1) {
      min_remaining = true;
      digitalWrite(fanPin, HIGH);
  }
  if (min_remaining) {
    leds_remaining = (1-((double) t)/((double) XplosionTime))*NofLeds*10+1;
  }
  Serial.print("Leds remaining:");
  Serial.println(leds_remaining);
  for (int i = 0; i < NofLeds; i++)
  {
    _Register[LightPos[i]] = (i < leds_remaining);
  }
  _controlLedsBlinkerLed = !_controlLedsBlinkerLed;
  if (ledBeep == 0) {
    tone(PiezoPin, 5000);
  }
  else {
    noTone(PiezoPin);
  }
  Serial.print("Beep: ");
  Serial.println(ledBeep);
  ledBeep++;
  if (ledBeep == 9) {
    ledBeep = 0;
  }
  _Register[LightPos[leds_remaining-1]] = _controlLedsBlinkerLed;
  writeRegister();
  printRegister();
}

void writeRegister()
{
  byte h = 0;
  byte l = 0;
  for (byte i = 0; i<8; i++)
  {
    h += _Register[i]<<i;
    l += _Register[i+8]<<i;
  }
  Serial.println("Writing Register");
  digitalWrite(LatchPin, LOW);
  shiftOut(DataPin, ClockPin, l);
  shiftOut(DataPin, ClockPin, h);
  digitalWrite(LatchPin, HIGH);
}

void printRegister()
{
  for (byte i= 0; i<16; i++)
  {
    Serial.print(_Register[i]);
    Serial.print("  "); 
  }
  Serial.println();
}

int absdiff(int a, int b)
{
  if (a > b)
  {
    return a - b;
  }
  return b - a;
}


void shiftOut(int myDataPin, int myClockPin, byte myDataOut) {
  // This shifts 8 bits out MSB first, 
  //on the rising edge of the clock,
  //clock idles low

//internal function setup
  int i=0;
  int pinState;
  pinMode(myClockPin, OUTPUT);
  pinMode(myDataPin, OUTPUT);

 //clear everything out just in case to
 //prepare shift register for bit shifting
  digitalWrite(myDataPin, 0);
  digitalWrite(myClockPin, 0);

  //for each bit in the byte myDataOut�
  //NOTICE THAT WE ARE COUNTING DOWN in our for loop
  //This means that %00000001 or "1" will go through such
  //that it will be pin Q0 that lights. 
  for (i=7; i>=0; i--)  {
    digitalWrite(myClockPin, 0);

    //if the value passed to myDataOut and a bitmask result 
    // true then... so if we are at i=6 and our value is
    // %11010100 it would the code compares it to %01000000 
    // and proceeds to set pinState to 1.
    if ( myDataOut & (1<<i) ) {
      pinState= 1;
    }
    else {  
      pinState= 0;
    }

    //Sets the pin to HIGH or LOW depending on pinState
    digitalWrite(myDataPin, pinState);
    //register shifts bits on upstroke of clock pin  
    digitalWrite(myClockPin, 1);
    //zero the data pin after shift to prevent bleed through
    digitalWrite(myDataPin, 0);
  }

  //stop shifting
  digitalWrite(myClockPin, 0);
}


//=========================RADIO================================


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
        reset();
        break;
      case SetXplosionTime:
        XplosionTime = IncomingData.Time;
        break;
      case SetOptions:
        smokeTime = IncomingData.smokeTime;
        smokeOn = IncomingData.smokeOn;
        buzzerOn = IncomingData.buzzerOn;
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
  if (isChestOpen) {OutgoingData.Time = XplosionTime - millis() + ChestOpeningTime;}
  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}


