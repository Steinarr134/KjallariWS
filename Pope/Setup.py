from MoteinoConfig import mynetwork, GreenDude, SplitFlap, \
     Morser, TimeBomb, LockPicking, Elevator, WineBoxHolder, \
     WineBox, TapeRecorder, LieButtons, moteino_status, \
     ShootingRange, Stealth, Sirens, LiePiA, LiePiB, Lie2Buttons, \
     TvPi, StealthSensor, GunDrop, ProbablyDoorSerialPort
from DoorControl import Door as _Door, SocketDoorController as _Dctrl, \
     RemoteDoor as _RemoteDoor
import threading
import logging
import time
from SocketCom import Client
import random
import HostInterface as gui
from Config import *
from Persistance import Perri


exitfunctions = []
exitfunctions.append(mynetwork.shut_down)

def list_threads():
    print "Threads that are still running:"
    for t in threading.enumerate():
        print t


def exit():
    print "Running Exit Functions"
    for func in exitfunctions:
        print "running exitfunc: {}".format(func)
        func()
    list_threads()
    print "exitfunctions done"
    quit()


def elevator_door_send_fun(what):
    if what == "open":
        Elevator.send("OpenDoors", ActiveDoor=1)
    elif what == "close":
        print "Elevator door closes automatically in a few seconds"
    else:
        print "WTF do you mean by '{}' in elevator_door_send_fun".format(what)


logging.debug("Initializing door control")
DoorController = _Dctrl(ProbablyDoorSerialPort)
ElevatorDoor = _Door(DoorController, 0)
SafeDoor = _RemoteDoor(LockPicking, auto_close=False)
BookDrawer = _Door(DoorController, 3)
WineCaseHolderDoor = _RemoteDoor(WineBoxHolder)
WineCaseDoor = _RemoteDoor(WineBox)
StealthDoor = _Door(DoorController, 4)
FromBombDoor = _Door(DoorController, 5)
FinalExitDoor = _Door(DoorController, 6)

print DoorController.Doors

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

Threads = []


def join_threads():
    for t in Threads:
        t.join()


exitfunctions.append(join_threads)


class SplitFlapAssistantObject(object):
    def __init__(self):
        self.ShouldSay = None

    def clear(self):
        if not self.ShouldSay is None:
            SplitFlap.send("Disp", self.ShouldSay)
        else:
            SplitFlap.send("Clear")

    def force_clear(self):
        self.ShouldSay = None
        self.clear()


SplitFlapAssistant = SplitFlapAssistantObject()


class Send2SplitFlapThread(threading.Thread):
    def __init__(self, stuff2send, time_between=7):
        threading.Thread.__init__(self)
        # Threads.append(self)
        self.Stuff2Send = stuff2send
        self.TimeBetween = time_between

        self.setDaemon(True)
        self.start()

    def run(self):
        with Send2SplitFlapLock:
            parts = self.Stuff2Send.split('\n')
            for i, part in enumerate(parts):
                part = part.rstrip()
                part += " "*(11 - len(part))
                SplitFlap.send("Disp", part)
                gui.SplitFlapDisplayLabel.configure(text="Now displaying: '{}'".format(part))
                if self.TimeBetween is None:
                    SplitFlapAssistant.ShouldSay = part
                    return
                time.sleep(self.TimeBetween)
            SplitFlapAssistant.clear()
            gui.SplitFlapDisplayLabel.configure(text="Now displaying: '{}'".format("           "))


def no_ack_fun(d):
    print d
    gui_notify("Oh, no! {} didn't hear us"
               "".format(d['Sender'].Name),
               warning=True)


mynetwork.bind_default(no_ack=no_ack_fun)

perri = Perri()


class Progressor(object):
    def __init__(self):
        self.Checkpoints = [
            "Nothing",
            "Elevator",
            "LockPicking",
            "GreenDude",
            "LieDetectorStart",
            "LieDetectorFinish",
            "WineBox",
            "ShootingRange",
            "Morser",
            "Stealth",
            "TimeBomb",
            "RoomFinished"
        ]
        self.progress = 0
        self.StartTime = None
        self.ProgressTimes = [None for cp in self.Checkpoints]

    def current_cp(self):
        return self.Checkpoints[self.progress]

    def plot(self):
        gui.update_progress_plot(self.ProgressTimes[1:self.progress+1])
    
    def log(self, checkpoint):
        print("###########  Progressor  {}, next progress should be {}"
              "".format(checkpoint, self.Checkpoints[self.progress+1]))
        for i in range(self.progress):
            if self.Checkpoints[i + 1] == checkpoint:
                print("Task already Done!!!")
                return False
        temp = True
        if self.Checkpoints[self.progress+1] != checkpoint:
            temp = gui.askquestion("Advencement to fast!", 
                                   "Players sem to have skipped something, " +
                                   "Should progress be overwritten?") == "yes"
            print "Answer = " + str(temp)
        if temp:
            if checkpoint in self.Checkpoints:
                print "Setting progress to {} (index:{})".format(checkpoint, self.Checkpoints.index(checkpoint))
                self.progress = self.Checkpoints.index(checkpoint)
                if self.StartTime is None:
                    # should happen during elevator escape
                    self.StartTime = time.time()
                self.ProgressTimes[self.Checkpoints.index(checkpoint)] = time.time() - self.StartTime
                self.plot()
                perri.save()
            else:
                raise ValueError("Checkpoint was: {}".format(checkpoint))
        # print "Returning {}".format(temp)
        return temp


def gui_notify(text, warning=False, solved=False, fail=False):
    gui.NotifyQ.put((text, warning, solved, fail))
    gui.globals.NotifyQHistory.append((text, warning, solved, fail))
    perri.save()


progressor = Progressor()


DeviceSubmenus = []

Music = Client(3022)


class Object(object):
    pass        # I do realize this seems pointless but it actually does something


def cumsum(l):
    new_l = []
    s = 0
    for number in l:
        s += number
        new_l.append(s)
    return new_l


if __name__ == '__main__':
    exit()
