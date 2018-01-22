/*********************************************************
This is a library for the MPR121 12-channel Capacitive touch sensor

Designed specifically to work with the MPR121 Breakout in the Adafruit shop 
  ----> https://www.adafruit.com/products/

These sensors use I2C communicate, at least 2 pins are required 
to interface

Adafruit invests time and resources providing this open source code, 
please support Adafruit and open-source hardware by purchasing 
products from Adafruit!

Written by Limor Fried/Ladyada for Adafruit Industries.  
BSD license, all text above must be included in any redistribution
**********************************************************/

#include <Wire.h>
#include "Adafruit_MPR121.h"

// You can have up to 4 on one i2c bus but one is enough for testing!
Adafruit_MPR121 cap = Adafruit_MPR121();

// Keeps track of the last pins touched
// so we know when buttons are 'released'
uint16_t lasttouched = 0;
uint16_t currtouched = 0;

byte Out1 = 10;
byte Out2 = 11;
void setup() {
  Serial.begin(9600);

  pinMode(Out1, OUTPUT);
  pinMode(Out2, OUTPUT);

  while (!Serial) { // needed to keep leonardo/micro from starting too fast!
    delay(10);
  }
  
  Serial.println("Adafruit MPR121 Capacitive Touch sensor test"); 
  
  // Default address is 0x5A, if tied to 3.3V its 0x5B
  // If tied to SDA its 0x5C and if SCL then 0x5D
  if (!cap.begin(0x5A)) {
    Serial.println("MPR121 not found, check wiring?");
    while (1);
  }
  Serial.println("MPR121 found!");
}


byte sum1 = 0;
byte sum2 = 0;

void loop() {
  // Get the currently touched pads
  currtouched = cap.touched();

  sum1 = 0;
  sum2 = 0;
  
  for (uint8_t i=0; i<12; i++) 
  {
    // it if *is* touched and *wasnt* touched before, alert!
    if (currtouched & _BV(i)) 
    {
      Serial.print("1");
      if (i < 5)
      {
        sum1++;
      }
      else if (i>6)
      {
        sum2++;
      }
    }
    else
    {
      Serial.print("0");
    }
    Serial.print("\t");
  }
  Serial.print("\tout1:");
  Serial.print(sum1 < 4);
  Serial.print("\tout2:");
  Serial.print(sum2 < 4);
  Serial.println();

  digitalWrite(Out1, sum1 < 4);
  digitalWrite(Out2, sum2 < 4);

  // reset our state
  lasttouched = currtouched;

  // comment out this line for detailed data from the sensor!
  return;
  
 
  // put a delay so it isn't overwhelming
  delay(5 00);
}
