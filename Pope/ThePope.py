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

WinBoxHOlder tharf ekki ad opnast i byrjun

gera thannig ad haegt se ad breyta timanum on the fly




Set up Database

Be able to abruptly stop and resume as if nothing happened
    First clearly define a state space
    rest will come 'EZ'
    
"""

# Functions to open windows to input and edit group info


def save_group_info(player_info={}):  # kannski ad nota {} i stadinn fyrir ()
    print "save_group_info() wants to save:{} but need programming".format(player_info)
    global NofPlayers
    NofPlayers = player_info['NofPlayers']


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


    # TimeBomb.send("Reset")

    Elevator.send("SetActiveDoor", 1)

    LockPicking.send("Reset")
    Stealth.send("Reset")
    LiePiA.send("Reset")
    LiePiB.send("Reset")
    LieButtons.send("Reset")
    WineBoxHolder.send("Reset")
    ShootingRange.send("Reset")
    TimeBomb.send("Reset")
    TapeRecorder.send("Reset")

    GreenDude.send("SetPasscode", PassCode=GreenDudeCorrectPassCode)
    LockPicking.send("SetCorrectPickOrder", LockPickCorrectPickOrder)
    gui.notify("Sending pickorder:{}".format(LockPickCorrectPickOrder) )


    # taperecorder load 1 and pauses

    failed = display_status_all_devices()

    # give gui time to print all the stuff??
    dt = time.time() - t
    if dt < 10:
        time.sleep(10 - dt)

    for device in failed:
        display_status(device)

    ElevatorDoor.close()
    Send2SplitFlapThread("  Camp Z   ", time_between=None)
    # ShootingRange.send("DispColors", Colors=[0]*5)
    CalibrateStealth()

    gui.notify("Initialization complete")

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


def critical_send(towhom, *args, **kwargs):
    n = kwargs["n"] if "n" in kwargs else 10
    for _ in range(n):
        if towhom.send(*args, **kwargs):
            return True
        time.sleep(0.3)
    return False


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

        self.DispAt = [m*60 for m in [80, 70, 60, 50, 40, 30, 20, 10, 5, 4, 3, 2, 1]]
        self.FinalCountdownAt = 10  # seconds
        self.StopCountdown = False

        self.start()

    def notify(self):
        m = self.minutes_left()
        if m is None:
            return
        s = " " + str(m) if m < 10 else str(m)
        Send2SplitFlapThread("{} min left".format(s))


    # TODO: make this better
    def final_countdown(self):
        for s in range(self.FinalCountdownAt):
            if self.StopCountdown:
                return
            with Send2SplitFlapLock:
                    SplitFlap.send("Disp", "9876543210  "[:(s+1)].ljust(11))
            time.sleep(1)


    @staticmethod
    def minutes_left():
        seconds = SplitFlapTimeWarnerBro.seconds_left()
        if seconds is None:
            return None
        return max(0, int(round(seconds / 60.)))

    @staticmethod
    def seconds_left():
        if gui.o.ClockStartTime is None:
            return None
        return MaxPlayingTime - (time.time() - gui.o.ClockStartTime)

    def not_now(self):
        self.wait = True

    def ok_now(self):
        self.wait = False

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
                return
            else:
                ts = [seconds - _t for _t in self.DispAt]
                wait = min([_t for _t in ts if _t > 0])
                time.sleep(wait)
                self.notify()


splitflaptimer = SplitFlapTimeWarnerBro()


class ScoreKeeping(object):
    Skills = ["Thievery",
              "Resourcefulness",
              "Deception",
              "Weapon Proficiency",
              "Stealth",
              "working under pressure"]
    PassingScores = { "Thievery": 15,
                      "Resourcefulness": 15,
                      "Deception": 20,
                      "Weapon Proficiency": 15,
                      "Stealth": 10,
                      "working under pressure": 25}
    DeductionCosts = {"Thievery": 5,
                      "Resourcefulness": 5,
                      "Deception": 3,
                      "Weapon Proficiency": 2,
                      "Stealth": 3,
                      "working under pressure": 10}

    def __init__(self):
        self.Scores = {"Thievery": 0,
                      "Resourcefulness": 0,
                      "Deception": 0,
                      "Weapon Proficiency": 0,
                      "Stealth": 0,
                      "working under pressure": 0}
        self.Deductions = {   "Thievery": 0,
                              "Resourcefulness": 0,
                              "Deception": 0,
                              "Weapon Proficiency": 0,
                              "Stealth": 0,
                              "working under pressure": 0}

    def register(self, skill, fail_or_pass, n_deductions):
        self.Scores[skill] = int(fail_or_pass) * self.PassingScores[skill]
        self.Deductions[skill] = n_deductions*self.DeductionCosts[skill]

    def calc_scores(self, timeleft):
        score = 0
        deductions = 0
        for skill in self.Skills:
            score += self.Scores[skill]
            deductions += self.Deductions[skill]
        return score - deductions + timeleft/60


# Elevator


def ElevatorEscaped(fail=False):
    # passcodes are 4132 and 1341

    # Escaping Elevator starts the room.
    # clock starts now and intro message from TapeRecorder
    # should start in a bit

    if progressor.log("Elevator"):

        ElevatorDoor.open()
        # run_after(StartTapeRecorderIntroMessage, seconds=20)
        gui.o.ClockStartTime = time.time()
        gui.o.ClockHasStarted = True
        logging.debug("starting clock")
        run_after(ElevatorDoor.close, seconds=15)
        if fail:
            gui.notify("Elevator failed, opened manually", fail=True)
        else:
            gui.notify("Elevator Successfully Escaped", solved=True)
        nextFailButton("Elevator Escape")
        TapeRecorder_play("Room Intro")
        TapeRecorder.send("Pause")


def elevator_receive(d):
    if d["Command"] == "SolveDoor1":
        ElevatorEscaped()
    else:
        print "elevator receive: " + str(d)


Elevator.bind(receive=elevator_receive)

# TapeRecorder

TapeRecorderIntroMessageStarted = False
TapeRecorderFiles = [("1b.ogg", 58, "Room Intro", 2),
                     ("2.ogg", 24, "Rod Hint", 4.2),
                     ("3.ogg", 24, "Lie Detector Instructions", 3.7),
                     ("4.ogg", 35, "WineBox Hint", 4.1),
                     ("5.ogg", 30, "Successfully Completed", 3.2),
                     ("6.ogg", 30, "Bomb Go Boom!", 1.4),
                     ("8.ogg", 31, "Time Ran Out", 2.3),
                     ("a.ogg", 17, "Shooting Range Instructions", 2.3),
                     ("b.ogg", 6, "Colored Circles", 0),
                     ("c.ogg", 18, "Stealth Rules", 0)]


def TapeRecorder_play(filehandle):
    index = [t[2] for t in TapeRecorderFiles].index(filehandle)
    f = TapeRecorderFiles[index][0]
    TapeRecorder.send(Command='Load', s=f + "\0"*(10 - len(f)), FileLength=TapeRecorderFiles[index][1],
                                                                StartPos=int(TapeRecorderFiles[index][3]*10))


def StartTapeRecorderIntroMessage(timeout=False, fail=False):
    global TapeRecorderIntroMessageStarted
    if not TapeRecorderIntroMessageStarted:
        if progressor.current_cp() == "Elevator":
            TapeRecorderIntroMessageStarted = True
            TapeRecorder.send("Play")
            gui.notify("TapeRecorder Intro Message Started")
            # run_after(PlayLockPickingHint, seconds=5+50)
            nextFailButton("Start TapeRecorder")


# def PlayLockPickingHint(fail=False):
#     gui.notify("LockPicking hint started playing")
#     TapeRecorder.send(Command='Load', s="3.ogg" + "\0"*5, FileLength=17)


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
        TapeRecorder_play("Rod Hint")
        # run_after(BookDrawer.open, seconds=12)
        nextFailButton("GreenDude Fail")


def green_dude_receive(d):
    print "GreenDude Receive"
    if d['Command'] == "CorrectPasscode":
        print "CorrectPassCode"
        GreenDudeCompleted()


GreenDude.bind(receive=green_dude_receive)


class GreenDudeUpdaterClass(threading.Thread):
    TimeBetween = 3

    def __init__(self):
        threading.Thread.__init__(self)
        self.last_update_time = time.time()
        self.UpdateEvent = threading.Event()
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:  # daemonic so it's cool
            self.UpdateEvent.wait()
            self.UpdateEvent.clear()
            self._update()

    def update(self, event=None):
        if time.time() - self.last_update_time > self.TimeBetween:
            self.UpdateEvent.set()

    def _update(self):
        d = GreenDude.send_and_receive("Status")
        # print d
        if d:
            gui.GreenDudeSetColors(d["Lights"])


GreenDudeUpdater = GreenDudeUpdaterClass()
gui.GreenDudeCanvas.bind("<Button-1>", GreenDudeUpdater.update)


# Lie Detector


def LieDetectorActivated(fail=False):
    if progressor.log("LieDetectorStart"):
        global StealthActive
        StealthActive = False
        LieDetectorHandler.setnofplayers(NofPlayers)
        gui.notify("Lie Detector Activated", fail=fail, solved=not fail)
        TapeRecorder_play("Lie Detector Instructions")
        run_after(BookDrawer.open, seconds=8.3,)
        LieButtons.send("CorrectLightShow")
        nextFailButton("Start Lie Detector")
        run_after(LieDetectorHandler.start_lie_detector, seconds=5)


class LieDetectorOperationHandler(object):
    def __init__(self):
        self.P = None
        self.setnofplayers(random.randint(3, 5))


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
                       Scene(["GB1_SJ.mov", "GB3_J.mov",
                              ["GB5_1.mov", "GB5_2.mov", "GB5_3.mov"], "GB6.mov"], 2, 20)]
                       # Scene(["GB1.mov", "GB2.mov", "GB3.mov", "GB4.mov",
                       #        ["GB5_1.mov", "GB5_2.mov", "GB5_3.mov", "GB5_4.mov"], "GB6.mov"], 2, 20)]
        self.CurrentScene = None
        self.Lock = threading.Lock()

    def setnofplayers(self, NP):
        self.P = NP
        if NP == 3:
            bla = bool(int(random.random()+0.5))
            self.ScenesAvailable = [bla, not bla, True]
        elif NP == 4:
            self.ScenesAvailable = [True, True, False]
        elif NP == 5:
            self.ScenesAvailable = [True, True, True]

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
                    StealthButton(incoming["Command"])

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
                        Send2SplitFlapThread("Mission {}\n Completed".format(self.CurrentScene.N + 1))#, (self.CurrentScene.OutroLength - 5 )/2)
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


LieDetectorHandler = LieDetectorOperationHandler()
LieButtons.bind(receive=LieDetectorHandler.handle)
Lie2Buttons.bind(receive=LieDetectorHandler.handle)


LieDetectorHasBeenActivated = False


def LieDetectorCompleted(fail=False):
    if progressor.log("LieDetectorFinish"):
        gui.notify("Lie Detector Completed", fail=fail, solved=not fail)
        Send2SplitFlapThread("Well Done!", 10)
        time.sleep(5)
        TapeRecorder_play("WineBox Hint")
        nextFailButton("Lie Detector Fail")
        LiePiA.send("Reset")
        LiePiB.send("Reset")
        run_after(OpenWineBoxHolder, seconds=3.5)


# WineBox

def OpenWineBoxHolder():
    WineBoxHolder.send("Open")


def WineBoxCompleted(fail=False):
    if progressor.log("WineBox"):
        if fail:
            WineBox.send("Open")
        gui.notify("Wine Box opened", fail=fail, solved=not fail)
        nextFailButton("Open WineBox")
        ShootingRangeGame.start()


def winebox_receive(d):
    if d['Command'] == "IWasSolved":
        WineBoxCompleted()


WineBox.bind(receive=winebox_receive)

# Shooting Range


def ShootingRangeCompleted(fail=False):
    if progressor.log("ShootingRange"):
        gui.notify("Shooting Range Completed", fail=fail, solved=not fail)
        if fail:
            ShootingRangeGame.game_over(lose=True)
        TvPi.send("PlayFile", s="SOS.mov")
        nextFailButton("Shooting Range Fail")
        CalibrateStealth()


def get_shootingrange_sequence(length):
    ret = [random.randint(1, 4)]
    while len(ret) < length:
        r = random.randint(0, 4)
        if ret[-1] != r:
            if len(ret) == 0 and r != 0:
                continue
            ret.append(r)
    return ret


class ShootingRangeGameClass(object):
    SequenceLength = 7
    TargetNames = "zpcma"

    def __init__(self):
        self.TargetSequence = get_shootingrange_sequence(self.SequenceLength)
        self.hitnr = 0
        self.GameOver = False

    def start(self):
        self.send_next_target_to_shootingrange()
        self.send_next_target_to_splitflap()
        splitflaptimer.not_now()

    def send_next_target_to_shootingrange(self):
        ShootingRange.send("NewSequence", Sequence=[self.TargetSequence[self.hitnr]]*5)

    def send_next_target_to_splitflap(self):
        Send2SplitFlapThread("{}/{}  next:{}".format(self.hitnr,
                                                     self.SequenceLength,
                                                     self.TargetNames[self.TargetSequence[self.hitnr]]),
                             time_between=None)

    def target_hit(self):
        target = self.TargetNames[self.TargetSequence[self.hitnr]]
        self.hitnr += 1
        if self.hitnr >= self.SequenceLength:
            self.game_over(win=True)
            return
        gui.notify("Target {} was hit!, next target: {}"
                   "".format(target, self.TargetNames[self.TargetSequence[self.hitnr]])
                   ,solved=True)
        time.sleep(1)
        ShootingRange.send("DispColors", Colors=[2]*5)
        time.sleep(0.5)
        ShootingRange.send("Reset")
        self.send_next_target_to_splitflap()
        time.sleep(0.3)
        self.send_next_target_to_shootingrange()

    def game_over(self, win=False, lose=False):
        self.GameOver = True
        splitflaptimer.ok_now()
        if win:
            ShootingRangeCompleted()
            Send2SplitFlapThread("Well Done!", time_between=10)

        if lose:
            Send2SplitFlapThread("Mission \n Failed")


    def receive(self, d):
        if self.GameOver:
            return
        if d['Command'] == "TargetHit":
            if d['Target'] == self.TargetSequence[self.hitnr]:
                self.target_hit()
                # gui.ShootingCirclesSetColor(d['Target'], 'green')
        elif d['Command'] == "WrongTarget":
            # Send2SplitFlapThread("not {},  {}!".format(d['Target'], self.TargetSequence[self.hitnr]))
            # time.sleep(6)
            # self.send_next_target_to_splitflap()
            # gui.notify("Wrong Target, {} was hit, target is {}".format(d['Target'],
            #                                                            self.TargetSequence[self.hitnr]))
            pass
        elif d['Command'] == "MissionComplete" or d['Command'] == "PuzzleFinished":
            time.sleep(3)
            ShootingRange.send("Reset")


ShootingRangeGame = ShootingRangeGameClass()
ShootingRange.bind(receive=ShootingRangeGame.receive)


# Morser

MorseSequence = [63, 38, 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38, 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38,
                        25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38, 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38]


def MorseCompleted(fail=False):
    if progressor.log("Morser"):
        gui.notify("Morse Completed", fail=fail, solved=not fail)
        nextFailButton("Morse Fail")
        # TvPi.send("")
        StealthDoor.open()
        StealthStart()
        TapeRecorder_play("Stealth Rules")


def morse_receive(d):
    if d['Command'] == "CorrectPasscode":
        MorseCompleted()


Morser.bind(receive=morse_receive)


# Stealth
StealthActive = True


def run_CalibrateStealth():
    t = threading.Thread(target=CalibrateStealth)
    t.setDaemon(True)
    t.start()


def CalibrateStealth():
    # if StealthActive:
    #     if not gui.askquestion("Stealth Active", "Stealth is active do you still want to calibrate?"):
    #         gui.notify("CalibrateStealth() problem: Stealth is Active, can't calibrate", warning=True)
    #         return

    d = Stealth.send_and_receive("GetPhotovalues", max_wait=4000)
    if not d:
        gui.notify("CalibrateStealth() problem: Didn't get photovalues from Stealth, aborting calibration")
        return

    pvs = d["Sequence"][:6]
    devs = d["Sequence"][10:16]
    maxs = d["Sequence"][20:26]

    thresholds = [min(255, maxs[i] + devs[i] + 20) for i in range(6)]

    s = "CalibrateStealth(): Thresholds calibrated to: {}".format(thresholds)

    gui.notify(s)

    Stealth.send("SetThresholds", Sequence=thresholds)


def StealthStart():
    Stealth.send("SetSequence", Sequence=MorseSequence)
    global StealthActive
    StealthActive = True


def StealthButton(press):
    if press == "Button1Press":
        Stealth.send("SetSequence", Sequence=MorseSequence)
        Sirens.send("SetPin2Low")
        gui.notify("Stealth has been reset")
    elif press == "Button2Press":
        Sirens.send("SetPin2High")


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
    gui.notify( "Bomb Activated, Time to solve: {}:{}"
               "".format(int(TimeLeft/60), int(TimeLeft) % 60), solved=True)
    TimeBomb.send("SetExplosionTime", Time=int(TimeLeft*1000))
    seconds = int(TimeLeft) % 60
    seconds = "0" + str(seconds) if len(str(seconds)) == 1 else str(seconds)

    Send2SplitFlapThread("Time left\n {}:{}".format(int(TimeLeft/60), seconds))


def BombDiffused():
    gui.notify("Bomb Diffused ", solved=True)
    gui.notify("Room Completed!!!", solved=True)
    TapeRecorder_play("Successfully Completed")
    FinalExitDoor.open()


def BombExploded():
    gui.notify("Bomb Exploded!", fail=True)
    run_after(BombGoBoom, seconds=20)
    FinalExitDoor.open()


def BombGoBoom():
    TapeRecorder_play("Bomb Go Boom")


def TimeRunsOut():
    gui.notify("Time's Up! They have lost. MuHAHAH!", fail=True)
    TapeRecorder_play("Time Ran Out")


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
        DeviceSubmenu.add_command(label="Send LightShow",
                                  command=lambda: Stealth.send("SetSequence", Sequence=MorseSequence))
        DeviceSubmenu.add_command(label="Calibrate Thresholds",
                                  command=run_CalibrateStealth)
        subsubmenu = gui.tk.Menu(DeviceSubmenu, tearoff=False)
        DeviceSubmenu.add_cascade(label="Set Tempo", menu=subsubmenu)
        for i in range(10):
            t = 1000 + i*250
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
        for i, scene in enumerate(LieDetectorHandler.Scenes):
            subsubmenu = gui.tk.Menu(DeviceSubmenu, tearoff=False)
            DeviceSubmenu.add_cascade(label="Scene {}".format(i+1), menu=subsubmenu)
            fs = []
            # print scene.Files
            for f in scene.Files:
                if type(f) is str:
                    # print "found string"
                    fs.append(f)
                elif type(f) is list:
                    # print "found list"
                    for ff in f:
                        if type(ff) is str:
                            # print "found string in list"
                            fs.append(ff)
            for f in fs:
                subsubmenu.add_command(label=f,
                                       command=lambda _f=f: TvPi.send("PlayFile", s=_f))
            subsubmenu.add_command(label="SOS.mov",
                                   command=lambda _f="SOS.mov": TvPi.send("PlayFile", s=_f))

    if Device == "WineBox":
        DeviceSubmenu.add_command(label="Open",
                                  command=lambda: WineBox.send("Open"))

    if Device == "ShootingRange":
        DeviceSubmenu.add_command(label="Register Hit",
                                  command=ShootingRangeGame.target_hit)


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

