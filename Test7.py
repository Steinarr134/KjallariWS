import serial
import time

s = serial.Serial("Com5", baudrate=115200)
time.sleep(2)

while True:
    s.write("010101\n")
    resp = s.readline()
    print("SUCCESS {}".format(int(resp[6:], base=16) - 0x7f) if resp[5] == "1" else "fail")
    time.sleep(0.25)
