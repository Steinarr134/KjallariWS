import logging
logging.basicConfig(level=logging.DEBUG)
from Config import *


seq = [63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0, 63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0]


def stealth_receive(d):
    print "Stealth said: " + str(d)
    if d['Command'] == "Triggered":
        print "Triggered!"
        Sirens.send("SetPin1High")


Stealth.bind(receive=stealth_receive)

t = 500

if __name__ == '__main__':
    while True:
        bla = raw_input("insert tempo and press enter to reset Stelth")
        try:
            t = int(bla.strip())
        except:
            pass

        Stealth.send("SetSequence", Sequence=seq, Tempo=t)