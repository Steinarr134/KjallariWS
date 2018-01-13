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
  //Serial.println("adsfsfd");
  
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  //Serial.println("sdsdfsdfa");
  /*while (false)
  {
    checkOnRadio();
  }
  */
  //Retrieve the last sequence from the EEPROM memory

  for (int i = 0; i < sequenceSize; i++) {
    sequence[i] = 127;
  }

  sendBeat();
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
    switch (IncomingData.command)
    {
      case statusCommand:
        sendStatus();
        break;
      case beatCommand:
        setBeat();
        break;
      case sequenceCommand:
        setSequence();
        setBeat();
        Run = 1;
        firstRun = 0;
        lightmillis = millis();
        break;
      case resetCommand:
        reset();
        break;
    }
  }
}


void loop() {
  checkOnRadio();
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
    Wire.requestFrom(i, 1);

    // Steinarr added this part so that the radio can still be rensponsive while
    // the master waits for a slave to communicate
    while (!Wire.available())
    {
      checkOnRadio();
    }
    
    slaveChar = Wire.read();
    if (slaveChar == trigger && (millis() - slaveSendTimes[i] > 20))
    {
      return i;
      //Serial.println(i);
    }
  }
  return 0;
}

void sendBeat()//send the slaves 1 for ligth on, 0 for light off.
{
  if (counter > sequenceSize - 1)
  {
    counter = 0;
  }
  for (int i = 1; i <= numberOfStations; i++)
  {
    checkOnRadio(); // Steinarr added this line to prevent lost packets while updating beat
    slaveSend(i, counter);
    slaveSendTimes[i] = millis();
  }
  counter++;

}

void slaveSend(int slaveNumber, int counter)//i2c transmission to slave number i
{
  Wire.beginTransmission(slaveNumber);
  Wire.write(getBit(counter, slaveNumber));
  Wire.endTransmission();

}

void lightsOn()
{
  for (int i = 1; i <= numberOfStations; i++)
  {
    Wire.beginTransmission(i);
    Wire.write(2);
    Wire.endTransmission();
  }
}

void sendStatus()//not active
{
  triggerstatus = checkTrigger();
  OutgoingData.trippedSlave = triggerstatus;
  OutgoingData.command = statusCommand;
  OutgoingData.beat = beat;
  radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), sizeof(OutgoingData));
}

void setBeat()
{
  if (IncomingData.beat < 100) {
    return;
  }
  else {
    beat = IncomingData.beat;
  }
}

void setSequence() {
  for (int i = 0; i < sequenceSize; i++) {
    sequence[i] = IncomingData.sequence[i];
  }
  counter = 0;


}

void reset() {
  asm volatile("jmp 0");
}

byte getBit(byte byteNumber, byte bitNumber)//this function converts an integer to an 8 bit binary number
{
  return  ((sequence[byteNumber] & 0x01 << bitNumber - 1) >> bitNumber - 1);
}

