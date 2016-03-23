import serial
import threading
import time
import sys
__author__ = 'SteinarrHrafn'

"""
Example usage:


from MoteinoBeta import MoteinoNetwork


class MyNetwork(MoteinoNetwork):
    def __init__(self):
        MoteinoNetwork.__init__(self, port='COM50', baudrate=9600)

    def recieve(self, diction): #  overwrite this to respond
        print diction


mynetwork = MyNetwork()
mynetwork.add_device('TestDevice', 0, "int Command;int Something;")
mynetwork.start_listening()

mynetwork.send('TestDevice', {'Command': 123, 'Something': 456})
"""


def dprint(s, newline=True):  # print for debugging purposes
    if True:
        sys.stdout.write(s + ('\n' if newline else ''))


def _hexprints(n):
    """
    Returns a hex sting of lengt 2 that represents the number n
    :raises ValueRrror if 0 > n or n > 255
    :param n: int
    :return: string
    """
    if 0 > n or n > 255:
        raise ValueError('n too big for _hexprints')
    if n > 15:
        return hex(n)[2:]
    else:
        return '0' + hex(n)[2:]


def _hex2dec(s):
    """
    returns the int represented by hex string s

    :param s: string
    :return: int
    """
    if not len(s) == 2:
        raise ValueError("s(" + str(s) + ") did not fit for _hex2dec")
    else:
        # debug_print("S: " + s)
        return int(s, base=16)


class DataType(object):
    pass
    # NofBytes = None
    #
    # @staticmethod
    # def hexprints(data):
    #     pass
    #
    # @staticmethod
    # def hex2dec(s):
    #     pass


class Byte(DataType):
    """
    A class describing the byte datatype
    """
    NofBytes = 1
    ReturnType = int

    @staticmethod
    def hexprints(i=0):
        if i > 2**8:
            raise ValueError("The number given to Byte.hexprints() doesn't fit, it was: " + str(i))
        return _hexprints(i)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s)


class Char(Byte):
    ReturnType = str


class UnsignedInt(DataType):
    """
    A class describing the unsigned int datatype
    """
    NofBytes = 2
    ReturnType = int

    @staticmethod
    def hexprints(i=0):
        if not 0 <= i < 2**16:
            raise ValueError("The number given to UnsignedInt.hexprints() doesn't fit, it was: " + str(i))
        return _hexprints(i % 256) + _hexprints(i/2**8)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s[2:4])*2**8 + _hex2dec(s[:2])


class Int(DataType):
    NofBytes = 2
    ReturnType = int

    @staticmethod
    def hexprints(i=0):
        if not -32769 < i < 32768:
            raise ValueError("The number given to Int.hexprints() doesn't fit, it was: " + str(i))
        if i >= 0:
            return UnsignedInt.hexprints(i)
        else:
            return UnsignedInt.hexprints(2**16+i)

    @staticmethod
    def hex2dec(s):
        i = UnsignedInt.hex2dec(s)
        if i > 32767:
            i -= 32767
        return i


class Bool(DataType):
    NofBytes = 1
    ReturnType = bool

    @staticmethod
    def hexprints(i=False):
        if type(i) is not bool:
            raise ValueError('unexpected arguement in Bool.hexprint, expected bool but got ' + str(type(i)))
        if i:
            return "01"
        else:
            return "00"

    @staticmethod
    def hex2dec(s):
        if not len(s) == 2:
            raise ValueError('Bool.hex2dec expected string of length 2 but got: ' + s)
        if s == "00":
            return False
        else:
            return True


class Array(DataType):
    """
    A class to describe the array datatype, requires the subtype to be defined
    """
    def __init__(self, subtype, n):
        if not issubclass(subtype, DataType):
            raise ValueError("problem in Array.__init__(), subtype is not a Datatype!")
        self.SubType = subtype
        self.N = n
        self.NofBytes = subtype.NofBytes*n

    def hexprints(self, l=None):

        # untested code:
        if type(l) is str:
            s = str(l)
            l = list()
            for S in s:
                l.append(ord(S))
        returner = str()
        if not l:
            l = list()
        # /untested code
        while len(l) < self.N:
            l.append(0)
        for L in l:
            returner += self.SubType.hexprints(L)
        return returner

    def hex2dec(self, s):
        returner = list()
        for i in range(self.N):
            returner.append(self.SubType.hex2dec(s[:self.SubType.NofBytes*2]))
            s = s[self.SubType.NofBytes*2:]
        if self.SubType == Char:
            idk = str()
            for i in returner:
                idk += chr(i)
            return idk
        else:
            return returner

# a dictionary of known datatypes to more easily call them
types = {
    'byte': Byte,
    'char': Char,
    'unsigned int': UnsignedInt,
    'int': Int,
    'bool': Bool,
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
            temp = line.rsplit(' ', 1)  # split by whitespaces
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
        # debug_print("S: \"" + s + "\"")
        # debug_print("Parts: " + str(self.Parts))
        for (Type, Name) in self.Parts:
            returner[Name] = Type.hex2dec(s[:2*Type.NofBytes])
            s = s[2*Type.NofBytes:]
        return returner


class Device:

    def __init__(self, network, _id, structstring, name):
        self.ID = _id
        self.Struct = Struct(structstring)
        self.LastSent = dict()
        self.Network = network
        self.Name = name

    def send2radio(self, diction, expect_response=False, max_wait=None):
        """
        :param max_wait: int
        :param diction: dict
        :param expect_response: bool
        :return: None
        """
        self.Network.ResponseExpected = expect_response
        self.LastSent = diction
        self.Network.send2radio(send2id=self.ID, payload=self.Struct.encode(diction), max_wait=max_wait)

    def send2parent(self, payload):
        """
        :param payload: string
        :return: None
        """
        d = self.Struct.decode(payload)
        d['SenderID'] = self.ID
        d['Sender'] = self.Name
        self.Network.RadioIsBusy = False
        if not self.Network.ReceiveWithSendAndReceive:
            self.Network.receive(self, d)
        else:
            self.Network.LastReceived = d
            self.Network.ReceiveWithSendAndReceive = False

    def send(self, diction, expect_response=False, max_wait=None):
        self.Network.send(self.Name,
                          diction=diction,
                          expect_response=expect_response,
                          max_wait=max_wait)

    def send_and_receive(self, diction):
        return self.Network.send_and_receive(self.Name, diction=diction)


class BaseMoteino(Device):
    def __init__(self, network):
        Device.__init__(self, network, 0xFF, "byte Sender;bool AckReceived", 'BaseMoteino')

    def send2parent(self, payload):
        dprint("BaseMoteino.send2parent")
        d = self.Struct.decode(payload)
        if d['Sender'] not in self.Network.devices:
            raise ValueError("Sender not in known devices")
        sender = self.Network.devices[d['Sender']]
        if d['AckReceived']:
            if not self.Network.ResponseExpected:
                self.Network.RadioIsBusy = False
            self.Network.ack(sender.Name, sender.LastSent)
        else:
            self.Network.RadioIsBusy = False
            self.Network.no_ack(sender.Name, sender.LastSent)


class Send2ParentThread(threading.Thread):
    """
    This is the thread that interprets the struct recieved by the moteino network
    and runs the recieve, no_ack or ack function. The user is allowed to hijack this
    thread from the recieve, no_ack or ack functions.
    """
    def __init__(self, network, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming
        self.Network = network

    def run(self):
        # dprint("Recieved from BaseMoteino:  " + self.Incoming)

        # The first byte from the hex string is the sender ID.
        # We use that to get a pointer to the sender (an instance of the Device class)

        sender_id = _hex2dec(self.Incoming[:2])
        if sender_id not in self.Network.devices:
            print "Something must be wrong because BaseMoteino just recieved a message " \
                  "from moteino with ID: " + str(sender_id) + " but no such device has " \
                  "been registered to the network. Btw the raw data was: " + self.Incoming
        else:
            sender = self.Network.devices[sender_id]
            sender.send2parent(self.Incoming[2:])


class ListeningThread(threading.Thread):
    """
    A thread that listens to the Serial port. When something (that ends with a newline) is recieved
    the thread will start up a Send2Parent thread and go back to listening to the Serial port
    """
    def __init__(self, network):
        threading.Thread.__init__(self)
        self.Network = network
        self.Listen2 = network.Serial

    def stop(self):
        self.Listen2.close()

    def run(self):
        while True:
            try:
                incoming = self.Listen2.readline()
            except serial.SerialException:
                break
            incoming.rstrip('\n')  # nota [:-1]?
            print "ABC we got: " + incoming
            fire = Send2ParentThread(self.Network, incoming)
            fire.start()


class MoteinoNetwork:
    """
    This is the class that user should inteface with. It is a module that
    ables the user to communicate with moteinos through a top level script.

    Example Usage:

    # Define a subclass MyNetwork
    class MyNetwork(MoteinoNetwork):
        def __init__(self):
            # Initialize superclass and pass information about the Serial port
            MoteinoNetwork.__init__(self, port='COM50', baudrate=9600)

        # Overwrite the recieve function, put here how you want to
        def recieve(self, diction):
            print "We just recieved:"
            print diction
            print "from the moteino network"

    # Make an instance of the class we just made
    mynetwork = MyNetwork()
    # Define a device on the network
    mynetwork.add_device('TestDevice', 0, "int Command;int Something;")
    # We can use this to send information.
    mynetwork.send('TestDevice', {'Command': 123, 'Something': 456})

    """

    def __init__(self,
                 port,
                 baudrate=115200,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS):

        self.Serial = serial.Serial(port=port,
                                    baudrate=baudrate,
                                    parity=parity,
                                    stopbits=stopbits,
                                    bytesize=bytesize,
                                    writeTimeout=0.5)
        # Call readline to wait for BaseMoteino to start up
        dprint("Waiting for BaseMoteino to send a waking up sign...", False)
        self.Serial.readline()
        dprint("We got it!")
        self.SerialLock = threading.Lock()

        self.RadioIsBusy = False
        self.ResponseExpected = False
        self.ReceiveWithSendAndReceive = False
        self.print_when_acks_recieved = False

        self.devices = dict()
        self.serial_listening_thread = None
        self._serial_listening_thread_is_active = False
        self.max_wait = 500
        self.LastReceived = None

        self.BaseMoteino = BaseMoteino(self)
        self._add_device(self.BaseMoteino)
        self.start_listening()

    def _wait_for_radio(self, max_wait=None):
        """
        There are two reasons for waiting for radio.
            1 - When the base sends a packet and waits for an ACK
                it is not processing from the serial port. If we would
                just keep printing more and more packets to send it
                might fill the buffer on the BaseMoteino's serial port
                and cause lost data.
            2 - It is preferable that devices on the network act mostly
                like slaves, that is, don't talk much unless asked to.
                Most tyoes of information should therefore be requested
                by the master (the users python script). In this case
                the user should call mynetwork.send() with expect_response
                as True. This will cause the module to wait until it
                recieves a packet or the max_wait period.

        :param max_wait: int
        """
        if max_wait is None:
            max_wait = self.max_wait
        counter = 1
        # dprint("Waiting for radio....")
        t = time.time()
        while self.RadioIsBusy:
            # print "waiting..."
            counter += 1
            time.sleep(0.01)
            if (time.time() - t)*1000 > max_wait:
                break
        dprint("I waited for radio for " + str((time.time() - t)*1000) + " ms")

    def send2radio(self, send2id, payload, max_wait=None):
        """
        To prevent multiple threads from printing to the Serial port at the same time
        all printing is done through this function and using the threading.Lock() module
        :param send2id: int
        :param payload: str
        :param max_wait: int
        """
        with self.SerialLock:
            # dprint("Waiting for radio....")
            self.Serial.write(_hexprints(send2id) + payload + '\n')
            dprint("we sent: " + _hexprints(send2id) + payload)
            self.RadioIsBusy = True
            self._wait_for_radio(max_wait=max_wait)

    def _add_device(self, device):
        """
        A private method that adds device to the networks list of devices
        :param device: Device
        :return:
        """
        self.devices[device.Name] = device
        self.devices[device.ID] = device

    def add_device(self, name, _id, structstring):
        """
        This function defines a device on the network
        :param name: str
        :param _id: int
        :param structstring: str
        """
        if _id == 0xFF:
            raise ValueError("Device ID can't be 255 (0xFF) because that is ")

        d = Device(network=self,
                   _id=_id,
                   structstring=structstring,
                   name=name)
        self._add_device(d)

        return d

    def send_and_recieve(self, send2, diction, max_wait=None):
        """
        This function can be called from top level script. It sends the
        information found in diction to the device specified with send2.
        It will then wait until the network received something and return
        what was received. This will prevent the receive() function from
        being called.

        :param send2: str or Device
        :param diction: dict
        :return: dict
        """
        self.ReceiveWithSendAndReceive = True
        temp = id(self.LastReceived)
        self.send(send2=send2,
                  diction=diction,
                  expect_response=True,
                  max_wait=max_wait)
        if id(self.LastReceived) != temp:
            return self.LastReceived
        else:
            return None

    def send(self, send2, diction, expect_response=False, max_wait=None):
        """
        This function should be called from top level script to send someting.
        Input parameter diction is a dict that contains what should be sent.
        The structure of diction depends on the struct that the device expects.
        Any parameter missing in diction will be assumed to be 0

        :param send2: str or Device
        :param diction: dict
        :param expect_response: bool
        :param max_wait: int
        """
        if type(send2) is str or type(send2) is int:
            self.devices[send2].send2radio(diction, expect_response=expect_response, max_wait=max_wait)
        elif type(send2) is Device:
            send2.send2radio(diction=diction, expect_response=expect_response, max_wait=max_wait)
        else:
            raise ValueError("send2 must be string or Device but was " + str(type(send2)))

    def start_listening(self):  # starts a thread that listens to the serial port
        if not self._serial_listening_thread_is_active:
            self.serial_listening_thread = ListeningThread(network=self)
            if not self.Serial.isOpen():
                self.Serial.open()
            self.serial_listening_thread.start()
            self._serial_listening_thread_is_active = True

    def stop_listening(self):
        self.serial_listening_thread.stop()
        self.Serial.close()
        self._serial_listening_thread_is_active = False

    def receive(self, sender, diction):
        """
        User should overwrite this function
        :param sender: Device
        :param diction: dict
        """
        print "MoteinoNetwork received: " + str(diction) + "from" + sender.Name

    def no_ack(self, sender, last_sent_diction):
        """
        User might want to overwrite this function
        :param sender: Device
        :param last_sent_diction: dict
        """
        print "Oh no! We didn't recieve an ACK from " + sender.Name + " when we sent " + str(last_sent_diction)

    def ack(self, sender, last_sent_diction):
        """
        This funcion is totally unnecessary.... mostly for debugging but maybe
        it will be usefull someday to overwrite this with something
        :param sender: Device
        :param last_sent_diction: dict
        """
        if self.print_when_acks_recieved:
            print sender.Name + " responded with an ack when we sent: " + str(last_sent_diction)
