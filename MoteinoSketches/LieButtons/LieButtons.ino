/*
 Öfugt: digitalWrite(Lights[i],LOW) kveikir ljosid, HIGH slekkur.


*/
// for the radio
#include <RFM69.h>
#include <SPI.h>
#define NODEID        51    //unique for each node on same network
#define NETWORKID     7  //the same on all nodes that talk to each other
#define FREQUENCY     RF69_433MHZ
#define HIGH_POWER    true
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
RFM69 radio;
bool promiscuousMode = false; //set to 'true' to sniff all packets on the same network

#define waittime 1500  // bid timi, ef rangt password.


const byte PassCodeLength = 3;
byte PassCode[] = {6, 3, 6};

// Here we define our struct.
// The radio always sends 64 bytes of data. The RFM69 library uses 3 bytes as a header
// so that leaves us with 61 bytes. You'll have to fit every peaca of info into 61 bytes
// since multiple structs to single nodes hasn't been implemented into moteinopy.
typedef struct{
  int Command;
  byte PassCode[PassCodeLength];
  byte Lights[7];
} Payload;

// Two instances of payload:
Payload OutgoingData;
Payload IncomingData;
byte BaseID = 1;

// Command values:
const int Status = 99;
const int CorrectPassCode = 5101;
const int ChangePassCode = 5102;
const int Disp = 5103;
const int cmdSetActive = 5104;
const int cmdSetInactive = 5105;
const int cmdLightRight = 5106;
const int cmdLightWrong = 5107;

const byte N = 7;  // fjoldi takka

byte Lights[] = {A0, 9, 7, 6, 5, 4, 3};
byte Buttons[] = {A7, A6, A5, A4, A3, A2, A1};
byte ButtonPresses[] = {-1, -1, -1};

unsigned long int lastbuttontime = 0;
unsigned long int lastChange = 0;
byte havenotified[N] = {false};

byte ON = LOW;
byte OFF = HIGH;
byte IN = LOW;
byte OUT = HIGH;

byte laststate[N] = {OUT};

byte Pressed[N] = {false};
bool dispOn = false;




void setup() {
  // initiate Serial port:
  Serial.begin(115200);
  Serial.println("Ready!");

  // initiate radio:
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  if (HIGH_POWER)
    radio.setHighPower(); //only for RFM69HW!
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);


  ////////////////// put your code here

  OutgoingData.Command = 100;
  sendOutgoingData();

  for (int i = 0; i< N; i++)
  {
    pinMode(Lights[i], OUTPUT);
    pinMode(Buttons[i], INPUT);
  }

  for(int i=0; i<N;i++){
  digitalWrite(Lights[i], HIGH);
  delay(1);
  }
}

/*
2 modes:
- active=1; Thraut virk. Lesa af tökkum, tekka a passcode
  -- ef rett passcode, senda, setja mode 0. Fa leyfi fyrir LightRight
  active=0; Ekki lesa af tokkum, ekki ljós, thraut ekki virk.

*/
boolean active = 1;

void loop(){
  checkOnRadio();

  if(active == 1){
    checkOnButtons();

    // thetta kallar a check fallid, sem skilar true og sendir skilabod ef rett
    // annars skildar thad false, sem er geymt i breytu og notad.
    boolean correct = checkIfCorrectPassCode();

    if((!correct) && ButtonPresses[0] != 255){
      if((millis() - lastChange) >= 500){
        resetButtonPresses();     // setur allt i 255 (== -1)
        lastChange = millis();
        Serial.println("reset 1 triggered");
        //  lightWrong(); // -- commentad ut, pafi kallar a thetta.
        }
      }

    for (int i = 0; i< N; i++)   // N = fjoldi takka, 7
    {
      if (Pressed[i])
      {
       acceptButtonPress(i);
       Pressed[i] = false;
       dispOn = false;
       Serial.print("Button ");
       Serial.print(i);
        Serial.print(" pressed, ButtonPresses=");
       for (int i= 0; i<PassCodeLength; i++)
       {
         Serial.print(ButtonPresses[i]);
         Serial.print(", ");
       }
       Serial.println();
      }
    }
  } // if active

  if(active == 0){
    for(int i=0; i<N;i++){
    digitalWrite(Lights[i], HIGH);
    delay(1);
    }
  } 
}   // ## --- LOOP CLOSE --- ## // 

void resetButtonPresses(){
  for(int i=0;i<PassCodeLength;i++){
    ButtonPresses[i] = -1;
    }
 }

boolean checkIfCorrectPassCode(){
  boolean check = true;
  for (int i=0; i<PassCodeLength; i++){
    if ((PassCode[i]-1) != ButtonPresses[i]){
      check = false;
      // return check;
    }
  }

  if(check){
  active = 0;  
  // lightRight(); // -- commentad ut, pafi kallar a thetta.
  Serial.println("Correct!, informing Pope");
  OutgoingData.Command = CorrectPassCode;
  sendOutgoingData();
  }
  return check;
}

void acceptButtonPress(byte button){
  for (int i=0; i<(PassCodeLength-1); i++){
    ButtonPresses[i] = ButtonPresses[i+1];
  }
  ButtonPresses[PassCodeLength-1] = button;
}

void checkOnButtons(){
  unsigned long int now = millis();
  if (now - lastbuttontime > 80){
    lastbuttontime = now;
    for (int i = 0; i< N; i++){
      byte state = (analogRead(Buttons[i]) > 1000);
      if (!dispOn){
        digitalWrite(Lights[i], state);
      }
      if (state == laststate[i]){
        if (state == IN){
          if (!havenotified[i]){
            Pressed[i] = true;
            havenotified[i] = true;
            lastChange = now;
          }
        }
        else{
          havenotified[i] = false;
        }
      }
      
     laststate[i] = state;
      
    }
  }
}

// byte PassCode[] = {6, 3, 6, 4};
// byte Lights[] = {A0, 9, 7, 6, 5, 4, 3};
// kveikja a tokkum nr. password write(Lights[PassCode[i]-1], high)
// ((PassCode[i]-1) == ButtonPresses[i])


// tharf ad skoda thetta betur. Kveiknar ekki rett a ljosunum, 
// sidasta buttonpress rett blikkar??
// Lights[] pinnar: {A0, 9, 7, 6, 5, 4, 3};
void lightRight(){  // LOW = ljos kveikt, HIGH, ljos slokkt. don't ask.
  for(int i=0; i<N;i++){  // allir lysa, 0.5s
    digitalWrite(Lights[i], LOW); 
    }
  delay(500);
  for(int i=0; i<N;i++){  // allir slokkna
    digitalWrite(Lights[i], HIGH); 
    }
    
  for(int i=0; i<N;i++){  // ljos hleypur yfir
    digitalWrite(Lights[i], LOW);
    delay(120);
    digitalWrite(Lights[i], HIGH);
    delay(120);
  }
  for(int i=0; i<N;i++){ // allir lysa, 1 sek
    digitalWrite(Lights[i], LOW); 
  }
  delay(1000);
  for(int i=0; i<N;i++){
    digitalWrite(Lights[i], HIGH); 
  }
}

void lightWrong(){
  for(int i = 0; i<3; i++){
    
    for (int i = 0; i<N; i++){
      digitalWrite(Lights[i], LOW);
    }
    delay(300);
    for (int i = 0; i<N; i++){
      digitalWrite(Lights[i], HIGH);
    }
    delay(300);
  }
}

void checkOnRadio(){
    // if nothing was received then we'll return immediately
   if (radio.receiveDone())
  {
    // receive the data into IncomingData
    IncomingData = *(Payload*)radio.DATA;

    // send ack if requested
    if (radio.ACKRequested())
    {
      radio.sendACK();
    }
    // useful for debugging:
    Serial.print("Received: command: ");
    Serial.println(IncomingData.Command);

    switch (IncomingData.Command)
    {
      case Status:
        sendStatus();
        break;
      case Disp:
        disp();
        break;
      case ChangePassCode:
        for (int i=0; i<PassCodeLength; i++)
        {
          PassCode[i] = IncomingData.PassCode[i];
        }
      case cmdSetActive:
        active=1;
        break;
      case cmdSetInactive:
        active=0;
        break;
      case cmdLightRight:
        lightRight();
        break;
      case cmdLightWrong:
        lightWrong();
        break;
      default:
        Serial.print("Received unkown Command: ");
        Serial.println(IncomingData.Command);
    }
  }
}

void disp()
{
  dispOn = true;
  for (int i = 0; i<7; i++)
  {
    digitalWrite(Lights[i], IncomingData.Lights[i]);
  }
}

void sendStatus()
{
  OutgoingData.Command = Status;
  for (int i=0; i<PassCodeLength; i++)
  {
    OutgoingData.PassCode[i] = PassCode[i];
  }

  sendOutgoingData();
}

bool sendOutgoingData()
{
  return radio.sendWithRetry(BaseID,(const void*)(&OutgoingData),sizeof(OutgoingData));
}
