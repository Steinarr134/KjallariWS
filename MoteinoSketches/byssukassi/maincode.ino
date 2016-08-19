// MPU-6050 Short Example Sketch
// By Arduino User JohnChi
// August 17, 2014
// Public Domain
#include<Wire.h>
const int MPU_addr=0x68;  // I2C address of the MPU-6050
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
boolean success;
unsigned long time;
int transistorPin = 6;
int buzzer = 5;

void setup(){
  pinMode(transistorPin, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  Serial.begin(9600);
}
void loop(){
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,6,true);  // request a total of 14 registers
  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)    
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  success = false;
  
  if (abs(AcX)>10000) {
    time = millis();
    Wire.beginTransmission(MPU_addr);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_addr,2,true);
    AcX=Wire.read()<<8|Wire.read();
    while (abs(AcX) > 10000) {
      Wire.beginTransmission(MPU_addr);
      Wire.write(0x3B);
      Wire.endTransmission(false);
      Wire.requestFrom(MPU_addr,2,true);
      AcX=Wire.read()<<8|Wire.read();
      if (millis()-time >= 3000) {
        success = true;
        AcX = 0;
      }
    }
    
    if (success) {
      digitalWrite(buzzer, HIGH);
      Serial.println("Success");
      success = false;
      delay(2000);
      digitalWrite(buzzer, LOW);
      Wire.beginTransmission(MPU_addr);
      Wire.write(0x3D);
      Wire.endTransmission(false);
      Wire.requestFrom(MPU_addr,2,true);
      AcY=Wire.read()<<8|Wire.read();
      if (abs(AcY)>10000) {
        time = millis();
        while (abs(AcY) > 10000) {
          Wire.beginTransmission(MPU_addr);
          Wire.write(0x3D);
          Wire.endTransmission(false);
          Wire.requestFrom(MPU_addr,2,true);
          AcY=Wire.read()<<8|Wire.read();
          if (millis()-time >= 3000) {
            success = true;
            AcY=0;
          }
        }
      }
      if (success) {
        digitalWrite(buzzer, HIGH);
        success = false;
        Serial.println("Success");
        delay(2000);
        digitalWrite(buzzer, LOW);
        Wire.beginTransmission(MPU_addr);
        Wire.write(0x3F);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU_addr,2,true);
        AcZ=Wire.read()<<8|Wire.read();
        if (AcZ>10000) {
          time = millis();
          while (AcZ > 10000) {
            Wire.beginTransmission(MPU_addr);
            Wire.write(0x3F);
            Wire.endTransmission(false);
            Wire.requestFrom(MPU_addr,2,true);
            AcZ=Wire.read()<<8|Wire.read();
            if (millis()-time >= 3000) {
              success = true;
              AcZ=0;
            }
          }
        }
      }
    }
  }
  if (success) {
    Serial.println("The real success");
    digitalWrite(transistorPin, HIGH);
    delay(4000);
    digitalWrite(transistorPin, LOW);
  }
  
  Serial.print("AcX = "); Serial.print(AcX);
  Serial.print(" | AcY = "); Serial.print(AcY);
  Serial.print(" | AcZ = "); Serial.println(AcZ);
  delay(15);
}
