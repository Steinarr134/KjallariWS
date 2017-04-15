from Config import mynetwork, GreenDude, SplitFlap, \
     Morser, TimeBomb, LockPicking, Elevator, TapeRecorder, WineBoxHolder, \
     WineBox
from DoorControl import Door as _Door, DoorController as _Dctrl, \
     RemoteDoor as _RemoteDoor
import threading
import logging
import time
import pickle
import HostInterface as gui

def elevator_door_send_fun(what):
    if what == "open":
        Elevator.send("OpenDoors", ActiveDoor=1)
    elif what == "close":
        print "Elevator door closes automatically in a few seconds"
    else:
        print "WTF do you mean by '{}' in elevator_door_send_fun".format(what)

DoorController = _Dctrl("/dev/ttyUSB0")
ElevatorDoor = _RemoteDoor(Elevator)
SafeDoor = _Door(DoorController, 1)
BookDrawer = _Door(DoorController, 2)
WineCaseHolderDoor = _RemoteDoor(WineBoxHolder)
WineCaseDoor = _RemoteDoor(WineBox)
StealthDoor = _Door(DoorController, 3)
FromBombDoor = _Door(DoorController, 4)
FinalExitDoor = _Door(DoorController, 5)



Doors = [ElevatorDoor,
         SafeDoor,
         BookDrawer,
         WineCaseHolderDoor,
         WineCaseDoor,
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
        with Send2SplitFlapLock:
            parts = self.Stuff2Send.split('\n')
            for part in parts:
                part = part.strip()
                part += " "*(11 - len(part))
                SplitFlap.send("Disp", part)
                gui.SplitFlapDisplayLabel.configure(text="Now displaying: '{}'".format(part))
                time.sleep(5)
            SplitFlap.send("Clear")
            gui.SplitFlapDisplayLabel.configure(text="Now displaying: '{}'".format("           "))
                
def no_ack_fun(d):
    gui.notify("sdfsdf")

mynetwork.bind_all(no_ack=no_ack_fun)
