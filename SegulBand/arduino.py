import serial
from moteinopy import Struct
from threading import Lock


class Motor(object):
    def __init__(self):
        self.Serial = serial.Serial('dev/ttyAMA0', baudrate=115200)
        self.SerialLock = Lock()
        self.Struct = Struct("int Command;")
        self.Status = 99
        self.Play = 1301
        self.Stop = 1302
        self.Rewind = 1303
        self.FastForward = 1304
        self.ReturnToZero = 1305
        self.SetParams = 1306
        self.SetLights = 1307

    def play(self):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.Play})+'\n')

    def stop(self):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.Stop})+'\n')

    def rewind(self):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.Rewind})+'\n')

    def forward(self):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.FastForward})+'\n')

    def return2zero(self):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.ReturnToZero})+'\n')

    def get_temps(self):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.Status})+'\n')
        incoming = self.Serial.readline()
        return self.Struct.decode(incoming)
