import serial
import threading
from Imports import ListeningThread
from Dictionaries import *
import sys
import demjson
__author__ = 'SteinarrHrafn'

Serial = serial.Serial(
    port='COM3',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)
SerialLock = threading.Lock()
StdoutLock = threading.Lock()


def _hexprints(n):
    if n > 255:
        raise ValueError('n of stort i hexprints')
    if n > 15:
        return hex(n)[2:]
    else:
        return '0' + hex(n)[2:]


def _hex2dec(s):
    if len(s) > 2:
        raise ValueError('Of langur strengur i hex2dec')
    else:
        return int(s, base=16)


def _send2radio(send2id=None, payload=None):
    print " sending2radio..."
    with SerialLock:
        print "sending..."
        Serial.write(_hexprints(send2id) + payload + '\n')
        print("Sending2Radio: " + _hexprints(send2id) + payload + '\n')


def _send2pope(diction):
    diction['ID'] = EventIDs['Moteino']
    with StdoutLock:
        sys.stdout.write(demjson.encode(diction) + '\n')


class Byte:
    NofBytes = 1

    def __init__(self):
        pass

    @staticmethod
    def hexprints(i=0):
        if i > 2**8:
            raise Exception("Of stor tala til ad komast fyrir i byte")
        return _hexprints(i)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s)


class Int:
    NofBytes = 2

    def __init__(self):
        pass

    @staticmethod
    def hexprints(i=0):
        if i > 2**16:
            raise Exception("Of stor tala til ad komast fyrir i int")
        return _hexprints(i % 256) + _hexprints(i/2**8)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s[2:4])*2**8 + _hex2dec(s[:2])


class Array:

    def __init__(self, subtype, n):
        self.SubType = subtype
        self.N = n
        self.NofBytes = subtype.NofBytes*n

    def hexprints(self, l=list()):
        returner = str()
        while len(l) < self.N:
            l.append(0)
        for L in l:
            returner += self.SubType.hexprints(L)
        return returner

    def hex2dec(self, s):
        returner = list()
        for i in range(self.N):
            returner.append(self.SubType.hex2dec(s[:self.SubType.NofBytes*2]))
            s = s[self.SubType.NofBytes:]
        return returner


types = {
    'byte': Byte,
    'int': Int,
}


class Struct:
    def __init__(self, structstring):
        self.Parts = list()
        lines = structstring.rstrip(';').split(';')
        for line in lines:
            temp = line.split(' ')
            if not len(temp) == 2:
                raise ValueError(temp)
            if '[' in temp[1]:
                ttemp = temp[1].split('[')
                self.Parts.append((Array(types[temp[0]], int(ttemp[1][:-1])), ttemp[0]))
            else:
                self.Parts.append((types[temp[0]], temp[1]))

    def encode(self, values_dict):
        returner = str()
        for (Type, Name) in self.Parts:
            if Name in values_dict:
                returner += Type.hexprints(values_dict[Name])
            else:
                returner += Type.hexprints()
        return returner

    def decode(self, s):
        returner = dict()
        for (Type, Name) in self.Parts:
            returner[Name] = Type.hex2dec(s[:2*Type.NofBytes])
            s = s[2*Type.NofBytes:]
        return returner


# structs = {
#     'GreenDude': Struct(['int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int']),
#     'TapeRecorder': Struct(['int', 'long', 'long']),
#     'Stealth': Struct(['int', 'int'] + list(repeat('byte', 50))),
# }

class Device:

    def __init__(self, _id, structstring):
        self.ID = _id
        self.Struct = Struct(structstring)

    def send2radio(self, diction):
        print "Device with ID: " + str(self.ID)
        _send2radio(send2id=self.ID, payload=self.Struct.encode(diction))

    def send2pope(self, payload):
        d = self.Struct.decode(payload)
        d['SenderID'] = self.ID
        _send2pope(d)


'''
class GreenDude(Device):



    def __init__(self):
        Device.__init__(self,
                        _id=MoteinoIDs['GreenDude'],
                        structstring="int Command;" +
                                     "byte Lights[7];" +
                                     "byte Temperature;")


    def translate4pope(self, payload):
        if payload['Command'] == MoteinoCommands['CorrectPasscode']:
            return {
                'ID': EventIDs['GreenDudeCorrectPasscode'],
            }
        elif payload['Command'] == MoteinoCommands['Status']:
            return {
                "ID": EventIDs['MoteinoStatus'],
            }
        else:
            raise NotImplementedError(str(payload))

    # def send2radio(self, diction):
    #     if diction['Command'] == self.Commands['Status']:
    #         self.send({
    #             'Command': self.Commands['Status']
    #         })
    #     elif diction['Command'] == self.Commands['Disp']:
    #         self.send({
    #             'Command': self.Commands['Disp'],
    #             'Lights': diction
    #         })
    #     else:
    #         raise NotImplementedError(str(diction))


class Stealth:
    ID = 7
    Struct = Struct("int Command;" +
                    "int Beat;" +
                    "byte stuff[50];")

    def __init__(self):
        pass

    def wrap4pope(self, payload):
        raise NotImplementedError(str(payload))



class Test:
    Struct = Struct("byte b;")
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
        raise NotImplementedError(payload)

    # def send2radio(self, diction):
    #     # if diction['Command'] == MoteinoCommands['Test2']:
    #     #     _send2radio(send2id=self.ID,
    #     #                 payload=[diction['Command']])
    #     # else:
    #     #     raise NotImplementedError(str(diction))
    #     print "sldfkj"
    '''

device = {
    'GreenDude': Device(_id=MoteinoIDs['GreenDude'],
                        structstring="int Command;" +
                                     "byte Lights[7];" +
                                     "byte Temperature;"),
    # 'Test': Test(),
    'Stealth': Device(_id=MoteinoIDs['Stealth'],
                      structstring="int Command;" +
                                   "int Beat;" +
                                   "byte stuff[50];")
}
# a = structs['GreenDude'].code([300, 300])  # thetta gefur structid sem hexastreng
#
# send(send2id=IDs['GreenDude'], payload=a)


class Pope2Moteino(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming
        print incoming

    def run(self):
        diction = demjson.decode(self.Incoming)
        # diction = dict(self.Incoming)
        print "sending 2 class: Device"
        device[inv_MoteinoIDs[diction['Send2ID']]].send2radio(diction)


class Moteino2Pope(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        sender = device[inv_MoteinoIDs[_hex2dec(self.Incoming[:2])]]
        sender.send2pope(self.Incoming[2:])

# print Serial.readline()
# raw_input("....")
SerialListeningThread = ListeningThread(Serial, Moteino2Pope)
SerialListeningThread.start()
#
PopeListeningThread = ListeningThread(sys.stdin, Pope2Moteino)
PopeListeningThread.start()
# if __name__ == 'main':
#     print "sdlfkjsf"

a = {"Send2ID":11,"Command":122,"Lights":[1,1,1,2,2,1,1]}