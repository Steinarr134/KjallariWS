# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
from MoteinoConfig import *
import time


seq = [63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0, 63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0]


def stealth_receive(d):
    print "Stealth said: " + str(d)
    if d['Command'] == "Triggered":
        print "Triggered!"
        # Sirens.send("SetPin1High")


Stealth.bind(receive=stealth_receive)

t = 500

if __name__ == '__main__':
    while True:
        bla = raw_input("insert tempo and press enter to reset Stealth: ")
        try:
            t = int(bla.strip())
        except:
            if bla == "quit":
                mynetwork.shut_down()
                break
            elif bla == "test":
                SplitFlap.send("Clear")
                time.sleep(0.5)
                SplitFlap.send("Disp", 'abcdefg')
            elif bla== "elevator":
                Elevator.send("SolveDoor1")
        else:
            Stealth.send("SetSequence", Sequence=seq, Tempo=t)

"""

Hæ strakar, keyrið þetta script, stealt_rceive fallið keyrir sjálfkrafa
þegar páfinn fær eitthvað frá Stealth, getið til dæmis breytt því til að resetta
Stelth eftir nokkrar sekúndur.

Annars er bara að stimpla inn tempoið og ýta á enter (eða stimpla inn ekkert og
þá er sama tempo og síðast notað)

getið skrifað 'test' til að prófa að senda eitthvað á splitflapið til að vera vissir
um að sendingar virka hérna megin frá.

"""


