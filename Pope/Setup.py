from MoteinoConfig import mynetwork, GreenDude, SplitFlap, \
     Morser, TimeBomb, LockPicking, Elevator, WineBoxHolder, \
     WineBox, TapeRecorder, LieButtons, moteino_status, \
     ShootingRange, Stealth, Sirens, LiePiA, LiePiB, Lie2Buttons, \
     TvPi
from DoorControl import Door as _Door, DoorController as _Dctrl, \
     RemoteDoor as _RemoteDoor
import threading
import logging
import time
import HostInterface as gui
from Config import *


def elevator_door_send_fun(what):
    if what == "open":
        Elevator.send("OpenDoors", ActiveDoor=1)
    elif what == "close":
        print "Elevator door closes automatically in a few seconds"
    else:
        print "WTF do you mean by '{}' in elevator_door_send_fun".format(what)

logging.debug("Initializing door control")
DoorController = _Dctrl("/dev/ttyUSB1")
ElevatorDoor = _Door(DoorController, 0)
SafeDoor = _RemoteDoor(LockPicking, auto_close=False)
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

logging.debug("Doors Initialized")

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
    print d
    gui.notify("Oh, no! {} didn't hear us"
               "".format(d['Sender'].Name),
               warning=True)

mynetwork.bind_default(no_ack=no_ack_fun)


class Progressor(object):
    def __init__(self):
        self.Checkpoints = [
            "Nothing",
            "Elevator",
            "TapeRecorder",
            "LockPicking",
            "GreenDude",
            "LieDetector",
            "WineBox",
            "ShootingRange",
            "Morser",
        ]
        self.progress = 0

        self.ProgressTimes = []

    def current_cp(self):
        return self.CheckPoints[self.progress]
    
    def log(self, checkpoint):
        print("###########  Progressor  {}, progress is {}"
              "".format(checkpoint, self.Checkpoints[self.progress+1]))
        temp = True
        if self.Checkpoints[self.progress+1] != checkpoint:
            temp = gui.askquestion("Advencement to fast!", 
                                   "Players sem to have skipped something, " +
                                   "Should progress be overwritten?") == "yes"
            print "Answer = " + str(temp)
        if temp:
            self.progress +=1
            self.ProgressTimes.append(time.time())
        return temp



progressor = Progressor()
        
