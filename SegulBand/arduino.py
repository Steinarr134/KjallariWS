import serial
from moteinopy import Struct
from threading import Lock, Thread
import time
import logging
import select

##class readingThread(Thread):
##    def __init__(self, listen2):
##        Thread.__init__(self)
##        self.Listen2 = listen2
##    def run(self):
##        while True:
##            incoming = self.Listen2.readline()
##            print incoming
##

def read(thing, timeout):
    readable, writable, errored = select.select([thing], [], [], timeout)
    if readable:
        return readable.readline()
    else:
        return False


class Motor(object):
    def __init__(self, port='/dev/ttyUSB0'):
        print "trying " + port
        self.Serial = serial.Serial(port, baudrate=38400)
        print "sending X"
        self.Serial.write("X")
        logging.debug("waiting for wakeup sign...")
        readable, writable, errored = select.select([self.Serial], [], [], 2)
        if not readable:
            print "Serial port not readable after 2 seconds"
        else:
            line = self.Serial.readline().rstrip()
            print "port(" + port + ") said: " + line
            if line == b"moteinopy basesketch v2.3":

                port = '/dev/ttyUSB1'
                print "using other one, aka " + port
                print "closing current..."
                self.Serial.close()
                print "opening other one..."
                self.Serial = serial.Serial(port, baudrate=38400)
                print "no reason to wait for wakeup, right?"
                # print "finally, port said: " + self.Serial.readline()
        logging.debug("Arduino Serial successfully initialized")
        self.Port = port
        self.SerialLock = Lock()
        self.Struct = Struct("int Command;"
                             "byte MotorTemp;"
                             "byte DriverTemp;"
                             "long CurrentPos;"
                             "byte LightIntensity;"
                             "int Acceleration;"
                             "int SlowSpeed;"
                             "int FastSpeed;")
        self.Status = 99
        self.Play = 1301
        self.Stop = 1302
        self.Rewind = 1303
        self.FastForward = 1304
        self.ReturnToZero = 1305
        self.SetParams = 1306
        self.SetLights = 1307
        self.SetCurrentPosAsZero = 1308
##        self.bla = readingThread(self.Serial)
##        self.bla.start()

    def _send_command(self, command):
        self._write(self.Struct.encode({'Command': command}) + '\n')
<<<<<<< HEAD
=======

    def _write(self, msg):
        with self.SerialLock:
            logging.debug("sending '{}' to serial port".format(msg))
            self.Serial.write(msg+"\n")
>>>>>>> c244b6121d9efbc178f7085e9bc9abb74a9ab50e

    def _write(self, msg):
        with self.SerialLock:
            logging.debug("sending '{}' to serial port".format(msg))
            self.Serial.write(msg+"\n")
    
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

    def set_current_pos_as_zero(self):
        self.send_command(self.SetCurrentPosAsZero)

    def set_params(self, acc, slow, fast):
        self._write(self.Struct.encode(
<<<<<<< HEAD
            {"Command": self.SetParams, 
=======
            {"Command": self.SetParams,
>>>>>>> c244b6121d9efbc178f7085e9bc9abb74a9ab50e
             "Acceleration": acc,
             "SlowSpeed": slow,
             "FastSpeed": fast}))

    def get_temps(self):
        self._send_command(self.Status)
        incoming = self.Serial.readline()
        return self.Struct.decode(incoming)

    def set_lights(self, intensity):
        self._write(self.Struct.encode({'Command': self.SetLights,
                                        'LightIntensity': intensity}))
