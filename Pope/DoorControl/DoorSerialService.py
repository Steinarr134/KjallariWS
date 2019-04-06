from SocketCom import Server
import serial
import threading


class Handler(object):
    def __init__(self):
        self.Serial = None
        self.SerialWriteLock = threading.Lock()

    def aquire_serial(self, port):
        self.Serial = serial.Serial(port, 115200)