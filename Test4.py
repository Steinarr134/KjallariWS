import serial
import time

Serial = serial.Serial(port='COM51')

while True:
    a = Serial.readline()
    print a
    time.sleep(0.01)
    response = "FF" + a[:2] + "01\n"
    Serial.write(response)
    time.sleep(0.1)
    Serial.write("0a626c61626c61626c612e01000200030004000500\n")
    print response
