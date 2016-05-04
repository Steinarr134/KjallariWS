#include <EEPROMex.h>
#include <EEPROMVar.h>

/////////////////// for the temperature sensors:
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 7  // ÞArf að stilla rétt!
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
DeviceAddress MotorSensor;
DeviceAddress DriverSensor;  //// Þarf a' stilla líka
DeviceAddress HousingSensor;

//////////////////////// for the radio
#include <RFM69.h>    
#include <SPI.h>
#define NODEID        13    //unique for each node on same network   
#define NETWORKID     7  //the same on all nodes that talk to each other
//Match frequency to the hardware version of the radio on your Moteino (uncomment one):
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define SERIAL_BAUD   9600
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network
typedef struct{
  int Command;
  byte MoteinoTemperature;
  byte MotorTemperature;
  byte DriverTemperature;
  long CurrentPosition;
  long MaxPosition;
  unsigned int FastSpeed;
  unsigned int SlowSpeed;
  unsigned int Acceleration;
  byte LightIntensity;
  
} Payload;
Payload OutgoingData;
Payload IncomingData;
byte DataLen = sizeof(IncomingData);
byte BaseID = 1;

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
const int FastSpeed_EEPROM_Address = 100;
const int SlowSpeed_EEPROM_Address = 102;
const int Acceleration_EEPROM_Address = 104;

int FastSpeed = EEPROMReadInt(FastSpeed_EEPROM_Address);
int SlowSpeed = EEPROMReadInt(SlowSpeed_EEPROM_Address);
int Acceleration = EEPROMReadInt(Acceleration_EEPROM_Address);
long MaxPosition;

const byte MotorEnablePin = 7;
const byte MotorStepPin = 3;
const byte MotorDirectionPin = 4;


///// For the motor
#include <AccelStepper.h>
AccelStepper Motor(AccelStepper::FULL2WIRE, MotorStepPin, MotorDirectionPin);


//// For the lights
byte LightPin = 6;  //// Þarf að stilla

///// For the buttons
byte RewindPin = A6;
byte FastForwardPin = A5;
byte StopPin = A4;
byte PlayPin = A3;

byte ON = LOW;
byte OFF = HIGH;

void setup() {
  Serial.begin(9600);

  ////// Setup Temperature sensors
  sensors.begin();

  ///// Setup Radio
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

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

  checkOnButtons();

  checkOnRadio();
}

void runMotor()
{
  if (!Motor.run())
  {
    // if Motor is not running: disable motor
    disableMotor();
  }
}

void checkOnButtons()
{
  if (digitalRead(RewindPin))
  {
    sendRewind();
  }
  if (digitalRead(FastForwardPin))
  {
    sendFastForward();
  }
  if (digitalRead(StopPin))
  {
    sendStop();
  }
  if (digitalRead(PlayPin))
  {
    sendPlay();
  }
}

void sendRewind()
{
  OutgoingData.Command = SendRewind;
  send();
}
void sendFastForward()
{
  OutgoingData.Command = SendFastForward;
  send();
}
void sendPlay()
{
  OutgoingData.Command = SendPlay;
  send();
}
void sendStop()
{
  OutgoingData.Command = SendStop;
  send();
}

void checkOnRadio()
{
  if (radio.receiveDone())
  {
    if (radio.SENDERID == BaseID)
    {
      IncomingData = *(Payload*)radio.DATA;
      if (radio.ACKRequested())
      {
        radio.sendACK();
      }
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
  }
}

void sendStatus()
{
  sensors.requestTemperatures();
  delay(10);
//  OutgoingData.numbers[5] = 10*sensors.getTempC(MotorSensor);
//  OutgoingData.numbers[6] = 10*sensors.getTempC(DriverSensor);
//  OutgoingData.numbers[7] = 10*sensors.getTempC(HousingSensor);
  send();
}

void play()
{
  enableMotor();
  Motor.setSpeed(SlowSpeed);
  Motor.moveTo(MaxPosition);
}

void stop()
{
  Motor.stop();
}

void rewind()
{
  enableMotor();
  Motor.setSpeed(FastSpeed);
  Motor.moveTo(0);
}

void fastForward()
{
  enableMotor();
  Motor.setSpeed(FastSpeed);
  Motor.moveTo(MaxPosition);
}

void returnToZero()
{
  enableMotor();
  Motor.setSpeed(FastSpeed);
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

void send()
{
  radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),DataLen);
}

void enableMotor()
{
  digitalWrite(MotorEnablePin, ON);
}

void disableMotor()
{
  digitalWrite(MotorEnablePin, OFF);
}
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

