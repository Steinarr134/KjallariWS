import serial
import threading
import logging

HIGH = 1
LOW = 0


def emptyfunction():
    pass


class ListeningThread(threading.Thread):
    """
    A thread that listens to the Serial port. When something (that ends with a newline) is recieved
    the thread will start up a Send2Parent thread and go back to listening to the Serial port
    """
    def __init__(self, logger, listen2, function2run):
        threading.Thread.__init__(self)
        self.Logger = logger
        self.Listen2 = listen2
        self.Stop = False
        self.React = function2run

    def stop(self):
        self.Stop = True
        self.Listen2.close()

    def run(self):
        self.Logger.debug("Serial listening thread started")
        incoming = ''
        while True:
            try:
                incoming = self.Listen2.readline().rstrip('\n')
            except serial.SerialException as e:
                if not self.Stop:
                    self.Logger.warning("serial exception ocurred: " + str(e))
                    break
            if self.Stop:
                break
            else:
                # self.Logger.debug("Serial port said: " + str(incoming))
                if incoming:
                    self.React(incoming)
        self.Logger.info("Serial listening thread shutting down")


class ReactionThread(threading.Thread):
    def __init__(self, reaction, arduino):
        threading.Thread.__init__(self)
        self.Reaction = reaction
        self.Arduino = arduino
        self.Arduino.ReactionThreads.append(self)
        self.start()

    def run(self):
        self.Reaction()
        self.Arduino.ReactionThreads.remove(self)


class Arduino(object):
    def __init__(self, port, baudrate):
        self.RunReactionsInNewThreads = True

        self.SliderState = None
        self.Button1State = None
        self.Button2State = None

        self._B1_rising = emptyfunction
        self._B1_falling = emptyfunction
        self._B2_rising = emptyfunction
        self._B2_falling = emptyfunction

        self.ReactionThreads = []

        self.Serial = serial.Serial(port, baudrate=baudrate)
        self.ListeningThread = ListeningThread(logging, self.Serial, self._read)
        self.ListeningThread.start()

    def _read(self, incoming):
        self.SliderState = int(incoming[:2], base=16)

        button1state = int(incoming[2])
        if button1state != self.Button1State:
            if self.Button1State is not None:
                if self.Button1State == HIGH:
                    self._react(self._B1_falling)
                else:
                    self._react(self._B1_rising)
            self.Button1State = button1state

        button2state = int(incoming[3])
        if button2state != self.Button2State:
            if self.Button2State is not None:
                if self.Button2State == HIGH:
                    self._react(self._B2_falling)
                else:
                    self._react(self._B2_rising)
            self.Button2State = button2state

    def _react(self, reaction):
        if self.RunReactionsInNewThreads:
            ReactionThread(reaction, self)
        else:
            reaction()

    def bind_button1(self, rising=None, falling=None):
        if rising is not None:
            self._B1_rising = rising
        if falling is not None:
            self._B1_falling = falling

    def bind_button2(self, rising=None, falling=None):
        if rising is not None:
            self._B2_rising = rising
        if falling is not None:
            self._B2_falling = falling
