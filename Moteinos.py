__author__ = 'SteinarrHrafn'

import serial
import threading
import math
# from ThePope import ListeningThread

Serial = serial.Serial(
    port='COM52',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

SerialLock = threading.Lock()


BaseID = 1
GreenDude = 11
SegulBand = 10


def send(outgoing):
    with SerialLock:
        Serial.write(chr(len(outgoing)) + outgoing)


class Give:
    def __init__(self):
        pass

    @staticmethod
    def byte(i):
        if i > 2**8:
            raise Exception("Of stor tala til ad komast fyrir i byte")

        return ord(i)

    @staticmethod
    def uint16(i):
        if i > 2**16:
            raise Exception("Of stor tala til ad komast fyrir i int")
        return chr(i/2**8) + chr(i % 256)

    @staticmethod
    def uint32(i):
        return(chr(i/2**24) +
               chr(i/2**16) +
               chr(i/2**8) +
               chr(math.floor(i % 256)))


class Take:
    def __init__(self):
        pass

    @staticmethod
    def byte(i):
        return ord(i)

    @staticmethod
    def uint16(i):
        return ord(i[0])*2**8 + ord(i[1])

    @staticmethod
    def uint32(i):
        raise NotImplementedError


give_types = {'byte': Give.byte,
              'int': Give.uint16}

take_types = {'byte': Take.byte,
              'int': Take.uint16}

len_types = {'byte': 1,
             'int': 2}

class Struct:
    def __init__(self, _types):
        self.Types = _types

    def sprint(self, values):
        returner = str()
        while len(values) < len(self.Types):
            values.append(0)
        for i in range(len(self.Types)):
            returner += give_types[self.Types[i]](values[i])
        return returner

    def decode(self, s):
        returner = list()
        for t in self.Types:
            returner.append(take_types[t](s[:len_types[t]]))
            s = s[len_types[t]:]
        return returner


structs = {
    'GreenDude': Struct(['int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int']),
    'TapeRecorder': Struct(['int', 'long', 'long'])
}

a = structs['GreenDude'].sprint([300, 300]) # thetta gefur structid a binary formi

print [ord(A) for A in a]

print structs['GreenDude'].decode(a) # thetta afkodar structid yfir i lista
