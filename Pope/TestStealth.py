import logging
logging.basicConfig(level=logging.DEBUG)
from Config import *
seq = [63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0, 63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0]


def fun():
    Stealth.send("SetSequence", Sequence=seq, Tempo=500)

