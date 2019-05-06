//********************************************//
// DISTANCE MEASUREMENT USING                 //
// SHARP GP2Y0A21YK0F                         //
// PLACE 470µF CAPACITOR ON VCC NEAR SENSOR   //
//           FOR POWER SUPPLY STABILISATION   //
//              --MAY 2019 - INGI V.--        //
//********************************************//

#include <SharpIR.h>
// https://github.com/guillaume-rico/SharpIR

#define threshold 30  // Threshold for triggering
#define rel 8         // Relay used for testing
#define ledPin 13     // Visual aid
#define IR A0         // the pin where your sensor is attached
#define model 1080    // used 1080 because model GP2Y0A21YK0F is used

SharpIR SharpIR(IR, model);

void setup() {
 Serial.begin(9600);        // Start Serial communication
 pinMode (rel, OUTPUT);     // TEST RELAY 
 pinMode (ledPin, OUTPUT);  // Test LED
}


void loop() {
  delay(70);                      // Signal stabilizing (deBounce)
  int dis=SharpIR.distance();     // this returns the distance to the object you're measuring
//  Serial.print("distance: ");   // prints to the serial monitor
//  Serial.println(dis);          // prints value to serial monitor

//---------- DO SOMETHING ---------------//
  int i;
  if (dis < threshold){           // distance less than X cm
    for (i=0; i<10; i++){         // BLINKY BLINKY
      digitalWrite (ledPin, HIGH);
      delay(100);
      digitalWrite (ledPin, LOW);
      delay(100);
    }     // end of for loop
  }       // end of if loop
//----------------------------------------//     
} // end of code
