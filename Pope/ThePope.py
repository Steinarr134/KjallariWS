from Setup import *
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

# Initialize Scheduler

scheduler = BackgroundScheduler()
scheduler.start()


# A nice little quick hand function to run something at a later time using the Scheduler.
def run_after(func, seconds=0, minutes=0):
    scheduler.add_job(func,
                      'date',
                      run_date=datetime.fromtimestamp(time.time() + seconds + 60*minutes))


# Configurate logging module
logging.basicConfig(level=logging.DEBUG)

# This is supposed to hold the player info
CurrentPlayerInfo = perri.get("CurrentPlayerInfo", {})

"""
TODO:



Control the lights

Set up Database

Be able to abruptly stop and resume as if nothing happened
    First clearly define a state space
    rest will come 'EZ'
    
"""

# Functions to open windows to input and edit group info


def save_group_info(player_info={}):  # kannski ad nota {} i stadinn fyrir ()
    print "save_group_info() wants to save:{} but need programming".format(player_info)


def new_group():
    result = gui.askquestion("Start new group?",
                             "Do you want to start a new group?",
                             icon='warning')
    if result == 'yes':
        # make sure everything about the previous group has been saved
        gui.player_info(initialize_room)


def edit_group_info():
    gui.player_info(save_group_info, CurrentPlayerInfo)


# A function to handle resetting the room
def initialize_room(player_info={}):
    """
    This function should set everything up
    That includes resetting any variables
    """
    t = time.time()
    if player_info == {} and \
            gui.askquestion("Reload Previous Group", "Do you want to reload previous group?") == "yes":
        perri.load()
    else:
        perri.reset()
        player_info['room initialization time'] = t

    gui.o = perri.get("gui.o", default=gui.P())
    global progressor
    progressor = perri.get("progressor", Progressor())
    if progressor.progress > 1:
        nextFailButton(gui.FailButtonNames[progressor.progress - 1])
    progressor.plot()

    # TODO: fix states of things if progress was loaded from previous group
    progress = progressor.current_cp()
    if progress == "Nothing":
        pass
    elif progress == "Elevator":
        pass
    elif progress == "TapeRecorder":
        pass
    elif progress == "LockPicking":
        pass
    elif progress == "GreenDude":
        pass
    elif progress == "LieDetectorStart":
        pass
    elif progress == "LieDetectorFinish":
        pass
    elif progress == "WineBox":
        pass
    elif progress == "ShootingRange":
        pass
    elif progress == "Morser":
        pass
    elif progress == "Stealth":
        pass
    elif progress == "TimeBomb":
        pass
    elif progress == "RoomFinished":
        pass

    LockPicking.send("Reset")
    LockPicking.send("SetCorrectPickOrder", [0, 1, 2, 3, 4, 5])

    # TimeBomb.send("Reset")

    Elevator.send("SetActiveDoor", 1)

    Stealth.send("Reset")
    LiePiA.send("Reset")
    LiePiB.send("Reset")
    LieButtons.send("Reset")
    WineBoxHolder.send("Reset")
    ShootingRange.send("Reset")
    TimeBomb.send("Reset")

    SplitFlap.send("Disp", "  Camp Z   ")

    TapeRecorder.send("Reset")
    # taperecorder load 1 and pauses

    failed = display_status_all_devices()

    # give gui time to print all the stuff??
    dt = time.time() - t
    if dt < 10:
        time.sleep(10 - dt)

    for device in failed:
        display_status(device)

    ElevatorDoor.close()
    # gui.notify("Test warning", warning=True)
    # gui.notify("Test solved", solved=True)
    # gui.notify("Test Fail", fail=True)

    def printrssi():
        while True:
            time.sleep(2)
            stuff = "RSSI={}".format(mynetwork.Base.report()[0])
            gui.notify(stuff)

    # t = threading.Thread(target=printrssi)
    # t.setDaemon(True)
    # t.start()
# Some helper functions

def display_status_all_devices():
    ret = []
    for device in Devices:
        state = display_status(device)
        time.sleep(0.1)
        if not state:
            ret.append(device)
    return ret


def nextFailButton(button=None):
    if button not in gui.FailButtonNames:
        print "{} not in {}".format(button, gui.FailButtonNames)
        return
    global currentFailButton
    while True:
        print gui.MissionFailButtons[currentFailButton].config("text")
        b_text = gui.MissionFailButtons[currentFailButton].config("text")[-1]
        gui.MissionFailButtons[currentFailButton].config(state=gui.tk.DISABLED)
        currentFailButton += 1
        print "comparing {} and {}, == {}".format(b_text, button, b_text == button)
        if b_text == button:
            gui.MissionFailButtons[currentFailButton].config(state=gui.tk.NORMAL)
            break
        if currentFailButton > 20:
            break

    # TODO: if the clock isn't running, start the clock according to the mean time for this point


def display_status(device):
    print("display status", device)
    status = moteino_status(device)
    if status[:11] == "No response":
        color = 'red'
        ret = False
    else:
        color = 'green'
        ret = True

    for _i in range(len(gui.DeviceSubmenus)):
        if gui.DeviceMenu.entrycget(_i, 'label') == device:
            gui.DeviceMenu.entryconfig(_i, background=color)
    gui.notify(status)
    return ret


# SplitFlap

def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get(1.0, gui.tk.END).strip().upper()
    print "I want to send this to splitflap: " + stuff2send
    Send2SplitFlapThread(str(stuff2send))
    gui.SplitFlapEntry.delete(0., float(len(stuff2send)))
    gui.notify("'" + stuff2send.replace('\n', ' / ') + "' sent to SplitFlap", fail=True)


# gui.SplitFlapEntry.bind("<Return>", send_to_split_flap)
gui.SplitFlapEntryButton.bind("<Button-1>", send_to_split_flap)


class SplitFlapTimeWarnerBro(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()

        self.DispAt = [m*60 for m in [80, 70, 60, 50, 40, 30, 20, 10, 5, 2]]
        self.FinalCountdownAt = 1*60
        self.StopCountdown = False

    def notify(self):
        m = self.minutes_left()
        if m is None:
            return
        s = " " + str(m) if m < 10 else str(m)
        Send2SplitFlapThread("disp", "{} min left".format(s))


    # TODO: make this better
    def final_countdown(self):
        for s in range(60, 0, -1):
            if self.StopCountdown:
                return
            with Send2SplitFlapLock:
                SplitFlap.send("Disp", str(s).ljust(11))
            time.sleep(1)


    @staticmethod
    def minutes_left():
        seconds = SplitFlapTimeWarnerBro.seconds_left()
        if seconds is None:
            return None
        return max(0, int(seconds / 60))

    @staticmethod
    def seconds_left():
        if gui.o.ClockStartTime is None:
            return None
        return MaxPlayingTime - (time.time() - gui.o.ClockStartTime)

    def run(self):
        while True:
            seconds = self.seconds_left()
            if seconds is None:  # if the clock hasn't started
                time.sleep(60)  # sleep for a minute and check again
                continue

            if seconds < self.DispAt[-1]:
                wait = seconds - self.FinalCountdownAt
                time.sleep(wait)
                self.final_countdown()
            else:
                ts = [seconds - _t for _t in self.DispAt]
                wait = min([_t for _t in ts if _t > 0])
                time.sleep(wait)
                self.notify()








# Elevator


def ElevatorEscaped(fail=False):
    # passcodes are 4132 and 1341

    # Escaping Elevator starts the room.
    # clock starts now and intro message from TapeRecorder
    # should start in a bit

    if progressor.log("Elevator"):

        ElevatorDoor.open()
        run_after(StartTapeRecorderIntroMessage, seconds=20)
        gui.o.ClockStartTime = time.time()
        gui.o.ClockHasStarted = True
        logging.debug("starting clock")
        run_after(ElevatorDoor.close, seconds=15)
        if fail:
            gui.notify("Elevator failed, opened manually", fail=True)
        else:
            gui.notify("Elevator Successfully Escaped", solved=True)
        nextFailButton("Elevator Escape")
        TapeRecorder.send(Command='Load', s="1.ogg" + "\0"*5, FileLength=50)
        TapeRecorder.send("Pause")


def elevator_receive(d):
    if d["Command"] == "SolveDoor1":
        ElevatorEscaped()
    else:
        print "elevator receive: " + str(d)


Elevator.bind(receive=elevator_receive)

# TapeRecorder

TapeRecorderIntroMessageStarted = False
TapeRecorderFiles = [("1.ogg", 50, "Room Intro"),
                     ("2.ogg", 26, "Alternate Intro"),
                     ("3.ogg", 17, "LockPick Hint"),
                     ("4.ogg", 15, "A fine start..."),
                     ("5.ogg", 21, "Rod hint"),
                     ("6.ogg", 37, "Lie Detector Instructions"),
                     ("7.ogg", 38, "WineBox Hint")]


def StartTapeRecorderIntroMessage(timeout=False, fail=False):
    global TapeRecorderIntroMessageStarted
    if not TapeRecorderIntroMessageStarted:
        if progressor.log("TapeRecorder"):
            TapeRecorderIntroMessageStarted = True
            TapeRecorder.send("Play")
            gui.notify("TapeRecorder Intro Message Started")
            run_after(PlayLockPickingHint, seconds=5+50)
            nextFailButton("Start TapeRecorder")


def PlayLockPickingHint(fail=False):
    gui.notify("LockPicking hint started playing")
    TapeRecorder.send(Command='Load', s="3.ogg" + "\0"*5, FileLength=17)


# LockPicking


def LockPickingCompleted(fail=False):
    if progressor.log("LockPicking"):
        if fail:
            gui.notify("LockPicking failed, opened manually", fail=True)
            LockPicking.send("OpenYourself")
        else:
            gui.notify("LockPicking Successfully Completed", solved=True)
        nextFailButton("Open Safe")


def lockpicking_receive(d):
    if d["Command"] == "LockWasPicked":
        LockPickingCompleted()


LockPicking.bind(receive=lockpicking_receive)


# GreenDude


def GreenDudeCompleted(fail=False):
    if progressor.log("GreenDude"):
        gui.notify("GreenDude Correct Passcode entered", fail=fail, solved=not fail)
        TapeRecorder.send(Command='Load', s="5.ogg" + "\0"*5, FileLength=22)
        run_after(BookDrawer.open, seconds=21)
        nextFailButton("GreenDude Fail")


def green_dude_receive(d):
    print "GreenDude Receive"
    if d['Command'] == "CorrectPasscode":
        print "CorrectPassCode"
        GreenDudeCompleted()


GreenDude.bind(receive=green_dude_receive)


# Lie Detector


def LieDetectorActivated(fail=False):
    if progressor.log("LieDetectorStart"):
        gui.notify("Lie Detector Activated", fail=fail, solved=not fail)
        TapeRecorder.send(Command='Load', s="6.ogg" + "\0"*5, FileLength=37)
        LieButtons.send("CorrectLightShow")
        nextFailButton("Start Lie Detector")
        run_after(LieDetectorHandler.start_lie_detector, seconds=5)


class LieDetectorOperationHandler(object):
    def __init__(self, NP):
        self.P = NP
        if NP == 3:
            bla = bool(int(random.random()+0.5))
            self.ScenesAvailable = [True, bla, not bla]
        elif NP == 4:
            self.ScenesAvailable = [False, True, True]
        elif NP == 5:
            self.ScenesAvailable = [True, True, True]

        class Scene(object):
            def __init__(self, Files, Number, Outlength):
                self.Files = Files
                self.N = Number
                self.CurrentFile = None
                self.Done = False
                self.CurrentFileNumber = -1
                self.OutroLength = Outlength

            def reset(self):
                self.CurrentFileNumber = -1
                self.CurrentFile = None

            def next_file(self):
                if self.Done:
                    return
                self.CurrentFileNumber += 1
                self.CurrentFile = self.Files[self.CurrentFileNumber]
                if type(self.CurrentFile) is list:
                    self.CurrentFile = random.choice(self.CurrentFile)
                if self.CurrentFileNumber == len(self.Files) - 1:
                    self.Done = True
                TvPi.send("PlayFile", self.CurrentFile)

            # def replay_file(self):
            #     TvPi.send("PlayFile", self.CurrentFile)

        self.Scenes = [Scene(["B1.mov", "B2.mov", "B3.mov", "B4.mov",
                              ["B5_1.mov", "B5_2.mov", "B5_3.mov"], "B6.mov"], 0, 14),
                       Scene(["PP1.mov", "PP2.mov", "PP3.mov", "PP4.mov",
                              ["PP5_1.mov", "PP5_2.mov", "PP5_3.mov", "PP5_4.mov"], "PP6.mov"], 1, 15),
                       Scene(["GB1.mov", "GB2.mov", "GB3.mov", "GB4.mov",
                              ["GB5_1.mov", "GB5_2.mov", "GB5_3.mov", "GB5_4.mov"], "GB6.mov"], 2, 20)]
        self.CurrentScene = None
        self.Lock = threading.Lock()

    def start_lie_detector(self):
        LieButtons.send("SetListenToButtonPresses")
        LiePiA.send("Start")
        LiePiB.send("Start")
        self.disp_scenes_available()

    def disp_scenes_available(self):
        bla = self.ScenesAvailable
        LieButtons.send("Disp", Lights=[int(not bla[0]), int(not bla[1]), int(not bla[2]), 1, 1, 1, 1])
        if not any(self.ScenesAvailable):
            LieDetectorCompleted()

    def disp_only(self, n):
        bla = [1, 1, 1, 1, 1, 1, 1]
        bla[n] = 0
        LieButtons.send("Disp", Lights=bla)

    def handle(self, incoming):
        if self.Lock.locked():
            return
        with self.Lock:
            print incoming
            if incoming["SenderName"] == "Lie2Buttons":
                if StealthActive:
                    StealthRetry()

                elif incoming["Command"] == "Button1Press":
                    # Players pass the question
                    if self.CurrentScene is None:
                        return
                    prev_file = str(self.CurrentScene.CurrentFile)
                    self.CurrentScene.next_file()
                    gui.notify("Scene({}) file('{}') passed, now playing '{}'"
                               "".format(self.CurrentScene.N + 1,
                                         prev_file,
                                         self.CurrentScene.CurrentFile), solved=True)
                    if self.CurrentScene.Done:

                        time.sleep(5)
                        Send2SplitFlapThread("Act {} Done".format(self.CurrentScene.N),
                                             self.CurrentScene.OutroLength - 5)
                        LieButtons.send("CorrectLightShow")
                        time.sleep(self.CurrentScene.OutroLength - 5)

                        self.ScenesAvailable[self.CurrentScene.N] = False
                        self.CurrentScene = None
                        self.disp_scenes_available()

                elif incoming["Command"] == "Button2Press":
                    # Players fail the Scene, Go back to Scene selection
                    if self.CurrentScene is None:
                        return

                    gui.notify("Scene({}) file('{}') failed, resetting..."
                               "".format(self.CurrentScene.N + 1,
                                         self.CurrentScene.CurrentFile), fail=True)
                    self.CurrentScene.reset()
                    self.CurrentScene = None

                    TvPi.send("Reset")
                    Send2SplitFlapThread("Try again", 10)
                    LieButtons.send("IncorrectLightShow")

                    run_after(self.disp_scenes_available, seconds=3)

            elif incoming["SenderName"] == "LieButtons":
                if incoming["Command"] == "CorrectPassCode":
                    LieDetectorActivated()
                elif incoming["Command"] == "ButtonPress":
                    if incoming["Button"] in [0, 1, 2]:
                        if self.CurrentScene is None:
                            if self.ScenesAvailable[incoming["Button"]]:
                                self.CurrentScene = self.Scenes[incoming["Button"]]
                                self.CurrentScene.next_file()
                                gui.notify("Player selected Scene({})".format(self.CurrentScene.N + 1))
                                self.disp_only(incoming["Button"])


LieDetectorHandler = LieDetectorOperationHandler(NofPlayers)
LieButtons.bind(receive=LieDetectorHandler.handle)
Lie2Buttons.bind(receive=LieDetectorHandler.handle)


LieDetectorHasBeenActivated = False
LieDetectorVideos = ["B1.mov", "B2.mov", "B3.mov"]

TvPiFiles = ["B1.mov",
             "B2.mov",
             "B3.mov",
             "PP1.mov",
             "PP2.mov",
             "PP3.mov",
             "SOS.mov"]


def LieDetectorCompleted(fail=False):
    if progressor.log("LieDetectorFinish"):
        gui.notify("Lie Detector Completed", fail=fail, solved=not fail)
        Send2SplitFlapThread("Well Done!", 10)
        time.sleep(5)
        TapeRecorder.send(Command='Load', s="7.ogg" + "\0"*5, FileLength=38)
        nextFailButton("Lie Detector Fail")
        LiePiA.send("Reset")
        LiePiB.send("Reset")
        run_after(OpenWineBoxHolder, seconds=12)


def liebuttons_receive(d):
    if d['Command'] == "CorrectPassCode":
        LieDetectorActivated()


# LieButtons.bind(receive=liebuttons_receive)


def lie_2_buttons_receive(d):
    print "lie_2_buttons_receive reacting to : " + str(d)
    if progressor.current_cp() == "LieDetector":
        if d['Command'] == "Button1Press":
            # PLay last video again
            if LieDetectorVideoPosition >= 0:
                TvPi.send("PlayFile", LieDetectorVideos[LieDetectorVideoPosition])
        elif d['Command'] == "Button2Press":
            global LieDetectorVideoPosition
            LieDetectorVideoPosition += 1
            if LieDetectorVideoPosition >= len(LieDetectorVideos):
                LieDetectorCompleted(fail=False)
            else:
                TvPi.send("PlayFile", LieDetectorVideos[LieDetectorVideoPosition])
    else:
        print "Progressor doesn't want to do stuff for lie_2_buttons_receive, " \
              "current progress was: {}".format(progressor.current_cp())


# Lie2Buttons.bind(receive=lie_2_buttons_receive)


# WineBox

def OpenWineBoxHolder():
    WineBoxHolder.send("Open")


def WineBoxCompleted(fail=False):
    if progressor.log("WineBox"):
        if fail:
            WineBox.send("Open")
        gui.notify("Wine Box opened", fail=fail, solved=not fail)
        nextFailButton("Open WineBox")


def winebox_receive(d):
    if d['Command'] == "IWasSolved":
        WineBoxCompleted()


WineBox.bind(receive=winebox_receive)

# Shooting Range


def ShootingRangeCompleted(fail=False):
    if progressor.log("ShootingRange"):
        gui.notify("Shooting Range Completed", fail=fail, solved=not fail)
        TvPi.send("PlayFile", s="SOS.mov")
        nextFailButton("Shooting Range Fail")


def shooting_range_receive(d):
    if d['Command'] == "TargetHit":
        gui.ShootingCirclesSetColor(d['Target'], 'green')
    elif d['Command'] == "WrongTarget":
        for _i in range(5):
            gui.ShootingCirclesSetColor(_i, 'red')
    elif d['Command'] == "MissionComplete" or d['Command'] == "PuzzleFinished":
        ShootingRangeCompleted()


ShootingRange.bind(receive=shooting_range_receive)


# Morser

MorseSequence = [63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0, 63, 0, 2, 0,
                 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0]


def MorseCompleted(fail=False):
    if progressor.log("Morser"):
        gui.notify("Morse Completed", fail=fail, solved=not fail)
        nextFailButton("Morse Fail")
        # TvPi.send("")
        StealthDoor.open()
        StealthStart()


def morse_receive(d):
    if d['Command'] == "CorrectPasscode":
        MorseCompleted()


Morser.bind(receive=morse_receive)


# Stealth
StealthActive = False


def StealthStart():
    Stealth.send("SetSequence", Sequence=MorseSequence)
    global StealthActive
    StealthActive = True


def StealthRetry():
    Stealth.send("SetSequence", Sequence=MorseSequence)
    Sirens.send("SetPin2Low")
    gui.notify("Stealth has been reset")


def StealthTripped(lasernr):
    Sirens.send("SetPin2High")
    gui.notify("Stealth tripped on laser {}".format(lasernr))


def StealthCompleted(fail=False):
    gui.notify("Stealth Completed", fail=fail, solved=not fail)
    nextFailButton("Stealth Fail")


def stealth_receive(d):
    if d['Command'] == 'Triggered':
        StealthTripped(d["Tripped"])


Stealth.bind(receive=stealth_receive)


# TimeBomb

def BombActivated():
    if gui.o.ClockStartTime is None:
        RoomTimeLeft = 10*60  # 10 minutes
    else:
        RoomTimeLeft = MaxPlayingTime - (time.time() - gui.o.ClockStartTime)
    TimeLeft = max(min(MaxBombTime, RoomTimeLeft), MinBombTime)  # max 10 minute, min 1 minute
    gui.notify("Bomb Activated, Time to solve: {}:{}"
               "".format(int(TimeLeft/60), int(TimeLeft) % 60), solved=True)
    TimeBomb.send("SetExplosionTime", Time=TimeLeft*1000)


def BombDiffused():
    gui.notify("Bomb Diffused ", solved=True)
    gui.notify("Room Completed!!!", solved=True)
    FinalExitDoor.open()


def BombExploded():
    gui.notify("Bomb Exploded!", fail=True)
    FinalExitDoor.open()


def timebomb_receive(d):
    if d:
        if d['Command'] == "BombActivated":
            BombActivated()
        elif d["Command"] == "BombDiffused":
            BombDiffused()
        elif d["Command"] == "BombExploded":
            BombExploded()


TimeBomb.bind(receive=timebomb_receive)


# Stealth Debugging:
class Stealth2SplitThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ActiveEvent = threading.Event()
        self.setDaemon(True)
        self.start()

    def activate(self):
        self.ActiveEvent.set()

    def run(self):
        while True:
            if self.ActiveEvent.is_set():
                d = Stealth.send_and_receive("Status")
                if d:
                    SplitFlap.send("Disp", str(d['Tripped']))
            time.sleep(5)

    def deactivate(self):
        self.ActiveEvent.clear()


stealth2split = Stealth2SplitThread()


# Gui functionality

def update_door_button_colors(recall=True):
    for j in range(len(gui.DoorNameList)):
        if Doors[j].is_open():
            gui.DoorButtons[j].configure(bg='green')
        else:
            gui.DoorButtons[j].configure(bg='red')
    if recall:
        gui.top.after(500, update_door_button_colors)


def door_button_callback(event=None):
    button = event.widget
    doorname = button.config("text")[-1]
    door = Doors[gui.DoorNameList.index(doorname)]
    if door.is_open():
        door.close()
        gui.notify("Closing " + doorname)
    else:
        door.open()
        gui.notify("Opening " + doorname)
    update_door_button_colors(recall=False)


for b in gui.DoorButtons:
    b.bind("<Button-1>", door_button_callback)

update_door_button_colors(recall=True)


def tape_recorder_buttons_callback(event=None):
    button = event.widget
    b_text = button.config("text")[-1]
    gui.notify("Tape Recorder: Host pressed " + b_text)
    TapeRecorder.send(b_text)


gui.TapeRecorderPlayButton.bind("<Button-1>", tape_recorder_buttons_callback)
gui.TapeRecorderPauseButton.bind("<Button-1>", tape_recorder_buttons_callback)


def mission_fail_callback(event=None):
    button = event.widget
    if button.config("state")[-1] == "disabled":
        return
    b_text = button.config("text")[-1]
    if b_text == "Elevator Escape":
        result = gui.askquestion("Elevator", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            ElevatorEscaped(fail=True)
    elif b_text == "Start TapeRecorder":
        result = gui.askquestion("TapeRecorder", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            StartTapeRecorderIntroMessage(fail=True)
    elif b_text == "Open Safe":
        result = gui.askquestion("OpenSafe", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            LockPickingCompleted(fail=True)
    elif b_text == "GreenDude Fail":
        result = gui.askquestion("GreenDude", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            GreenDudeCompleted(fail=True)
    elif b_text == "Start Lie Detector":
        result = gui.askquestion("Start Lie Detector", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            LieDetectorActivated(fail=True)
    elif b_text == "Lie Detector Fail":
        result = gui.askquestion("Lie Detector Fail", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            LieDetectorCompleted(fail=True)
    elif b_text == "Open WineBox":
        result = gui.askquestion("Lie Detector", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            WineBoxCompleted(fail=True)
    elif b_text == "Shooting Range Fail":
        result = gui.askquestion("Shooting Range", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            ShootingRangeCompleted(fail=True)
    elif b_text == "Morse Fail":
        result = gui.askquestion("Morse", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            MorseCompleted(fail=True)
    elif b_text == "Stealth Fail":
        gui.notify("Stealth Fail --- Dont know what you want me to do here")
    elif b_text == "TimeBomb Fail":
        gui.notify("TimeBomb Fail --- Dont know what you want me to do here")
    else:
        print "Don't know what happened but b_text was: " + b_text


for b in gui.MissionFailButtons:
    b.bind("<Button-1>", mission_fail_callback)

currentFailButton = 0
for DeviceSubmenu, Device in zip(gui.DeviceSubmenus, Devices):
    DeviceSubmenu.add_command(label="Get Status for {}".format(Device),
                              command=lambda device=Device: display_status(device))
    DeviceSubmenu.add_command(label="Send Reset command",
                              command=lambda device=Device: mynetwork.send(device, "Reset"))

    if Device[:-1] == "LiePi":
        DeviceSubmenu.add_command(label="Start",
                                  command=lambda device=Device: mynetwork.send(device, "Start"))
        DeviceSubmenu.add_command(label="Stop",
                                  command=lambda device=Device: mynetwork.send(device, "Reset"))
    if Device == "Stealth":
        DeviceSubmenu.add_command(label="Start Stealth2Split",
                                  command=lambda: stealth2split.activate())
        DeviceSubmenu.add_command(label="Stop Stealth2Split",
                                  command=lambda: stealth2split.deactivate())
        DeviceSubmenu.add_command(label="Send LightShow",
                                  command=lambda: Stealth.send("SetSequence", Sequence=MorseSequence))
        subsubmenu = gui.tk.Menu(DeviceSubmenu, tearoff=False)
        DeviceSubmenu.add_cascade(label="Set Tempo", menu=subsubmenu)
        for t in [200, 300, 400, 500, 600, 700, 800]:
            subsubmenu.add_command(label=str(t),
                                   command=lambda _t=t: Stealth.send("SetTempo", Tempo=_t))
    if Device == "Sirens":
        DeviceSubmenu.add_command(label="Turn on",
                                  command=lambda: Sirens.send("SetPin2High"))
        DeviceSubmenu.add_command(label="Turn off",
                                  command=lambda: Sirens.send("SetPin2Low"))

    if Device == "TapeRecorder":
        subsubmenu = gui.tk.Menu(DeviceSubmenu, tearoff=False)
        DeviceSubmenu.add_cascade(label="Play file", menu=subsubmenu)
        for i in range(len(TapeRecorderFiles)):
            subsubmenu.add_command(label=TapeRecorderFiles[i][2],
                                   command=lambda _i=i: TapeRecorder.send("Load",
                                                                          s=TapeRecorderFiles[_i][0] + "\0"*5,
                                                                          FileLength=TapeRecorderFiles[_i][1]))
        DeviceSubmenu.add_command(label="Set Zero Position",
                                  command=lambda: TapeRecorder.send("SetCurrentPosAsZero"))
        DeviceSubmenu.add_command(label="Engage Stupid State",
                                  command=lambda: TapeRecorder.send("SetStupidState"))
    if Device == "LieButtons":
        DeviceSubmenu.add_command(label="SetListenToPasscode",
                                  command=lambda: LieButtons.send("SetListenToPasscode"))
        DeviceSubmenu.add_command(label="SetListenToButtonPresses",
                                  command=lambda: LieButtons.send("SetListenToButtonPresses"))
        DeviceSubmenu.add_command(label="Correct LightShow",
                                  command=lambda: LieButtons.send("CorrectLightShow"))
        DeviceSubmenu.add_command(label="Incorrect LightShow",
                                  command=lambda: LieButtons.send("IncorrectLightShow"))

    if Device == "TvPi":
        subsubmenu = gui.tk.Menu(DeviceSubmenu, tearoff=False)
        DeviceSubmenu.add_cascade(label="Play file", menu=subsubmenu)
        for f in TvPiFiles:
            subsubmenu.add_command(label=f,
                                   command=lambda _f=f: TvPi.send("PlayFile", s=_f))

    if Device == "WineBox":
        DeviceSubmenu.add_command(label="Open",
                                  command=lambda: WineBox.send("Open"))


gui.ActionMenu.add_command(label="Check All Device Status", command=display_status_all_devices)
# gui.ActionMenu.add_command(label="Reset Room")
gui.ActionMenu.add_command(label="New Group", command=new_group)
gui.ActionMenu.add_command(label="Edit Group info", command=edit_group_info)


if __name__ == "__main__":
    run_after(initialize_room, seconds=1)
    try:
        gui.top.mainloop()
    except KeyboardInterrupt:
        pass
    print "Dropped out of mainloop"
    perri.save()
    exit()

