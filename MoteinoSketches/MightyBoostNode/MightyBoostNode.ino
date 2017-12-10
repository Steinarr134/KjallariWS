/*
 * This is a sketch for moteino sitting on MightyBoost
 * 
 * It controls the MightyBoost capabilitties and acts as a sender/receiver for the Pi
 * 
 * Behavior:
 * 
 * When Power is lost Send signal to Pi that it should shut down via RequestShutDownPin
 * Subsequentily cut power to the Pi after 15 seconds or sooner if bootOK signal disappears
 * 
 * When external power returns: Return power to Pi
 * 
 * Normal operation: Act as a sender/receiver, bridge between Serial and Network just like 
 * a BaseMoteino would in the moteinopy environment.
 * 
 */


#include <RFM69.h>
#include <SPI.h>
#define NODEID        55   //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define BAUDRATE      115200
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

byte ON = HIGH;
byte OFF = LOW;

byte dtabs = 0;

void debug(char *s)
{
  for (int i = 0; i<dtabs; i++)
  {
    Serial.print('\t');
  }
  Serial.println(s);
}

void setup()
{ // Setup runs once
  Serial.begin(BAUDRATE);
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
  {
    debug("Setting High Power");
    radio.setHighPower(); //only for RFM69HW!
  }
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);

  pinMode(5, OUTPUT);
  analogWrite(5, 100);
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

void delayWradio(long m)
{
  unsigned long tstart = millis();
  while (millis() < tstart + m)
  {
    checkOnRadio();
  }
}

unsigned long LastBatteryCheckTime = 0;
unsigned long LastTimeExternalPower = 0;
unsigned long LastTimeNoExternalPower = 0;

bool externalPowerConnected()
{
  float b = measureBattery();
  return (b > 4.3);
}
void checkOnBattery()
{ 
  // only do this every second
  if (millis() - LastBatteryCheckTime > 1000)
  {
    LastBatteryCheckTime = millis();
    if (externalPowerConnected())
    {
      LastTimeExternalPower = millis();

       // if external power has been on for 10-30 seconds
      if (millis() - LastTimeNoExternalPower > 10000
       && millis() - LastTimeNoExternalPower < 30000)
      {
        startUpPi();
      }
    }
    else
    {
      LastTimeNoExternalPower = millis();

      // if external power has been missing for 10-30 seconds
      if (millis() - LastTimeExternalPower > 10000
       && millis() - LastTimeExternalPower < 30000)
      {
        shutDownPi();
      }
    }
  }
}

void startUpPi()
{
  debug("startUpPi()");
  dtabs++;
  
  if (bootOK()) // if it's already up and running then do nothing
  {
    debug("Already up and running");
    dtabs--;
    return;
  }

  debug("Turning power on");
  digitalWrite(RequestShutDownPin, LOW);
  output5V(ON); // turn on 5V to Pi
  unsigned long tstart = millis();

  // wait until pi starts up, max 60 seconds
  debug("waiting for BootOK signal");
  while ((millis() - tstart < 60000) && !bootOK())
  {
    delay(50);
  }

  // if Pi failed to start up:
  if (!bootOK())
  {
    debug("Pi doesn't seem to be starting up correctly, let's try power cycling");
    output5V(OFF); // shut off 5V to Pi
    delay(1000); // Wait a bit so the Pi definitely shuts off
    debug("yay for recursion");
    startUpPi(); // call this function recursively, yay recursion!
  }
  else
  {
    debug("Pi is up and running");
  }
  
  dtabs--;
}

boolean Output5V = OFF;
void output5V(boolean onoff)
{
  digitalWrite(Output5VPin, onoff);
  Output5V = onoff;
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
  debug("shutDownPi()");
  dtabs++;
  // if 5V outout is off then the Pi can't be on, in wich case this
  // job is very easy, infact it is done.
  if (!Output5VPin)
  {
    debug("5V already off");
    dtabs--;
    return;
  }
  
  // if 5v active and Pi is notup and running it just might be booting up
  if (!bootOK())
  {
    debug("the Pi might be booting up");
    // in that case we sleep for 20 seconds to give the Pi time to boot before shutting it down
    boolean ExternalPowerWasPresent = externalPowerConnected();
    delay(20000);

    // if we are shutting down because of loss of power but power has been returned while waiting we cancel the whole thing
    if (!ExternalPowerWasPresent && externalPowerConnected())
    {
      debug("Power has been restored while we waited, cancelling shutdown");
      dtabs--;
      return;
    }
  }

  // Tell the Pi to shut down
  debug("sending ShutDownRequest");
  digitalWrite(RequestShutDownPin, HIGH);
  unsigned long RequestTime = millis();

  // wait for a maximum of 20 seconds for the Pi to die
  debug("Waiting for shutdown");
  while (bootOK() && millis() - RequestTime < 20000)
  {
    delay(50);
  }
  
  // wait 2 seconds just for the hell of it
  debug("shutdown complete");
  delay(2000);

  // cut the power
  debug("cutting power");
  output5V(OFF);
  digitalWrite(RequestShutDownPin, LOW);
  dtabs--;
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
      FirstHexDone = false;
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
