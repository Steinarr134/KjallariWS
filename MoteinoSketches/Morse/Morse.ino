/*
höf: Karl Birkir
Forritið notar interrupt til að fylgjast með spennunni á morse lyklinum.
Þegar spennan breytist (CHANGE) mælir forritið stöðuna, HIGH/LOW.
Ef HIGH, skra timann, merkja að það hafi verið lyklað.
Ef LOW, tekka hvort hafi verið lyklað, maela hversu langt sidan
Maelingarnar eru settar í fylki, timi[]. 
Finna stystu og lengstu lyklanir og skilgreina sem stutt/langt, 
radad inni annað fylki, dashDot[] eftir hlutföllum af min/max.
dashDot[] sidan borid saman vid solution[] til ad athuga hvort rett hafi verid lyklad.

HARDWARE:
  Morse lykill. 
  - Þarf gott debounce á takkana:
  -- ~100 nF thettir hlidtengt yfir rofa, eda milli 5v og D3 a arduino
  -- Lika debounce i software
  
 D3 pin er external interrupt 1.


Morse standard:
  dot = 1 unit
  dash = 3 units
  dotSpace = 1 unit
  charSpace = 3 units
  wordSpace = 7 units
  
  Mogulegt framtidardot:
  - Nota sveigjanlegann tima til ad athuga hvenar bokstaf er lokid, t.d. ef ekki lyklad i akvedinn tima (charSpace), 
  kalla a vinnslufall og finna ut bokstaf. Sama fyrir ord?
 

*/

#define DashDotRatio 2      // timahlutfall milli dash dot. 2 er sveigjanlegra en 3.
#define spaceDashRatio 3    // timahlutfall milli dash og space, milli stafa. Onotad i thessu samhengi.
#define debounce 20         // debounce, millisec
#define timeArrayLength 9   // fjoldi staka fylkis timamaelinga, þ.e. fjoldi morse lyklana (SOS=9)
#define resetDelay      2000 // millisec. timi thartil reset.

//Radio tings
#include <RFM69.h>
#define NODEID 15
#define NETWORKID 7
#define FREQUENCY RF69_433MHZ
#define ENCRYPTKEY "HugiBogiHugiBogi"
#define SERIAL_BAUD 115200
#define BaseID 1
RFM69 radio;


// ISR breytur
volatile boolean triggered = 0;                    // heldur utan um hvort lyklad hafi verid yfirhofud
unsigned long int timi[timeArrayLength];           // tekur vid maeldum tima milli interrupta
volatile int m = 0;                                // stak counter i timi[m], isr 


// tima utanumhald. millis() skilar unsigned long int
unsigned long int lastRelease = 0;       // timinn fra sidustu lyklun
unsigned long int lastKey = 20;          // software debounce a takka
unsigned long int timer = 100;           // timi fra high til low
unsigned long int now = 0;

// adrar breytur
byte dashDot[timeArrayLength];      // Dot==0, Dash==1.
boolean key = 0;                    // morse-lykill uppi eda nidri
boolean unprocessedData = 0;
byte solution[] = {0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0};   // 0==Dot, 1==Dash.
boolean globalWin = false;



/* Interrupt function + soft debounce */
void irFunc(){
  now = millis();
  if(now - lastKey >= debounce){
      triggered = 1;            // enablar vinnslufall
  }
  lastKey = now;
}

void setup(){
  Serial.begin(SERIAL_BAUD);
  Serial.println("Serial begin");
  // arduino pinni D3 = interrupt 1
  attachInterrupt(1, irFunc, CHANGE);
  pinMode(3, INPUT);

  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower();
  radio.encrypt(ENCRYPTKEY);
}

void loop(){

  checkOnRadio();
  
  // fall sem vinnur ur interruptinu, tekkar hvort high/low, radar tima i fylki
  if(triggered){    
    triggered = 0;
    //  Serial.println("Trigger reset");
    interruptHandler();
  }
  
  // Vinnslufall() : vinnur ur heilum vigri af timamaelingum, thegar hann er fullur: 
  // : finnur max/min, skiptir timi[] nidur i dashDot[], nullar timi[]
  // Ef ounnin gogn til stadar, lykillinn er nidri og sidasta stakid i sample fylkinu er != 0,

  if((unprocessedData) &&  !(key) &&  (timi[timeArrayLength-1] != 0)){
  unprocessedData = 0;
  vinnslufall();
       
  globalWin = winCheck();     // tekkar a hvort lyklad hafi verid rettu ordi
  //  Serial.println(globalWin);
  }

  // 16. dec: breyta, þannig að ef timinn sem er lidinn er c.a. 7x einhver timi[]: -> urvinnsla

  // reset fall. Ef buid ad lykla, en resetDelay timi lidinn fra lyklun, resetta allt. ~1.3 sek?
  if(unprocessedData && (millis() - lastRelease >= resetDelay)){
    nullstilla();
    Serial.println("too slow, reset!");
  }

}           // -- ## -- END LOOP


void nullstilla(){
  m = 0;
  unprocessedData = 0;
  key=0;
  triggered=0;
  for(int i=0; i<timeArrayLength; i++){  
    timi[i] = 0;
    dashDot[i] = 0;     
  }
  // dataDump();
}

// vinnur ur gognunum fyrir hvert interrupt
void interruptHandler(){
 // Serial.println("interruptHandler"); 
  boolean pinValue = digitalRead(3);

  unsigned long int now = millis();
 
  if(pinValue && (key==0)){
    timer = now;
    key = 1;          // lykill uppi
  }

  if(!pinValue && (key==1)){
    if(m > timeArrayLength-1) {m = 0;}  

    timi[m] = now - timer;     // timi sidan HIGH
    key = 0;                   // lykli nidri
    lastRelease = now;  
    unprocessedData = 1; 
    if(m >= 0 && m < timeArrayLength) {m = m + 1;}   
  } 
}

boolean winCheck(){
  boolean win = true;
  for(int i=0; i<timeArrayLength; i++){
    if(dashDot[i] != solution[i]){
      win = false;
    }
  }
  if(win){ 
  Serial.println("Morse correct!");
  sendMessageAboutCorrect();                // transmit
}
  if(!win) Serial.println("Morse fail!");

  return win;
}

void vinnslufall(){
  int tempMax = 0;
    int tempMin = 0;

   for(int i=0; i<timeArrayLength; i++){    // finna max gildi
      if (timi[i] > tempMax) 
         tempMax = timi[i];
    }
    tempMin = tempMax;

    for(int i=0; i<timeArrayLength; i++){   // finna min gildi
      if(timi[i] < tempMin)
          tempMin = timi[i];
    }

    for(int i=0; i<timeArrayLength; i++){     // skipta nidur i dash/dot. heiltoludeiling.
      if( int(timi[i]/tempMin) >= DashDotRatio) dashDot[i] = 1;         
        if(timi[i] != 0){                              // passa ad deila ekki med nulli
          if( int(tempMax/timi[i]) >= DashDotRatio) dashDot[i] = 0;          
      }
    }
     dataDump();     // godur stadur til ad tekka a breytum
    // resetta timi[] og m (timi index)
    for(int i=0; i<timeArrayLength; i++){  
      timi[i] = 0;   // debug
    }
    m=0;  
}

// ----- ## Her fyrir nedan eru bara atridi tengd radio rx/tx

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
const int SetPasscode = 1505;
const int CorrectPasscode = 1501;       // kodinn sem er sendur ef rett morse

void checkOnRadio(){
  if (radio.receiveDone()){
    if (radio.SENDERID == BaseID){
      IncomingData = *(Payload*)radio.DATA;
      if (radio.ACKRequested()){
        radio.sendACK();
      }
      Serial.print("Received: command: ");
      Serial.println(IncomingData.Command);

      switch (IncomingData.Command){
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
  for (byte i = 0; i < MaxArrayLength; i++){
    solution[i] = IncomingData.Passcode[i];
    OutgoingData.Passcode[i] = IncomingData.Passcode[i];
    if (IncomingData.Passcode[i] > 0){
      arrayLength = i+1;
    }
  }
}

void sendStatus()
{
  
  //Serial.println("sending status");
  OutgoingData.Command = Status;
  OutgoingData.Temperature = getTemperature();
  for (int i = 0; i < MaxArrayLength; i++)
  {
    OutgoingData.sendWin = globalWin;
  }
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

bool sendOutgoing(){
  return radio.sendWithRetry(BaseID, (const void*)(&OutgoingData), DataLen);
}

/*       // --- ## DEBUG fall, prentar breytur og fylki
void dataDump(){   
  Serial.println("DATADUMP:");

  Serial.print("timi[]: ");
  for(int i=0; i<timeArrayLength; i++){
      Serial.print(timi[i]);
      Serial.print(", ");
  }
  Serial.println("  ");
  
  Serial.print("dashDot[]: ");
  for(int i=0; i<timeArrayLength; i++){
      Serial.print(dashDot[i]);
      Serial.print(", ");
    }
  Serial.println(" ... ");

  Serial.print("m: ");
  Serial.println(m);
}


*/
