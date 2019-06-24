
#include <Wire.h>
#include <EEPROM.h>


#define STATION_NUMBER 6

//----------------- EEPROM Stuff -----------------------------

byte E_threshold = 101;



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
byte threshold = EEPROM.read(E_threshold);
int counter = 0;
int incoming = 0;
bool SendValueNext = false;
byte temperature = 20;

void setup() {
  //sensors.begin();
  Wire.begin(STATION_NUMBER);
  Serial.begin(115200);
  //i2c transmission
  Wire.onRequest(requestEvent);
  Wire.onReceive(receiveEvent);

  pinMode(ledPin , OUTPUT);
  pinMode(diodePin , OUTPUT);
  pinMode(photocellPin, INPUT);
  pinMode(laserPin1 , OUTPUT);
  pinMode(laserPin2 , OUTPUT);

  Serial.print("station number ");
  Serial.print(STATION_NUMBER);
  Serial.println(" started");
}

unsigned long printtime = 0;

bool bla = false;

void loop() {
    photocellValue = analogRead(photocellPin)/4;// read the value from the photocell
    /*if (millis() - printtime > 500)
    {
      printtime = millis();
    Serial.println(photocellValue); 
    }*/
    if(threshold < photocellValue) // if threshold is reached = movement
    {
      if(incoming == 1)// check if light is on
      {
      digitalWrite(diodePin, HIGH);
      trigger = 'x'; //sets the trigger to x, which is then sent to the master
      }
    }
    //if (bla){ Serial.println("sasdasd");}
}

void requestEvent()//when the master requests a status update on movement, sends the trigger value, and sets the trigger back to 'o'
{
  Serial.print("w:\t");
  if (SendValueNext)
  {
    if (photocellValue == 0)
    {
      Wire.write(1);
    }
    else
    {
      Wire.write(photocellValue);
    }
    
    Serial.println(photocellValue);
    SendValueNext = false;
  }
  else
  {
    Wire.write(trigger);
    Serial.println(trigger);
    trigger = 'o';
    digitalWrite(diodePin, LOW);
  }
}
void receiveEvent(int numBytes)//receiving
{
  incoming = Wire.read();
  Serial.print("rec:\t");
  Serial.println(incoming);
  delay(10);
  bla = true;
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
    EEPROM.write(E_threshold, threshold);
  }
   
}

