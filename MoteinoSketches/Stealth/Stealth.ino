// CSMA_LIMIT  í RFM69.h breytt í -50!

#include <SPIFlash.h>
#include <Wire.h>
#include <RFM69.h>
#include <SPI.h>


//radio
#define NODEID        7    //unique for each node on same network   
#define NETWORKID     7  //the same on all nodes that talk to each other
//Match frequency to the hardware version of the radio on your Moteino (uncomment one):
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define SERIAL_BAUD   9600
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network


// operating variables
const int statusCommand = 99;
const int resetCommand = 98;
const int beatCommand = 73;
const int sequenceCommand = 72;
const int triggerCommand = 71;
const int thresholdCommand = 74;
const int sendPhotoValuesCommand = 75;
const int setSkipDelayCommand = 76;

int const sequenceSize = 50;
int counter = 0;
bool Run = 0;
bool firstRun = 1;

char trigger = 'x';
char slaveChar;
int diodePin = 13;
const int numberOfStations = 6;
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;
unsigned long lightmillis = 0;
int beat = 2000;
int triggerstatus = 0;
unsigned long MaxSlaveWaitTime = 100;
byte skipdelay = 40;
bool lightson = false;
unsigned long lightsontime = 0;
bool lightsonnow = false;
int lightsonblinktime = 250;

//this is the package transmitted over RF
struct Payload {
  int command;
  int beat;
  byte trippedSlave;
  byte sequence[50];
};
Payload OutgoingData;
Payload IncomingData;
byte sequence[50];
byte DataLen = 54;
byte BaseID = 1;

void setup() {
  Wire.begin();
  
  Serial.begin(115200);
  Serial.println("adsfsfd");
  delay(10);
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);


  //Retrieve the last sequence from the EEPROM memory

  for (int i = 0; i < sequenceSize; i++) {
    sequence[i] = 0xFF;
  }
  
  sendPhotoValues();

  Serial.println("Started");
}

unsigned long slaveSendTimes[numberOfStations] = {0};

void checkOnRadio()
{
  // this function checks if there is any incoming message from the main computer
  //and deals with the message ones it arrives
  if (radio.receiveDone())
  {
    //Serial.println("!");
    IncomingData = *(Payload*)radio.DATA;
    if (radio.ACKRequested())
    {
      radio.sendACK();
      //Serial.println(millis());
    }
    Serial.println(IncomingData.command);
    switch (IncomingData.command)
    {
      case statusCommand:
        sendStatus();
        break;
      case beatCommand:
        setBeat();
        break;
      case sequenceCommand:
        lightson = false;
        setSequence();
        setBeat();
        Run = 1;
        firstRun = 0;
        lightmillis = millis();
        break;
      case resetCommand:
        reset();
        break;
      case thresholdCommand:
        setThreshold();
        break;
      case sendPhotoValuesCommand:
        sendPhotoValues();
        break;

      case setSkipDelayCommand:
        skipdelay = IncomingData.sequence[0];
        break;
    }
  }
}


void loop() {
  checkOnRadio();
  checkOnSerial();
  runLightsOn();
  if (Run) {
    //this function asks the slaves if any movement has been detected
    int triggeredSlave = checkTrigger();
    if (triggeredSlave && ((millis() - lightmillis) > 500)) {
      //digitalWrite(diodePin, HIGH);       Bannad ad nota pinna 13
      OutgoingData.command = triggerCommand;
      OutgoingData.trippedSlave = triggeredSlave;
      radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), sizeof(OutgoingData));
      Run = 0;
      lightsOn();
    }
    else {
      currentMillis = millis();
      if (currentMillis - previousMillis >= beat) {
        sendBeat();
        previousMillis = currentMillis;
      }
    }

  }
  if (firstRun) {
    currentMillis = millis();
    if (currentMillis - previousMillis >= beat) {
      sendBeat();
      checkTrigger();
      previousMillis = currentMillis;
    }
  }
}

int checkTrigger()//check if any movement has been detected, sends a message to the main computer if so.
{
  for (int i = 1; i <= numberOfStations; i++)
  {
    slaveChar = slaveRead(i);
    if (slaveChar == 0) // 0 means nothing was received
    {
      return i+10;
    }
    if (slaveChar == trigger && (millis() - slaveSendTimes[i-1] > skipdelay))
    {
      return i;
    }
  }
  return 0;
}

void sendPhotoValues()
{
  for (byte i = 0; i < sequenceSize; i++)
  {
    OutgoingData.sequence[i] = 0;
  }

  // tell all stations to turn on lights and lasers
  for (int i = 1; i <= numberOfStations; i++)
  {
    //i = 8;
    Serial.print("Sending: '");
    Serial.print("1");
    Serial.print("' to slave: ");
    Serial.println(i);
    slaveSend(i, 1);
  }

  //wait for half a second to give them time to change
  delay(500);
  
  for (int i = 1; i <= numberOfStations; i++)
  {
    //i = 8;
    Serial.print("Sending: '");
    Serial.print("3");
    Serial.print("' to slave: ");
    Serial.println(i);
    slaveSend(i, 3);
    OutgoingData.sequence[i] = slaveRead(i); 

    Serial.print("Read: '");
    Serial.print(OutgoingData.sequence[i]);
    Serial.print("' from slave: ");
    Serial.println(i);
  }

  OutgoingData.command = sendPhotoValuesCommand;
  sendOutgoingData();
}

void sendBeat()//send the slaves 1 for ligth on, 0 for light off.
{
  //Serial.println("send nudes");
  if (counter > sequenceSize - 1)
  {
    counter = 0;
  }
  for (int i = 1; i <= numberOfStations; i++)
  {
    //i=8;
    slaveSend(i, getBit(counter, i));
    slaveSendTimes[i-1] = millis();
    int bla = millis();
  }
  counter++;

}

byte slaveRead(byte i)
{
  Wire.requestFrom((int)i, 1);

    // Steinarr added this part so that the radio can still be rensponsive while
    // the master waits for a slave to communicate

    unsigned long t0 = millis();    
    while (!Wire.available())
    {
      checkOnRadio();
      if (millis() - t0 < MaxSlaveWaitTime);
      {
        return 0; // 0 if nothing is received
      }
    }
    
    return Wire.read();
}

void slaveSend(int slaveNumber, int what)//i2c transmission to slave number i
{
  Serial.print("slavesend  -  ");
  Serial.print("Sending: '");
  Serial.print(what);
  Serial.print("' to slave: ");
  Serial.println(slaveNumber);
  Wire.beginTransmission(slaveNumber);
  //Serial.println("Not reaching here - 1234"); delay(10);
  Wire.write(what);
  //Serial.println("Not reaching here - dgf"); delay(10);
  Wire.endTransmission();
  //Serial.println("Not reaching here- sdgh"); delay(10);
}


void lightsOn()
{
  lightson = true;
}

void runLightsOn()
{
  if (lightson)
  {
    if (millis() - lightsontime > lightsonblinktime)
    {
      lightsontime = millis();
      for (byte i = 1; i <= numberOfStations; i++)
      {
        slaveSend(i, ((byte)lightsonnow)*2);
      }
      lightsonnow = !lightsonnow;
    }
  }
}

void sendStatus()
{
  //Serial.println("sendStatus()");
  triggerstatus = checkTrigger();
  //Serial.println("got past checkTrigger()");
  OutgoingData.trippedSlave = triggerstatus;
  OutgoingData.command = statusCommand;
  OutgoingData.beat = beat;
  //Serial.println("Sending the status...");
  //delay(40);
  sendOutgoingData();
  //Serial.println("Status was sent");
}

void sendOutgoingData()
{
  radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), sizeof(OutgoingData));
}

void setThreshold()
{
  for (byte i = 1; i <= numberOfStations; i++)
  {
    slaveSend(i, IncomingData.sequence[i-1]);
  }
}

void setBeat()
{
  Serial.println("Setting beat to incoming");
  if (IncomingData.beat < 100) {
    return;
  }
  else {
    beat = IncomingData.beat;
  }
}

void setSequence() {
  Serial.println("Setting sequence from IncomingData");
  for (int i = 0; i < sequenceSize; i++) {
    sequence[i] = IncomingData.sequence[i];
  }
  counter = 0;
}

void checkOnSerial()
{
  if (Serial.available())
  {
    Serial.read();
    sendPhotoValues();
  }
}
void reset() {
  asm volatile("jmp 0");
}

byte getBit(byte byteNumber, byte bitNumber)//this function converts an integer to an 8 bit binary number
{
  return  ((sequence[byteNumber] & 0x01 << bitNumber - 1) >> bitNumber - 1);
}

