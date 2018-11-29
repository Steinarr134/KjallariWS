#include <Wire.h>
#include <EEPROM.h>


//----------------- EEPROM Stuff -----------------------------

byte E_threshold = 101;


//This function will write a 2 byte integer to the eeprom at the specified address and address + 1
void EEPROMWriteInt(int p_address, int p_value)
{
  byte lowByte = ((p_value >> 0) & 0xFF);
  byte highByte = ((p_value >> 8) & 0xFF);

  EEPROM.write(p_address, lowByte);
  EEPROM.write(p_address + 1, highByte);
}

//This function will read a 2 byte integer from the eeprom at the specified address and address + 1
unsigned int EEPROMReadInt(int p_address)
{
  byte lowByte = EEPROM.read(p_address);
  byte highByte = EEPROM.read(p_address + 1);

  return ((lowByte << 0) & 0xFF) + ((highByte << 8) & 0xFF00);
}

// for the temperature sensor: - not active yet
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 6  // ÞArf að stilla rétt!
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// operating variables
int ledPin = 4;
int laserPin1 = 5;
int laserPin2 = 12;
int photocellPin = A0;
int photocellValue = 0;
int diodePin = 13;
char trigger = 'o';
int threshold = EEPROMReadInt(E_threshold);
int counter = 0;
int incoming = 0;
bool SendValueNext = false;
byte temperature = 20;

void setup() {
  //sensors.begin();
  Wire.begin(5);
  Serial.begin(9600);
  //i2c transmission
  Wire.onRequest(requestEvent);
  Wire.onReceive(receiveEvent);

  pinMode(ledPin , OUTPUT);
  pinMode(diodePin , OUTPUT);
  pinMode(photocellPin, INPUT);
  pinMode(laserPin1 , OUTPUT);
  pinMode(laserPin2 , OUTPUT);
}

void loop() {
    photocellValue = analogRead(photocellPin);// read the value from the photocell
    Serial.println(photocellValue); 
    if(threshold < photocellValue) // if threshold is reached = movement
    {
      if(incoming == 1)// check if light is on
      {
      digitalWrite(diodePin, HIGH);
      trigger = 'x'; //sets the trigger to x, which is then sent to the master
      }
    }
}

void requestEvent()//when the master requests a status update on movement, sends the trigger value, and sets the trigger back to 'o'
{
  if (SendValueNext)
  {
    Wire.write(photocellValue);
  }
  else
  {
    Wire.write(trigger);
    trigger = 'o';
    digitalWrite(diodePin, LOW);
  }
}

void receiveEvent(int numBytes)//receiving
{
  incoming = Wire.read();
  if (incoming == 3) // next send should be photocell value
  {
    SendValueNext = true;
  }
  else if (incoming == 2) // turn on light but not lasers
  {
    digitalWrite(ledPin, HIGH);
    digitalWrite(laserPin1, LOW);
    digitalWrite(laserPin2, LOW);
  }
  else if (incoming == 1) // turn on light and lasers
  {
    digitalWrite(ledPin, HIGH);
    digitalWrite(laserPin1, HIGH);
    digitalWrite(laserPin2, HIGH);
  }
  else if (incoming == 0) // turn off light and lasers
  {
    digitalWrite(ledPin, LOW);
    digitalWrite(laserPin1, LOW);
    digitalWrite(laserPin2, LOW);
  }
  else // else master is sending a new threshold value
  {
    threshold = incoming;
    EEPROMWriteInt(E_threshold, threshold);
  }
   
}

