import serial
from Imports import *
from Dictionaries import *
import Queue
import time
__author__ = 'SteinarrHrafn'


class moteino:
    def __init__(self,
                 port,
                 baudrate=115200,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS):
        self.Serial = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, bytesize=bytesize)
        self.SerialLock = threading.Lock
Serial = serial.Serial(
    port='COM50',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
SerialLock = threading.Lock()
# StdoutLock = threading.Lock()

Q = Queue.Queue()


def _hexprints(n):
    if n > 255:
        raise ValueError('n too big for _hexprints')
    if n > 15:
        return hex(n)[2:]
    else:
        return '0' + hex(n)[2:]


def _hex2dec(s):
    if len(s) > 2:
        raise ValueError('s too long for _hex2dec')
    else:
        return int(s, base=16)


class Radio:
    def __init__(self):
        pass
    IsBusy = False
    ResponseExpected = False


def _wait_for_radio():
    while Radio.IsBusy:
        time.sleep(0.01)


def _send2radio(send2id, payload):
    with SerialLock:
        debug_print("Waiting for radio....")
        _wait_for_radio()
        Serial.write(_hexprints(send2id) + payload + '\n')
        debug_print("Sending2Radio: " + _hexprints(send2id) + payload + '\n')


def _send2pope(diction):
    if 'ID' not in diction:
        diction['ID'] = EventIDs['Moteino']
    debug_print("Moteino just added " + str(diction) + " to Q")
    Q.put(diction)


class Byte:
    """
    A class describing the byte datatype
    """
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
    """
    A class describing the int datatype
    """
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
    """
    A class to describe the array datatype, requires the subtype to be defined
    """
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

# a dictionary of known datatypes to more easily call them
types = {
    'byte': Byte,
    'int': Int,
}


class Struct:
    """
    This is a class for parsing a struct through a serial port
    example:

            mystruct = Struct(  "int a;"
                                "int b;")

            send_this_2_serial = mystruct.encode({'a': 1, 'b': 2])

            incoming = mystruct.decode(str_from_serial)

    """
    def __init__(self, structstring):
        self.Parts = list()
        self.NofBytes = 0
        lines = structstring.rstrip(';').split(';')  # remove the last ';' and split by the other ones
        for line in lines:
            temp = line.split()  # split by whitespaces
            if not len(temp) == 2:  # each line should always contain 2 words
                raise ValueError(temp)
            if '[' in temp[1]:  # if we are dealing with an array
                ttemp = temp[1].split('[')
                self.Parts.append((Array(types[temp[0]], int(ttemp[1][:-1])), ttemp[0]))
            else:
                self.Parts.append((types[temp[0]], temp[1]))

    def encode(self, values_dict):
        """
        This function will encode the struct into a HEX string.
        Not all values of the struct must be contained in values_dict,
        those that are not present will be assumed to be 0

        :param values_dict: dict
        :return: str
        """
        returner = str()
        for (Type, Name) in self.Parts:
            if Name in values_dict:
                returner += Type.hexprints(values_dict[Name])
            else:
                returner += Type.hexprints()  # hexprints() assumes value is 0
        return returner

    def decode(self, s):
        """
        This function will decode the struct recieved as a HEX string and return
        a dict with the corresponding values.
        The input string must be sufficiently long to contain the entire struct

        :param s: str
        :return: dict
        """
        returner = dict()
        for (Type, Name) in self.Parts:
            returner[Name] = Type.hex2dec(s[:2*Type.NofBytes])
            s = s[2*Type.NofBytes:]
        return returner


class Device:

    def __init__(self, _id, structstring):
        self.ID = _id
        self.Struct = Struct(structstring)
        self.LastSent = dict()

    def send2radio(self, diction, expect_response=False):
        """
        :param diction: dict
        :param expect_response: bool
        :return:
        """
        Radio.ResponseExpected = expect_response
        _send2radio(send2id=self.ID, payload=self.Struct.encode(diction))
        self.LastSent = diction

    def send2pope(self, payload):
        """
        :param payload: string
        :return: None
        """
        d = self.Struct.decode(payload)
        d['SenderID'] = self.ID
        d['Sender'] = inv_MoteinoIDs[self.ID]
        _send2pope(d)

    def get_status(self):
        self.send2radio({'Command': MoteinoCommands['Status']}, expect_response=True)


devices = dict()


def add_device(name, structstring):
    devices[name] = Device(_id=MoteinoIDs[name],
                           structstring=structstring)

# device = {
#     'GreenDude': Device(_id=MoteinoIDs['GreenDude'],
#                         structstring="int Command;" +
#                                      "byte Lights[7];" +
#                                      "byte Temperature;")
#     ,
#     'Stealth': Device(_id=MoteinoIDs['Stealth'],
#                       structstring="int Command;" +
#                                    "int Beat;" +
#                                    "byte stuff[50];")
#     ,
#     'TestDevice': Device(_id=MoteinoIDs['TestDevice'],
#                          structstring="int Command;"
#                                       "int Something;")
# }


def send(diction, expect_response=False):
    """
    This function should be called from top level script to send someting.
    Input parameter dicttion is a dict that contains what should be sent.
    The structure of diction depends on what device will recieve but diction
    must contain the key 'Send2'

    :param diction: dict
    :param expect_response: bool
    :return: Nothing
    """
    devices[diction['Send2']].send2radio(diction, expect_response=expect_response)


class Moteino2Pope(threading.Thread):
    """
    This is the thread that interprets what the struct recieved by the moteino network
    and fires the
    """
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        debug_print("Recieved from BaseMoteino:  " + self.Incoming)
        sender = devices[inv_MoteinoIDs[_hex2dec(self.Incoming[:2])]]
        if self.Incoming[2:5] is "FFF":
            if self.Incoming[5] is "0":
                _send2pope({'Event': EventIDs['MoteinoNoAck'],
                            'LastSent': dict(sender.LastSent)})
                if Radio.IsBusy:
                    Radio.IsBusy = False
            else:
                #  We recieved an ack and are very happy about it
                if Radio.ResponseExpected:
                    Radio.IsBusy = True
                else:
                    Radio.IsBusy = False
        else:
            sender.send2pope(self.Incoming[2:])


def start_listening():  # starts a thread that listens to the serial port
    serial_listening_thread = ListeningThread(Serial, Moteino2Pope)
    serial_listening_thread.start()


def get_all_statuses():
    for d in devices.values():
        d.get_status()


if __name__ == "__main__":
    add_device(name='GreenDude', structstring="int Command;" + "byte Lights[7];" + "byte Temperature;")
    add_device(name='Stealth', structstring="int Command;" + "int Beat;" + "byte stuff[50];")
    add_device(name='TestDevice', structstring="int Command" + "int Something")
    start_listening()
    get_all_statuses()
