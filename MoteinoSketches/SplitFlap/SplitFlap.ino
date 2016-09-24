// for the radio
#include <RFM69.h>    
#include <SPI.h>
#define NODEID        101    //unique for each node on same network   
#define NETWORKID     7  //the same on all nodes that talk to each other
//Match frequency to the hardware version of the radio on your Moteino (uncomment one):
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define SERIAL_BAUD   9600
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network
typedef struct{
  int Command;
  char Letters[11];
  byte Temperature;
} Payload;
Payload OutgoingData;
Payload IncomingData;
byte DataLen = sizeof(IncomingData);
byte BaseID = 1;

// operating variables
const int Status = 99;
const int Disp = 10101;
const int ClearAll = 10102;


void setup() {
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
  
  pinMode(0, INPUT);
  pinMode(1, OUTPUT);              // 
  //Serial.begin(9600);
  delay(4500);
  Serial.begin(4800, SERIAL_8E2);
  delay(500);
  for (byte i=0; i<11; i++)
  { 
    IncomingData.Letters[i] = 'a';
  }
  disp();
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
      //Serial.print("Received: command: ");
      //Serial.println(IncomingData.Command);
      switch (IncomingData.Command) 
      {
        case Status:
          sendStatus();
          break;
        case Disp:
          disp();
          break;
        case ClearAll:
          clearAll();
          break;
      }
    }
  }
}

void sendStatus()
{
  //Serial.println("sending statuts");
  OutgoingData.Command = Status;
  OutgoingData.Temperature = getTemperature();
  radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),DataLen);
}

byte getTemperature()
{
  return 0; /// vantar
}

void clearAll(){
  //Serial.begin(4800, SERIAL_8E2);   // Stillingar til að geta talað við splitflab  speed=4800, config = 8E2
  Serial.write(130);
 // Serial.begin(9600);               // Stillingar til að geta talað við páfa
}
  

unsigned long LastTime =0 ;


void disp()
{
  if (millis()-LastTime > 3500)
  {
   // Serial.begin(4800, SERIAL_8E2);   // Stillingar til að geta talað við splitflab  speed=4800, config = 8E2
    LastTime = millis();
    byte N=sizeof(IncomingData.Letters);
    for(int i =0;i<N;i++){
      Serial.write(136);              // splitflab gerir sig klart til ad taka a moti (einum) skilabodum
      Serial.write(i+1);              // splitflap nr. i+1 a ad taka a moti skilabodum
      Serial.write(IncomingData.Letters[i]);          // hvad a ad prenta ut a splitflap nr. i+1
    }
    Serial.write(129);                // til ad splitflab prenti ut dau skilabod sem hafa nú þegar verið send splitflabsins 
  }
 // Serial.begin(9600);                 // Stillingar til að geta talað við páfa
}


  
void loop() {
  checkOnRadio(); 
}
  
  





