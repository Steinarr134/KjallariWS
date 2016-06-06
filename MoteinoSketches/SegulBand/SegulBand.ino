#include <EEPROMex.h>
#include <EEPROMVar.h>
//Ásgeir er bestur

/////////////////// for the temperature sensors:
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
DeviceAddress MotorSensor = {0x28, 0xFF, 0x41, 0xC5, 0x10, 0x14, 0x00, 0x49};
DeviceAddress DriverSensor = {0x28, 0xFF, 0x8F, 0xE3, 0x10, 0x14, 0x00, 0xB0}; 
DeviceAddress HousingSensor;


typedef struct{         // Þarf að stilla
  int Command;
  byte MotorTemp;
  byte DriverTemp;
  int CurrentPosition;
  byte LightIntensity;
} Payload;
Payload OutgoingData;
Payload IncomingData;
const byte datalen = sizeof(IncomingData);


//////////// Command values
// incoming:
const int Status = 99;
const int Play = 1301;
const int Stop = 1302;
const int Rewind = 1303;
const int FastForward = 1304;
const int ReturnToZero = 1305;
const int SetParams = 1306;
const int SetLights = 1307;

// Outgoing:
const int SendRewind = 1351;
const int SendFastForward = 1352;
const int SendPlay = 1353;
const int SendStop = 1354;

//// Variables
byte N[datalen];
byte M[datalen];
byte Counter;
bool FirstHexDone;
byte FirstHex;

/*
const int FastSpeed_EEPROM_Address = 100;
const int SlowSpeed_EEPROM_Address = 102;
const int Acceleration_EEPROM_Address = 104;

int FastSpeed = EEPROMReadInt(FastSpeed_EEPROM_Address);
int SlowSpeed = EEPROMReadInt(SlowSpeed_EEPROM_Address);
int Acceleration = EEPROMReadInt(Acceleration_EEPROM_Address);
long MaxPosition;
*/

int FastSpeed = 1800;
int SlowSpeed = 500;
int Acceleration = 1500;
long MaxPosition = 100000;

const byte MotorEnablePin = 7;
const byte MotorStepPin = 9;
const byte MotorDirectionPin = 8;


///// For the motor
#include <AccelStepper.h>
AccelStepper Motor(AccelStepper::FULL2WIRE, MotorStepPin, MotorDirectionPin);


//// For the lights
byte LightPin = 3;  //// Þarf að stilla


byte ON = LOW;
byte OFF = HIGH;

void setup() {
  Serial.begin(115200);

  ////// Setup Temperature sensors
  sensors.begin();

  ////// Setup Motor
  Motor.setMaxSpeed(SlowSpeed);
  Motor.setAcceleration(Acceleration);
  pinMode(MotorEnablePin, OUTPUT);
  digitalWrite(MotorEnablePin, OFF);


  /////// Setup Lights
  pinMode(LightPin, OUTPUT);
  digitalWrite(LightPin, LOW);

  Serial.println("Here We GO!!");
}

unsigned long LastSendTime = 0;

void loop() 
{
  runMotor();

  checkOnSerial();

  
}

void runMotor()
{
  if (!Motor.run())
  {
    // if Motor is not running: disable motor
    disableMotor();
  }
}

void checkOnSerial(){
  // So, lets first process any serial input:
  if (Serial.available() > 0)
  {
    // The string will be on the form (Send2ID)#(number1):(number2):    with up to 10 numbers.
    // every number will be 'terminated' by a ':'
    char incoming = Serial.read(); // reads one char from the buffer
    if (incoming == '\n')
    { // if the line is over
      IncomingData = *(Payload*)N;
      react();
      Counter = 0;
    }
    else
    {
      if (FirstHexDone)
      {
        FirstHexDone = 0;
        N[Counter] = FirstHex*16+hexval(incoming);
        Counter++;
      }
      else
      {
        FirstHex = hexval(incoming);
        FirstHexDone = 1;
      }
    }
  }
}

void react()
{
  Serial.print("Received Command:");
  Serial.println(IncomingData.Command);
  switch (IncomingData.Command) 
  {
    case Status:
      sendStatus();
      break;
    case Play:
      play();
      break;
    case Stop:
      stop();
      break;
    case Rewind:
      rewind();
      break;
    case FastForward:
      fastForward();
      break;
    case ReturnToZero:
      returnToZero();
      break;
    case SetParams:
      setParams();
      break;
    case SetLights:
      setLights();
      break;
    default:
      Serial.println("Error: Command not recognized");
      break;
  }
}


void sendStatus()
{
  sensors.requestTemperatures();
  delay(10);
  OutgoingData.MotorTemp = (byte) sensors.getTempC(MotorSensor);
  OutgoingData.DriverTemp = (byte) sensors.getTempC(DriverSensor);
  Serial.println(OutgoingData.MotorTemp);
  OutgoingData.Command = Status;
  OutgoingData.LightIntensity = 100;
  OutgoingData.CurrentPosition = 101;
//  OutgoingData.numbers[7] = 10*sensors.getTempC(HousingSensor);
  Serial.println("sending status");
  send();
}

void send()
{
  memcpy(&M, &OutgoingData, datalen);
  for (byte i = 0; i < datalen; i++)
  {
    hexprint(M[i]);
  }
  Serial.println();
}
void play()
{
  enableMotor();
  Motor.setMaxSpeed(SlowSpeed);
  Serial.print("SlowSpeed");
  Serial.print("\t");
  Serial.println(SlowSpeed);
  Motor.moveTo(MaxPosition);
}

void stop()
{
  Motor.stop();
}

void rewind()
{
  enableMotor();
  Motor.setMaxSpeed(FastSpeed);
  Motor.moveTo(0);
}

void fastForward()
{
  enableMotor();
  Motor.setMaxSpeed(FastSpeed);
  Serial.print("FastSpeed");
  Serial.print("\t");
  Serial.println(FastSpeed);
  Motor.moveTo(MaxPosition);
}

void returnToZero()
{
  enableMotor();
  Motor.setMaxSpeed(FastSpeed);
  Motor.moveTo(0);
}

void setParams()
{ 
  Motor.setAcceleration(Acceleration);
}

void setLights()
{
  analogWrite(LightPin, IncomingData.LightIntensity);
}


void enableMotor()
{
  digitalWrite(MotorEnablePin, ON);
}

void disableMotor()
{
  digitalWrite(MotorEnablePin, OFF);
}

void hexprint(byte b)
{
  if (b<16)
  {
    Serial.print('0');
  }
  Serial.print(b, HEX);
}

byte hexval(char c)
{
  if (c <= '9')
  {
    return c - '0';
  }
  else if (c <= 'F')
  {
    return 10 + c - 'A';
  }
  else
  {
    return 10 + c - 'a';
  }
}

/*
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
*/
