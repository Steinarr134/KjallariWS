import serial
import threading
from SocketCom import Client
import json

OPEN = 0
CLOSED = 1


# class RemoteSerial(object):
#     def __init__(self):
#         self.Clien

class Door(object):
    OPEN = 0
    CLOSED = 1

    def __init__(self, controller, position):
        self.Controller = controller
        self.Position = position
        self.State = CLOSED
        self.Controller.add_door(self)

    def is_open(self):
        return self.State == OPEN

    def open(self):
        self.Controller.open(self)

    def close(self):
        self.Controller.close(self)


class EmptyDoorSlot(object):
    def __init__(self):
        self.State = CLOSED


class DoorController(object):
    def __init__(self, port):
        print "Door Control starting on port {}".format(port)
        self.Doors = [EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot()]

        self.Serial = None
        self.SerialWriteLock = None
        self._aquire_serial(port)

    def _aquire_serial(self, port):
        self.Serial = serial.Serial(port, 115200)
        self.SerialWriteLock = threading.Lock()

    def _send(self):
        s = ''
        for door in self.Doors:
            s += str(door.State)

        print "Sending: {}".format(s)
        with self.SerialWriteLock:
            self.Serial.write(s + '\n')

    def _set(self, door, state):
        if not isinstance(door, Door):
            raise ValueError("Expected a Door instance, but got a " + str(type(door)))
        door.State = state
        self._send()

    def open(self, door):
        print "opening door"
        self._set(door, OPEN)

    def close(self, door):
        print "closing door"
        self._set(door, CLOSED)

    def open_all(self):
        for door in self.Doors:
            door.State = OPEN
        self._send()

    def close_all(self):
        for door in self.Doors:
            door.State = CLOSED
        self._send()

    def add_door(self, door):
        if not isinstance(door, Door):
            raise ValueError("Expected a Door instance but got a " + str(door))
        if not isinstance(self.Doors[door.Position], EmptyDoorSlot):
            raise ValueError("Another door is already in that position!")

        self.Doors[door.Position] = door
