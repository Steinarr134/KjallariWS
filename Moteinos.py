import serial
import threading
import math
from Imports import ListeningThread
from Dictionaries import EventIDs, MoteinoCommands, MoteinoIDs
import sys
import demjson

__author__ = 'SteinarrHrafn'

Serial = serial.Serial(
    port='COM51',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)
SerialLock = threading.Lock()
StdoutLock = threading.Lock()


inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}


def hexprints(n):
    if n > 255:
        raise Exception('n of stort i hexprints')
    if n > 15:
        return hex(n)[2:]
    else:
        return '0' + hex(n)[2:]


def _hex2dec(s):
    if len(s) > 2:
        raise Exception('Of langur strengur i hex2dec')
    else:
        return int(s, base=16)


def _send2radio(send2id=None, payload=None):
    with SerialLock:
        Serial.write(hexprints(send2id) + payload + '\n')
        print(hexprints(send2id) + payload + '\n')


def _send2pope(diction):
    with StdoutLock:
        sys.stdout.write(demjson.encode(diction) + '\n')


class Byte:
    NofBytes = 1

    def __init__(self):
        pass

    @staticmethod
    def hexprints(i):
        if i > 2**8:
            raise Exception("Of stor tala til ad komast fyrir i byte")
        return hexprints(i)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s)


class Int:
    NofBytes = 2

    def __init__(self):
        pass

    @staticmethod
    def hexprints(i):
        if i > 2**16:
            raise Exception("Of stor tala til ad komast fyrir i int")
        return hexprints(i/2**8) + hexprints(i % 256)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s[0])*2**8 + _hex2dec(s[1])


class Give:
    def __init__(self):
        pass

    @staticmethod
    def uint32(i):
        return(hexprints(i/2**24) +
               hexprints(i/2**16) +
               hexprints(i/2**8) +
               hexprints(math.floor(i % 256)))


class Take:
    def __init__(self):
        pass

    @staticmethod
    def uint32(i):
        raise NotImplementedError


types = {
    'byte': Byte,
    'int': Int
}


class Struct:
    def __init__(self, _types):
        self.Types = _types

    def code(self, values):
        returner = str()
        while len(values) < len(self.Types):
            values.append(0)
        for (t, v) in map(None, self.Types, values):
            returner += types[t].hexprints(v)
        return returner

    def decode(self, s):
        returner = list()
        for t in self.Types:
            returner.append(t.hex2dec(s[:2*t.NofBytes]))
            s = s[2*t.NofBytes:]
        return returner


structs = {
    'GreenDude': Struct(['int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int']),
    'TapeRecorder': Struct(['int', 'long', 'long']),

}


class GreenDude:
    Struct = Struct(['int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int'])

    def __init__(self):
        pass

    @staticmethod
    def wrap4pope(payload):
        if payload[0] == MoteinoCommands['CorrectPasscode']:
            return {
                'ID': EventIDs['GreenDudeCorrectPasscode'],
                'SpinCounter': payload[1]
            }
        raise NotImplementedError

    @staticmethod
    def send2radio(diction):
        raise NotImplementedError


class Test:
    Struct = Struct(['byte'])
    ID = MoteinoIDs['Test']

    def __init__(self):
        pass

    def wrap4pope(self, payload):
        if payload[0] == MoteinoCommands['Test1']:
            return {
                'ID': EventIDs['Test1'],
                'Sender': self.ID,
                'Command': payload[0]
            }
        raise NotImplementedError

    def send2radio(self, diction):
        if diction['Command'] == MoteinoCommands['Test2']:
            _send2radio(send2id=self.ID,
                        payload=[diction['Command']])

device = {
    'GreenDude': GreenDude(),
    'Test': Test()

}
# a = structs['GreenDude'].code([300, 300])  # thetta gefur structid sem hexastreng
#
# send(send2id=IDs['GreenDude'], payload=a)


class Pope2Moteino(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        diction = demjson.decode(self.Incoming)
        device[diction['Send2ID']].wrap(diction)


class Moteino2Pope(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        sender = device[inv_MoteinoIDs[_hex2dec(self.Incoming[:2])]]
        # print "sender: " + str(sender)
        payload = sender.Struct.decode(self.Incoming[2:])
        # print "payload: " + str(payload)
        outgoing = sender.unwrap(payload)
        # print outgoing
        with StdoutLock:
            sys.stdout.write(demjson.encode(outgoing) + '\n')


SerialListeningThread = ListeningThread(Serial, Moteino2Pope)
SerialListeningThread.start()

PopeListeningThread = ListeningThread(sys.stdin, None)
PopeListeningThread.start()
