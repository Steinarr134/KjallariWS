import serial
from moteinopy import Struct
from threading import Lock, Thread
import time

##class readingThread(Thread):
##    def __init__(self, listen2):
##        Thread.__init__(self)
##        self.Listen2 = listen2
##    def run(self):
##        while True:
##            incoming = self.Listen2.readline()
##            print incoming
##
class Motor(object):
    def __init__(self):
        self.Serial = serial.Serial('/dev/ttyUSB0', baudrate=115200/2)
        time.sleep(1)
        self.SerialLock = Lock()
        self.Struct = Struct("int Command;"
                             "byte MotorTemp;"
                             "byte DriverTemp;"
                             "int CurrentPos;"
                             "byte LightIntensity;")
        self.Status = 99
        self.Play = 1301
        self.Stop = 1302
        self.Rewind = 1303
        self.FastForward = 1304
        self.ReturnToZero = 1305
        self.SetParams = 1306
        self.SetLights = 1307
##        self.bla = readingThread(self.Serial)
##        self.bla.start()

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
        self._send_command(self.Status)
        incoming = self.Serial.readline()
        return self.Struct.decode(incoming)

    def set_lights(self, intensity):
        with self.SerialLock:
            self.Serial.write(self.Struct.encode({'Command': self.SetLights,
                                                  'LightIntensity': intensity})
                              +'\n')
