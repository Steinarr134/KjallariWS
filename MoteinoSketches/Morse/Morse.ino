/*
   12.9.2016. Steina Dögg steina.dogg@gmail.com
   Sketch sem les pinna, ákvarðar hvort input sé dot eða dash, og safnar innslögum í innsláttar fylki.
   Eftir hverja lesningu eru gildin sem hafa safnast borin saman við lausnar kóða.
   Ef lausnarfylki er eins og innsláttarfylki þá sendir moteino kóða á páfann sem svo tengist rás sem opnar segullás.

*/
boolean displayWinner = false;

//Radio tings
#include <RFM69.h>
#define NODEID 15
#define NETWORKID 7
#define FREQUENCY RF69_433MHZ
#define ENCRYPTKEY "HugiBogiHugiBogi"
#define SERIAL_BAUD 9600
#define BaseID 1
RFM69 radio;


int indicator = 9; //built in led
int inputPin = 7;
int ditLength = 150; //Max length for a dit.
boolean previousState;
unsigned long lastChangeToHigh;
unsigned long currentLedOnTime;

byte dit = 1;
byte dah = 2;

int arrayLength = 7; // how many are relevant
const int MaxArrayLength = 15;
byte solution[] = {dit, dit, dah, dah, dah, dit, dit, 0, 0, 0, 0, 0, 0, 0, 0};
int input[MaxArrayLength]; // 15 total

void setup() {
  pinMode(inputPin,INPUT);
  pinMode(indicator,OUTPUT);

  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower();
  radio.encrypt(ENCRYPTKEY);
   
}

void loop() {

  //Stuff to do when input goes from LOW to HIGH.
  if (digitalRead(inputPin) == HIGH && previousState == LOW)
  {
    delay(10);//debounce
    lastChangeToHigh = millis();
    previousState = HIGH;
  }

  //Stuff to do when input goes from HIGH to LOW.
  if (digitalRead(inputPin) == LOW && previousState == HIGH)
  {
    delay(10);//Debounce

    //Serial.println("Seinni");
    unsigned long difference = millis() - lastChangeToHigh;
    if (difference <= ditLength)
    {
      insertIntoArray(dit);
    }
    else
    {
      insertIntoArray(dah);
    }
    previousState = LOW;
  }

//Smá kóði sem má fara út eftir prufanir. Hægt að nota lyklaborð til að gefa morse merki.
  if (Serial.available() > 0) {
    int incomingByte = Serial.parseInt();
    if (incomingByte == 1) insertIntoArray(dit);
    else if (incomingByte == 2) insertIntoArray(dah);
    else if (incomingByte == 3) printInput();
  }

  if (checkWinner()) {
    //Reset the input array.
    digitalWrite(indicator,HIGH);
    displayWinner = true;
    currentLedOnTime = millis();
    resetArray();
  }

 if (displayWinner)
 {
  if (millis()-currentLedOnTime > 1000)
  {
    digitalWrite(indicator,LOW);
    displayWinner = false;
  }
 }

 if (millis()-lastChangeToHigh>2000)
 {
  resetArray();
  lastChangeToHigh = millis();
 }
  
}
//End of loop

void insertIntoArray (byte ditOrDah) { //
  for (int x = arrayLength - 1; x > 0; x--)
  {
    //Rotate the array for all x except [0]
    input[x] = input[x - 1];
  }
  input[0] = ditOrDah;
}


void resetArray() {
  for (int x = 0; x<arrayLength; x++)
  {
    input[x] = 0;
  }
}
boolean checkWinner () {
  for (int x = 0; x < arrayLength; x++)
  {
    if (solution[x] != input[x]) return false;
  }
  return true;
}

void printInput () {
  for (int x = 0; x < arrayLength; x++)
  {
    Serial.println(input[x]);
  }
  Serial.println("---");
}

typedef struct{
  int Command;
  byte Temperature;
  byte Passcode[15];
} Payload;

Payload OutgoingData;
Payload IncomingData;

const int DataLen = sizeof(OutgoingData);

// Command Values:
const int Status = 99;
const int Reset = 98;
const int SetPasscode = 155;
const int CorrectPasscode = 151;

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
      Serial.print("Received: command: ");
      Serial.println(IncomingData.Command);

      switch (IncomingData.Command)
      {
        case Status:
          sendStatus();
          break;
        case Reset:
          reset();
          break;
        case SetPasscode:
          setPasscode();
          break;
      }
    }
  }
}

void reset()
{
  asm volatile(" jmp 0");
}

void setPasscode()
{
  for (byte i = 0; i < MaxArrayLength; i++)
  {
    solution[i] = IncomingData.Passcode[i];
    OutgoingData.Passcode[i] = IncomingData.Passcode[i];
    if (IncomingData.Passcode[i] > 0)
    {
      arrayLength = i+1;
    }
  }
}

void sendStatus()
{
  Serial.println("sending status");
  OutgoingData.Command = Status;
  OutgoingData.Temperature = getTemperature();
  if (!sendOutgoing())
    Serial.println("No ack recieved");
}

byte getTemperature()
{
  return (byte)radio.readTemperature(0);
}

unsigned long LastSendCorrectTime = 0;

void sendMessageAboutCorrect()
{
  if (millis() - LastSendCorrectTime > 5000)
  {
    OutgoingData.Command = CorrectPasscode;
    Serial.println("correct");
    if (!sendOutgoing())
      Serial.println("No ack");
    LastSendCorrectTime = millis();
    Serial.println("message about correct sent");
  }
}

bool sendOutgoing()
{
  return radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), DataLen);
}
