from Config import mynetwork, GreenDude, SplitFlap, \
     Morser, TimeBomb, LockPicking, Elevator, TapeRecorder
from DoorControl import Door as _Door, DoorController as _Dctrl, \
     RemoteDoor as _RemoteDoor
import threading
import logging
import time
import pickle

def elevator_door_send_fun(what):
    if what == "open":
        Elevator.send("OpenDoors", ActiveDoor=1)
    elif what == "close":
        print "Elevator door closes automatically in a few seconds"
    else:
        print "WTF do you mean by '{}' in elevator_door_send_fun".format(what)

DoorController = _Dctrl("/dev/ttyUSB0")
ElevatorDoor = _RemoteDoor(elevator_door_send_fun, 5)
SafeDoor = _Door(DoorController, 1)
BookDrawer = _Door(DoorController, 2)
WineCaseHolderDoor = _Door(DoorController, 6)
StealthDoor = _Door(DoorController, 3)
FromBombDoor = _Door(DoorController, 4)
FinalExitDoor = _Door(DoorController, 5)

Doors = [ElevatorDoor,
         SafeDoor,
         BookDrawer,
         WineCaseHolderDoor,
         StealthDoor,
         FromBombDoor,
         FinalExitDoor]

Send2SplitFlapLock = threading.Lock()

class Send2SplitFlapThread(threading.Thread):
    def __init__(self, stuff2send):
        threading.Thread.__init__(self)
        self.Stuff2Send = stuff2send
        self.start()

    def run(self):
        time.sleep(10)
        with Send2SplitFlapLock:
            parts = self.Stuff2Send.split('\n')
            for part in parts:
                part = part.strip()
                part += " "*(11 - len(part))
                SplitFlap.send("Disp", part)
                time.sleep(5)
            SplitFlap.send("Clear")
            
