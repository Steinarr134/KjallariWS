#include <RFM69.h>
#include <SPI.h>
#define NODEID        42    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network

// Incoming and Outgoing buffers:
typedef struct {
  byte x[61];
} Payload;
Payload RadioBuffer;
byte SerialBuffer[63];

typedef struct {
  byte sender;
    byte send2;
  byte rssi;
} RadioStruct;

typedef struct {
  byte send2id;
  bool ack_requested;
  byte retries;
  byte buffer[61];
} SerialStruct;

//SerialStruct s;
RadioStruct r;

byte RequestShutDownPin = 6;
byte BootOkPin = A0;
byte Output5VPin = 4;
byte BatteryPin = A7;
byte ButtonPin = 3;

void setup()
{ // Setup runs once
  Serial.begin(38400);
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
}

void pretendStartup()
{
  delay(700);
  Serial.println("moteinopy basesketch v2.3");
  unsigned long t = millis();
  while (millis() - t < 300)
  {
    if (Serial.available() > 0)
    {
      byte dontcare = Serial.read();
    }
  }
  Serial.println("Ready");
}

// Global variables to recieve incoming serial messages
char FirstHex;
boolean FirstHexDone = 0;
byte SerialCounter = 0; // Counter keeps count of how many bytes have been recieved.
byte SerialBufferLen = 0;
byte datalen = 0;


void loop()
{ //loop runs over and over forever
  // we want to do 2 thing at once, Listen to the Serial port and the radio. We can't
  // actually do both at the 'same' time but we can do one and then the other, extremely fast.

  // So, lets first process any serial input:
  checkOnSerial();

  // and then check on the radio:
  // The radio is always listening and recieving but doesn't respond on its own,
  // We have to constantly check if something has been recieved and answer with an ACK
  checkOnRadio();

  checkOnBattery();
}


unsigned long LastBatteryCheckTime = 0;
unsigned long LastTimeExternalPower = 0;
unsigned long LastTimeNoExternalPower = 0;
void checkOnBattery()
{
  if (millis() - LastBatteryCheckTime > 20)
  {
    float b = measureBattery();
    if (b > 4.3)
    {
      if (digitalRead(ButtonPin))
      {
        shutDownPi();
      }
      LastBatteryCheckTime = millis();
      LastTimeExternalPower = millis();
      if (millis() - LastTimeNoExternalPower > 3000)
      {
        startUpPi();
      }
    }
    else
    {
      LastTimeNoExternalPower = millis();
      if (millis() - LastTimeExternalPower > 3000)
      {
        shutDownPi();
      }
    }
  }
}

void startUpPi()
{
  digitalWrite(RequestShutDownPin, LOW);
  digitalWrite(Output5VPin, HIGH);
}

boolean bootOK()
{
  return analogRead(BootOkPin) > 800;
}

float measureBattery()
{
  return analogRead(BatteryPin) * 0.00322 * 1.47;
}

void shutDownPi()
{
  if (bootOK())
  {
    digitalWrite(RequestShutDownPin, HIGH);
    while (bootOK())
    {
      delay(50);
    }
    delay(5000);
    digitalWrite(Output5VPin, LOW);
    digitalWrite(RequestShutDownPin, LOW);
  }
}

void checkOnSerial()
{
  if (Serial.available() > 0)
  {
    char incoming = Serial.read(); // reads one char from the buffer
    if (incoming == '\n')
    { // if the line is over
      //Serial.println(SerialCounter);
      //for (int i = 0; i<SerialCounter; i++)
      
      //{
      //  Serial.print(SerialBuffer[i]);
      //  Serial.print(" ");
      //}
      //Serial.println();
      //delay(25);
      if ((SerialCounter == 1) && (SerialBuffer[0] == NODEID))
      {
        printStatus();
      }
      else
      {
        sendTheStuff();
      }
      SerialCounter = 0;
    }
    else if (incoming == 'X')
    {
      pretendStartup();
    }
    else if (incoming == 'S')
    {
      shutDownPi();
    }
    else
    {
      // each byte is represented as 2 hex characters
      if (FirstHexDone)
      {
        FirstHexDone = false;
        SerialBuffer[SerialCounter] = (FirstHex << 4) | hexval(incoming);
        SerialCounter++;
      }
      else
      {
        FirstHex = hexval(incoming);
        FirstHexDone = true;
      }
    }
  }
}

void checkOnRadio()
{
  if (radio.receiveDone())
  {
    // First lets put what we recieved into IncomingData. We have to do this before we
    // send the ACK because the radio.DATA cache will be overwritten when sending the ACK.
    RadioBuffer = *(Payload*)radio.DATA;
    r.sender = radio.SENDERID;
    r.send2 = radio.TARGETID;
    r.rssi = rssi();
    //datalen = radio.DATALEN;
    if (radio.ACKRequested())
    {
      radio.sendACK();
    }
    printTheStuff();
  }
}

void printTheStuff()
{
  //Serial.println("printing the stuff.");
  hexprint(r.sender);
  hexprint(r.send2);
  hexprint(r.rssi);
  for (int i = 0; i < 61; i++)
  {
    hexprint(RadioBuffer.x[i]);
  }
  Serial.println();
}

void sendTheStuff()
{
  SerialStruct s = *(SerialStruct*)(SerialBuffer);

  //Serial.print("sending to: ");
  //Serial.println(s.send2id);
  //if (s.ack_requested)
  //{
  //  Serial.println("Ack requeested");
  //}
  
  if (s.ack_requested)
  {
    bool success = radio.sendWithRetry(s.send2id, (const void*)(&s.buffer), SerialCounter - 3, s.retries);
    hexprint(NODEID);
    hexprint(s.send2id);
    hexprint(success);
    hexprint(rssi());
    Serial.println();
  }
  else
  {
    radio.send(s.send2id, (const void*)(&s.buffer), sizeof(s.buffer));
  }
}


typedef struct {
  int rssi;
  int temp;
} PrintStatusStruct;
PrintStatusStruct print_status_struct;

void printStatus()
{
  //Serial.print("X");
  print_status_struct.temp = (int)radio.readTemperature(0);
  print_status_struct.rssi = radio.readRSSI();
  byte b[4] = {0};
  memcpy(b, (const void*)&print_status_struct, 4);
  Serial.print("FF");
  for (int i = 0; i < 4; i++)
  {
    hexprint(b[i]);
  }
  Serial.println();
}

byte rssi()
{
  return radio.RSSI + 0x7F;
}

void hexprint(byte b)
{
  if (b < 16)
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
