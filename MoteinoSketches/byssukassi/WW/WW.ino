#include <Wire.h>
#include <TroykaIMU.h>
#define REL 3
#define BUZ 12
#define Porog 8  // порог чуствительности в м/с^2
 
Accelerometer accel;
int Test();

int anti;
int real;

void setup()
{
  Serial.begin(9600);
  Wire.begin();
  accel.begin();  
  pinMode(BUZ, OUTPUT);
  pinMode(REL, OUTPUT);
  tone(BUZ,1000);
  delay(500);
  tone(BUZ,2000);
  delay(500);
  noTone(BUZ);

  anti = Test();
  while(anti != 2 && anti != 1)
  {
    anti = Test();
    delay(1);
  }

  if (anti == 1) real=2;
  else real = 1;
  
}

int flag = 0;
int t[7];
uint64_t currtime;

void loop()
{

  if (Test() == real) 
  {
    //tone(BUZ,1000);
    delay(200);
    //tone(BUZ,2000);
    currtime = millis();
    while (millis() - currtime <10000)
    {
      if (Test() != real) return;
      delay(10);
    }
    digitalWrite(REL,1);
    delay(200);
    //noTone(BUZ);    
    digitalWrite(REL,0);
  }
  
  
}


int Test()
{
  int s = 0;
  int i = 0;
  while(!flag)
  {
    if (accel.readAZ() > Porog) s = 1; 
    else if (accel.readAZ() < -Porog) s = 2;
    else if (accel.readAX() > Porog) s = 3;
    else if (accel.readAX() < -Porog) s = 4;
    else if (accel.readAY() > Porog) s = 5;
    else if (accel.readAY() < -Porog) s = 6;
    else s = 0;
    t[i] = s;
    Serial.println(s);
    i++;
    if (i == 7) i = 0;
    if (t[0] == t[1] && t[0] == t[2] && t[0] == t[3] && t[0] == t[4] && t[0] == t[5] && t[0] == t[6] && t[0] != 0) flag =1;
    delay (10);
    
  }
  flag =0;
  return (t[0]);
}

