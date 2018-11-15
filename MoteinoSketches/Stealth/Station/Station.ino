#include <Wire.h>


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
int threshold =600;
int counter = 0;
int lightStatus = 0;
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
      if(lightStatus == 1)// check if light is on
      {
      digitalWrite(diodePin, HIGH);
      trigger = 'x'; //sets the trigger to x, which is then sent to the master
      }
    }
}

void requestEvent()//when the master requests a status update on movement, sends the trigger value, and sets the trigger back to 'o'
{
  Wire.write(trigger);
  trigger = 'o';
  digitalWrite(diodePin, LOW);
}

void receiveEvent(int numBytes)//receiving the light sequence
{
  lightStatus = Wire.read();
  if (lightStatus == 2)
  {
    digitalWrite(ledPin, HIGH);
    digitalWrite(laserPin1, LOW);
    digitalWrite(laserPin2, LOW);
  }
  else if (lightStatus == 1)
  {
    digitalWrite(ledPin, HIGH);
    digitalWrite(laserPin1, HIGH);
    digitalWrite(laserPin2, HIGH);
  }
  else
  {
    digitalWrite(ledPin, LOW);
    digitalWrite(laserPin1, LOW);
    digitalWrite(laserPin2, LOW);
  }
   
}

