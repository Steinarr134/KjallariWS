import serial
from moteinopy import Struct
from threading import Lock
import time

class Motor(object):
    def __init__(self):
        self.Serial = serial.Serial('/dev/ttyUSB0', baudrate=115200)
        time.sleep(1)
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

    def _send_command(self, command):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': command}) + '\n')

    def play(self):
        self._send_command(self.Play)

    def stop(self):
        self._send_command(self.Stop)

    def rewind(self):
        self._send_command(self.Rewind)

    def forward(self):
        self._send_command(self.FastForward)

    def return2zero(self):
        self._send_command(self.ReturnToZero)

    def get_temps(self):
        self._send_command(Status)
        incoming = self.Serial.readline()
        return self.Struct.decode(incoming)
