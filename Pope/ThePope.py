import sys
from datetime import datetime
outputfile = open(datetime.now().strftime("/home/pope/LogFiles/ThePopeLog__%Y_%d_%m__%H_%M"), 'w+')
# sys.stdout = outputfile
# sys.stderr = outputfile


from Setup import *
from apscheduler.schedulers.background import BackgroundScheduler
import time
# Initialize Scheduler

scheduler = BackgroundScheduler()
scheduler.start()


# A nice little quick hand function to run something at a later time using the Scheduler.
def run_after(func, seconds=0., minutes=0.):
    scheduler.add_job(func,
                      'date',
                      run_date=datetime.fromtimestamp(time.time() + seconds + 60*minutes))


# Configurate logging module
logging.basicConfig(level=logging.DEBUG)

# This is supposed to hold the player info
CurrentPlayerInfo = perri.get("CurrentPlayerInfo", {})

"""
TODO:

WinBoxHolder tharf ekki ad opnast i byrjun

gera thannig ad haegt se ad breyta timanum on the fly

"""

# Functions to open windows to input and edit group info
0

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
        reload_group = True
    else:
        perri.reset()
        player_info['room initialization time'] = t
        reload_group = False

    gui.globals = perri.get("gui.globals", default=gui.GlobalValues())
    global progressor
    progressor = perri.get("progressor", Progressor())
    if progressor.progress > 1:
        nextFailButton(gui.FailButtonNames[progressor.progress - 1])
    progressor.plot()

    # global LieDetectorHandler
    global LieDetectorHandler
    LieDetectorHandler = perri.get("LieDetectorHandler", default=LieDetectorOperationHandler())
    LieButtons.bind(receive=LieDetectorHandler.handle)
    Lie2Buttons.bind(receive=LieDetectorHandler.handle)

    global ShootingRangeGame
    print "%%%%%%%%%%%%%%%%%%  " + str(ShootingRangeGame.hitnr)
    ShootingRangeGame = perri.get("ShootingRangeGame", default=ShootingRangeGameClass())
    ShootingRange.bind(receive=ShootingRangeGame.receive)
    print "%%%%%%%%%%%%%%%%%%  " + str(ShootingRangeGame.hitnr)

    if reload_group:
        for message in gui.globals.NotifyQHistory:
            gui.NotifyQ.put(message)
        progress = progressor.current_cp()
        print "Loaded progress is {}".format(progress)
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

    else:
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
        gui_notify("Sending pickorder:{}".format(LockPickCorrectPickOrder))

        # taperecorder load 1 and pauses

        failed = display_status_all_devices()

        # give gui time to print all the stuff??
        dt = time.time() - t
        if dt < 10:
            time.sleep(10 - dt)

        for device in failed:
            display_status(device)

        ElevatorDoor.close()
        # Send2SplitFlapThread("  Camp Z   ", time_between=None)
        # ShootingRange.send("DispColors", Colors=[0]*5)
        CalibrateStealth()

        DoorController.close_all()
        music_send("KILL AUDIO")
        # Activate elevator noise that will loop until elevator is escaped -AJ
        music_send("ELEVATOR NOISE")


    gui.next_up("Put People in Elevator and they escape into the room", bg="yellow")
    gui_notify("Initialization complete")

    def printrssi():
        while True:
            time.sleep(2)
            stuff = "RSSI={}".format(mynetwork.Base.report()[0])
            gui_notify(stuff)

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
    gui_notify(status)
    return ret


# SplitFlap

def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get(1.0, gui.tk.END).strip().upper()
    print "I want to send this to splitflap: " + stuff2send
    Send2SplitFlapThread(str(stuff2send))
    gui.SplitFlapEntry.delete(0., float(len(stuff2send)))
    gui_notify("'" + stuff2send.replace('\n', ' / ') + "' sent to SplitFlap", fail=True)


# gui.SplitFlapEntry.bind("<Return>", send_to_split_flap)
gui.SplitFlapEntryButton.bind("<Button-1>", send_to_split_flap)


class SplitFlapTimeWarnerBro(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.wait = False

        self.DispAt = [m*60 for m in TimeLeftWarnings]
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
        if gui.globals.ClockStartTime is None:
            return None
        return MaxPlayingTime - (time.time() - gui.globals.ClockStartTime)

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
    PassingScores = {"Thievery": 15,
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
        self.Deductions = {"Thievery": 0,
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


def music_send(what):
    gui_notify("Sending: '{}' to Background Music".format(what))
    Music.send(what)


def start_music():
    music_send("StartMusic")


# Elevator


def ElevatorEscaped(fail=False):
    # passcodes are 4132 and 1341

    # Escaping Elevator starts the room.
    # clock starts now and intro message from TapeRecorder
    # should start in a bit

    if progressor.log("Elevator"):

        ElevatorDoor.open()
        gui.globals.ClockStartTime = time.time()
        gui.globals.ClockHasStarted = True
        logging.debug("starting clock")

        run_after(ElevatorDoor.close, seconds=15)
        if fail:
            gui_notify("Elevator failed, opened manually", fail=True)
        else:
            gui_notify("Elevator Successfully Escaped", solved=True)
        nextFailButton("Elevator Escape")
        TapeRecorder_play("Room Intro")
        TapeRecorder.send("Pause")
        music_send("BACKGROUND NOISE")
        gui.next_up("Players pless play on TapeRecorder. \n\n"
                    "Make sure they close the Elevator door behind them\n\n"
                    "{} players, is that correct?".format(NofPlayers), bg='yellow')
        run_after(start_music, seconds=0.5)
        gui.update_hints("Start Lie Detector")

        # starts first hint after 3 minutes -AJ
        run_after(start_tape, seconds=60*5)

def start_tape():

    result = gui.askquestion("Start first taperecorder hint", "Do you want to play the first tape msg?")
    if result == "yes":
        StartTapeRecorderIntroMessage(fail=True)


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
                     ("6.ogg", 30, "Bomb Go Boom!!!", 1.4),
                     ("8.ogg", 31, "Time Ran Out", 2.3),
                     ("a.ogg", 17, "Shooting Range Instructions", 2.3),
                     ("b.ogg", 6, "Colored Circles", 0.1),
                     ("c.ogg", 18, "Stealth Rules", 0)]


def TapeRecorder_play(filehandle):
    index = [_t[2] for _t in TapeRecorderFiles].index(filehandle)
    _f = TapeRecorderFiles[index][0]
    TapeRecorder.send(Command='Load', s=_f + "\0"*(10 - len(_f)),
                      FileLength=TapeRecorderFiles[index][1],
                      StartPos=int(TapeRecorderFiles[index][3]*10))


def StartTapeRecorderIntroMessage(timeout=False, fail=False):
    global TapeRecorderIntroMessageStarted
    if not TapeRecorderIntroMessageStarted:
        if progressor.current_cp() == "Elevator":
            TapeRecorderIntroMessageStarted = True
            TapeRecorder.send("Play")
            gui_notify("TapeRecorder Intro Message Started")
            # run_after(PlayLockPickingHint, seconds=5+50)
            nextFailButton("Start TapeRecorder")
            gui.next_up("Players Pick the Lock", bg='green')
            gui.update_hints("LockPicking")
            print("asdf")


# def PlayLockPickingHint(fail=False):
#     gui_notify("LockPicking hint started playing")
#     TapeRecorder.send(Command='Load', s="3.ogg" + "\0"*5, FileLength=17)


# LockPicking


def LockPickingCompleted(fail=False):
    if progressor.log("LockPicking"):
        if fail:
            gui_notify("LockPicking failed, opened manually", fail=True)
            LockPicking.send("OpenYourself")
        else:
            gui_notify("LockPicking Successfully Completed", solved=True)
        nextFailButton("Open Safe")
        gui.next_up("Players examine pearls under ultraviolet lamp, input \n"
                    "the color sequence into GreenDude and turn the dial",
                    bg="green")
        gui.update_hints("GreenDude")


def lockpicking_receive(d):
    if d["Command"] == "LockWasPicked":
        LockPickingCompleted()


LockPicking.bind(receive=lockpicking_receive)


# GreenDude


def GreenDudeCompleted(fail=False):
    if progressor.log("GreenDude"):
        gui_notify("GreenDude Correct Passcode entered", fail=fail, solved=not fail)
        TapeRecorder_play("Rod Hint")
        # run_after(BookDrawer.open, seconds=12)
        nextFailButton("GreenDude Fail")
        gui.next_up("Players put the rod into lamp and discover \n"
                    "the sequence for the LieDetector (636)", bg="green")


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

    @staticmethod
    def _update():
        d = GreenDude.send_and_receive("Status")
        # print d
        if d:
            gui.GreenDudeSetColors(d["Lights"])


GreenDudeUpdater = GreenDudeUpdaterClass()
gui.GreenDudeCanvas.bind("<Button-1>", GreenDudeUpdater.update)


# Lie Detector


def LieDetectorActivated(fail=False):
    if progressor.log("LieDetectorStart"):
        gui.globals.StealthActive = False
        LieDetectorHandler.setnofplayers(NofPlayers)
        gui_notify("Lie Detector Activated", fail=fail, solved=not fail)
        music_send("LIE DETECTOR START")
        BookDrawer.open()
        time.sleep(5)
        TapeRecorder_play("Lie Detector Instructions")
        # run_after(BookDrawer.open, seconds=19.5,)
        LieButtons.send("CorrectLightShow")
        nextFailButton("Start Lie Detector")
        run_after(LieDetectorHandler.start_lie_detector, seconds=5)
        gui.next_up("LieDetector!, Host input Required!", bg="red")
        gui.update_hints("LieDetector")


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


LieDetectorOperationLock = threading.Lock()


class LieDetectorOperationHandler(object):
    def __init__(self):
        self.P = None

        self.has_failed_map = False
        self.has_failed_factory = False
        self.has_failed_passport= False
        self.no_fails_map = 0
        self.no_fails_factory = 0
        self.no_fails_passport = 0
        self.name_of_current_scene = ""


        self.ScenesAvailable = [None, None, None]
        #                       B  , PP     , GB
        #                       MAP, FACTORY, PASSPORT
        #                       removed randomization from map and factory, added 2 player mode -AJ

        self.setnofplayers(random.randint(2, 5))

        # For passport, the first playthrough GB5_1 is played
        # if that fails, the next playthrough GB5_2 is played
        # third fail GB5_3 is played
        # in all Missions, if players fail, the first video (B1.mov, PP1.mov and GB1_LJ) is not played
        # in next playthrough

        # set all diff scenarios here:
        self.map_scenes = ["B1.mov", "B2.mov", "B3.mov", "B4.mov", "B5_2.mov", "B6.mov"]
        self.map_scenes_failed = ["B2.mov", "B3.mov", "B4.mov","B5_2.mov", "B6.mov"]

        self.factory_scenes = ["PP1.mov", "PP2.mov", "PP3.mov", "PP4.mov","PP5_2.mov", "PP6.mov"]
        self.factory_scenes_failed1 = ["PP2.mov", "PP3.mov", "PP4.mov","PP5_3.mov", "PP6.mov"]
        self.factory_scenes_failed2 = ["PP2.mov", "PP3.mov", "PP4.mov","PP5_4.mov", "PP6.mov"]

        self.passport_scenes = ["GB1_LJ.mov", "GB2_B.mov", "GB3_J.mov", "GB4_B.mov", "GB5_1.mov", "GB6.mov"]
        self.passport_scenes_failed1 = ["GB2_B.mov", "GB3_J.mov","GB5_2.mov", "GB6.mov"]
        self.passport_scenes_failed2 = ["GB2_B.mov","GB3_J.mov","GB5_3.mov", "GB6.mov"]

        self.Scenes = [Scene(self.map_scenes, 0, 14),
                       Scene(self.factory_scenes, 1, 15),
                       Scene(self.passport_scenes, 2, 20)]

        self.CurrentScene = None

    def setnofplayers(self, NP):
        # added 2 player mode - AJ
        self.P = NP
        if NP == 2:
            self.ScenesAvailable = [False, True, False]
        elif NP == 3:
            self.ScenesAvailable = [False, True, True]
        elif NP == 4:
            self.ScenesAvailable = [False, True, True]
        elif NP == 5:
            self.ScenesAvailable = [True, True, True]

    def start_lie_detector(self):
        LieButtons.send("SetListenToButtonPresses")
        LiePiA.send("Start")
        LiePiB.send("Start")
        self.disp_scenes_available()

    def disp_scenes_available(self):
        # Checks if player has failed any missions

        if self.has_failed_map: # If player has failed, we skip the first video of each mission
            self.map_scenes = self.map_scenes_failed

        if self.has_failed_factory:
            if self.no_fails_factory == 1:
                self.factory_scenes = self.factory_scenes_failed1
            elif self.no_fails_factory >= 2:
                self.factory_scenes = self.factory_scenes_failed2

        if self.has_failed_passport:
            if self.no_fails_passport == 1:
                self.passport_scenes = self.passport_scenes_failed1
            elif self.no_fails_passport >= 2:
                self.passport_scenes = self.passport_scenes_failed2

        # Redefines available scenes based on number of player failures
        self.Scenes = [
            Scene(self.map_scenes, 0, 14),
            Scene(self.factory_scenes, 1, 15),
            Scene(self.passport_scenes, 2, 20)
        ]

        bla = self.ScenesAvailable


        LieButtons.send("Disp", Lights=[int(not bla[0]), int(not bla[1]), int(not bla[2]), 1, 1, 1, 1])
        if not any(self.ScenesAvailable):
            LieDetectorCompleted()

    @staticmethod
    def disp_only(n):
        bla = [1, 1, 1, 1, 1, 1, 1]
        bla[n] = 0
        LieButtons.send("Disp", Lights=bla)

    def handle(self, incoming):
        if LieDetectorOperationLock.locked():
            return
        with LieDetectorOperationLock:
            print incoming
            if incoming["SenderName"] == "Lie2Buttons":
                if gui.globals.StealthActive:
                    StealthButton(incoming["Command"])

                elif incoming["Command"] == "Button1Press":
                    # Players pass the question
                    music_send("RIGHT ANSWER")
                    time.sleep(1)
                    if self.CurrentScene is None:
                        music_send("LIE DETECTOR START")
                        print "No CurrentScene, byebye"
                        return
                    prev_file = str(self.CurrentScene.CurrentFile)
                    self.CurrentScene.next_file()
                    gui_notify("Scene({}) file('{}') passed, now playing '{}'"
                               "".format(self.CurrentScene.N + 1,
                                         prev_file,
                                         self.CurrentScene.CurrentFile), solved=True)

                    if self.CurrentScene.Done:

                        time.sleep(5)
                        Send2SplitFlapThread("Mission {}\n Completed".format(self.CurrentScene.N + 1))
                        LieButtons.send("CorrectLightShow")
                        time.sleep(self.CurrentScene.OutroLength - 5)

                        self.ScenesAvailable[self.CurrentScene.N] = False
                        self.CurrentScene = None
                        self.disp_scenes_available()

                elif incoming["Command"] == "Button2Press":
                    # Players fail the Scene, Go back to Scene selection
                    music_send("WRONG ANSWER")

                    # check what mission
                    # trigger has failed for corresponding mission
                    # add no of fails to that mission

                    if self.name_of_current_scene == "factory":
                        self.has_failed_factory = True # Player has failed once or more -> first video not replayed
                        self.no_fails_factory += 1 # Player has failed x times (random videos are changed)

                    elif self.name_of_current_scene == "map":
                        self.has_failed_map = True
                        self.no_fails_map += 1

                    elif self.name_of_current_scene == "passport":
                        self.has_failed_passport = True
                        self.no_fails_passport += 1

                    self.name_of_current_scene = ""

                    time.sleep(1)
                    music_send("LIE DETECTOR START")
                    if self.CurrentScene is None:
                        return

                    gui_notify("Scene({}) file('{}') failed, resetting..."
                               "".format(self.CurrentScene.N + 1,
                                         self.CurrentScene.CurrentFile), fail=True)
                    self.CurrentScene.reset()
                    self.CurrentScene = None

                    TvPi.send("Reset")
                    Send2SplitFlapThread("Try again", 10)
                    LieButtons.send("IncorrectLightShow")

                    run_after(self.disp_scenes_available, seconds=3)

            elif incoming["SenderName"] == "LieButtons":
                if incoming["Command"] == "CorrectPassCode": # Correct passcode was chosen and liedetector activated
                    LieDetectorActivated()
                elif incoming["Command"] == "ButtonPress":
                    if incoming["Button"] in [0, 1, 2]:
                        if self.CurrentScene is None:
                            if self.ScenesAvailable[incoming["Button"]]:
                                if incoming["Button"] == 2: #if PASSPORT mission is selected -AJ
                                    music_send("MISSION 2 PASSPORT START")
                                    self.name_of_current_scene = "passport"
                                elif incoming["Button"] == 0: #if MAP mission is selected -AJ
                                    music_send("MISSION 3 MAP START")
                                    self.name_of_current_scene = "map"
                                elif incoming["Button"] == 1: #if FACTORY mission is selected -AJ
                                    music_send("MISSION 1 FACTORY START")
                                    self.name_of_current_scene = "factory"

                                self.CurrentScene = self.Scenes[incoming["Button"]]
                                self.CurrentScene.next_file()
                                gui_notify("Player selected Scene({})".format(self.CurrentScene.N + 1))
                                self.disp_only(incoming["Button"])


LieDetectorHandler = LieDetectorOperationHandler()
LieButtons.bind(receive=LieDetectorHandler.handle)
Lie2Buttons.bind(receive=LieDetectorHandler.handle)


LieDetectorHasBeenActivated = False


def LieDetectorCompleted(fail=False):
    if progressor.log("LieDetectorFinish"):
        gui_notify("Lie Detector Completed", fail=fail, solved=not fail)
        music_send("LIE DETECTOR COMPLETE")
        Send2SplitFlapThread("Well Done!", 10)
        time.sleep(3)
        OpenWineBoxHolder()
        time.sleep(2)
        TapeRecorder_play("WineBox Hint")
        nextFailButton("Lie Detector Fail")
        LiePiA.send("Reset")
        LiePiB.send("Reset")
        gui.next_up("Players Discover WineBox, put it \n"
                    "on the correct place and it opens")
        gui.update_hints("Wine Box")


# WineBox

def OpenWineBoxHolder():
    WineBoxHolder.send("Open")


def WineBoxCompleted(fail=False):
    if progressor.log("WineBox"):
        if fail:
            WineBox.send("Open")
        gui_notify("Wine Box opened", fail=fail, solved=not fail)
        nextFailButton("Open WineBox")
        GunDrop.send("MonitorTrigger")
        gui.next_up("Players use the key to open the Gun Range closet and deposit the gun\n"
                    "Host --> Be ready to lower the gun range window thing", bg="yellow")
        gui.update_hints("Shooting Range")


def winebox_receive(d):
    if d['Command'] == "IWasSolved":
        WineBoxCompleted()


WineBox.bind(receive=winebox_receive)


def GunDropped():
    ShootingRangeGame.start()


def gundrop_receive(d):
    if d['Command'] == "Triggered":
        GunDropped()
        GunDrop.send("StopMonitoring")


GunDrop.bind(receive=gundrop_receive)

# Shooting Range


def ShootingRangeCompleted(fail=False):
    if progressor.log("ShootingRange"):
        gui_notify("Shooting Range Completed", fail=fail, solved=not fail)
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
    #TargetNames = "63SZGKY"
    TargetNames = "NZ6KG"
    #
    # Because of way pope talks to shootingrange its unnecessarily complex to add 2 more to the sequence
    # IMPROVE LATER
    # TargetNames = "5M6KG"
    #              01234
    # N - 3 - S - Z - G - K - Y
    # br = bottom right, bl = bottom left, m = middle, tl = top left, tr = top right
    # gamla var: z p c m a

    #        br  - bl      - tl - m - tr
    # gamla: z   - p       - c  - m - a
    # nyja:  5/N - M/H/7/Z - 6  - K/S - 9/G/3
    # corrected:
    # N3SZGKY a mismunandi skotskifum

    def __init__(self):
        #self.TargetSequence = get_shootingrange_sequence(self.SequenceLength)
        self.TargetSequence = [0, 1, 2, 3, 4, 3, 1]
        #                  N  Z  6  K  G
        #                 [0, 1, 2, 3, 4,]
        self.hitnr = 0
        self.GameOver = False

    def start(self):
        self.send_next_target_to_shootingrange()
        self.send_next_target_to_splitflap()
        splitflaptimer.not_now()
        music_send("SHOOTING RANGE")
        # gui.askquestion("Reminder!","Have you turned on the smoke machine for STEALTH?")
        # FIND BETTER PLACE reminder for smoke machine -AJ
        gui.next_up("Players shoot the targets as advised through SplitFlap\n\n"
                    "Host --> Be ready to register hit if the system glitches", bg="yellow")

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
        gui_notify("Target {} was hit!, next target: {}"
                   "".format(target, self.TargetNames[self.TargetSequence[self.hitnr]]),
                   solved=True)
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
        music_send("SHOOTING RANGE DONE")
        if win:
            ShootingRangeCompleted()
            Send2SplitFlapThread("Well Done!", time_between=10)

        if lose:
            Send2SplitFlapThread("Mission \n Failed")
        gui.next_up("Players input Morse code found on TV screen to access Stealth")

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
            # gui_notify("Wrong Target, {} was hit, target is {}".format(d['Target'],
            #                                                            self.TargetSequence[self.hitnr]))
            pass
        elif d['Command'] == "MissionComplete" or d['Command'] == "PuzzleFinished":
            time.sleep(3)
            ShootingRange.send("Reset")


ShootingRangeGame = ShootingRangeGameClass()
ShootingRange.bind(receive=ShootingRangeGame.receive)


def register_hit_fun():
    print "register_hit_fun"
    ShootingRangeGame.target_hit()


# Morser

MorseSequence = [63, 38, 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38, 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38,
                 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38, 25, 6, 63, 32, 31, 6, 57, 38, 31, 0, 63, 38]

StopSequence = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def MorseCompleted(fail=False):
    if progressor.log("Morser"):
        gui_notify("Morse Completed", fail=fail, solved=not fail)
        nextFailButton("Morse Fail")
        # TvPi.send("")
        StealthDoor.open()
        StealthSensor.send("MonitorTrigger")
        TapeRecorder_play("Stealth Rules")


def morse_receive(d):
    if d['Command'] == "CorrectPasscode":
        MorseCompleted()


Morser.bind(receive=morse_receive)


StealthSensorReceivedAlreadyJustShutTheF_UP = False


def stealthsensor_receive(d):
    global StealthSensorReceivedAlreadyJustShutTheF_UP
    if d['Command'] == "Triggered":
        StealthSensor.send("StopMonitoring")
        if not StealthSensorReceivedAlreadyJustShutTheF_UP:
            StealthSensorReceivedAlreadyJustShutTheF_UP = True
            StealthStart()


StealthSensor.bind(receive=stealthsensor_receive)


def run_CalibrateStealth():
    _t = threading.Thread(target=CalibrateStealth)
    _t.setDaemon(True)
    _t.start()


def CalibrateStealth():
    # if StealthActive:
    #     if not gui.askquestion("Stealth Active", "Stealth is active do you still want to calibrate?"):
    #         gui_notify("CalibrateStealth() problem: Stealth is Active, can't calibrate", warning=True)
    #         return

    d = Stealth.send_and_receive("GetPhotovalues", max_wait=4000)
    if not d:
        gui_notify("CalibrateStealth() problem: Didn't get photovalues from Stealth, aborting calibration")
        return

    pvs = d["Sequence"][:6]
    devs = d["Sequence"][10:16]
    maxs = d["Sequence"][20:26]

    thresholds = [min(255, maxs[_i] + devs[_i] + 20) for _i in range(6)]

    s = "CalibrateStealth(): Thresholds calibrated to: {}".format(thresholds)

    gui_notify(s)

    Stealth.send("SetThresholds", Sequence=thresholds)


def StealthStart():
    gui_notify("Stealth Started")
    Stealth.send("SetSequence", Sequence=MorseSequence)

    # senda nytt sequence sem er = 0 thegar stealth er klarad og tha hreyfast ljos aldrei

    StealthSetTempo(1500)

    gui.globals.StealthActive = True
    music_send("STEALTH")
    gui.next_up("Stealth! Host input needed!", bg="red")
    gui.update_hints("Stealth")


def StealthButton(press):
    if press == "Button1Press":
        Stealth.send("SetSequence", Sequence=MorseSequence, Tempo=Stealth.Tempo)
        Sirens.send("SetPin2Low")
        gui_notify("Stealth has been reset")
    elif press == "Button2Press":
        Sirens.send("SetPin2High")


def StealthSetTempo(tempo):
    Stealth.Tempo = tempo
    Stealth.send("SetTempo", Tempo=tempo)


def StealthTripped(lasernr):
    Sirens.send("SetPin2High")
    gui_notify("Stealth tripped on laser {}".format(lasernr))

# testa betur
def StealthCompleted(fail=False):
    gui_notify("Stealth Completed", fail=fail, solved=not fail)
    nextFailButton("Stealth Fail")
    Stealth.send("SetSequence", Sequence=StopSequence, Tempo=0)
    nextFailButton("Stealth Fail")

def stealth_receive(d):
    if d['Command'] == 'Triggered':
        StealthTripped(d["Tripped"])


Stealth.bind(receive=stealth_receive)


# TimeBomb

def BombActivated():
    if gui.globals.ClockStartTime is None:
        RoomTimeLeft = 10*60  # 10 minutes
    else:
        RoomTimeLeft = MaxPlayingTime - (time.time() - gui.globals.ClockStartTime)
    TimeLeft = max(min(MaxBombTime, RoomTimeLeft), MinBombTime)
    gui_notify("Bomb Activated, Time to solve: {}:{}"
               "".format(int(TimeLeft/60), int(TimeLeft) % 60), solved=True)
    TimeBomb.send("SetExplosionTime", Time=int(TimeLeft*1000))
    music_send("BOMB!!!")
    seconds = int(TimeLeft) % 60
    seconds = "0" + str(seconds) if len(str(seconds)) == 1 else str(seconds)

    Send2SplitFlapThread("Time left\n {}:{}".format(int(TimeLeft/60), seconds))
    gui.next_up("Bomb Active, Host --> keep up the Stealth duties", bg="red")
    gui.update_hints("Bomb")


def BombDiffused():
    gui_notify("Bomb Diffused ", solved=True)
    gui_notify("Room Completed!!!", solved=True)
    music_send("VICTORY")
    FinalExitDoor.open()
    RoomOver()


def BombExploded():
    gui_notify("Bomb Exploded!", fail=True)
    music_send("YOU LOSE")
    FinalExitDoor.open()
    RoomOver()


def TimeRunsOut():
    gui_notify("Time's Up! They have lost. MuHAHAH!", fail=True)
    music_send("OUT OF TIME")
    RoomOver()


def RoomOver():
    gui.globals.ClockHasStarted = False
    gui.next_up("Room Over, Congratulate Players", bg="red")


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
        gui_notify("Closing " + doorname)
    else:
        door.open()
        gui_notify("Opening " + doorname)
    update_door_button_colors(recall=False)


for b in gui.DoorButtons:
    b.bind("<Button-1>", door_button_callback)

update_door_button_colors(recall=True)


def tape_recorder_buttons_callback(event=None):
    button = event.widget
    b_text = button.config("text")[-1]
    gui_notify("Tape Recorder: Host pressed " + b_text)
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
    elif b_text == "Stealth Stop":
        result = gui.askquestion("StealthStop", "Are you sure you want to stop the stealth lazers?", icon='warning')
        if result == 'yes':
            StealthStop()
    elif b_text == "Stealth Fail":
        gui_notify("Stealth Fail --- Dont know what you want me to do here")
    elif b_text == "TimeBomb Fail":
        gui_notify("TimeBomb Fail --- Dont know what you want me to do here")
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
                                   command=lambda _t=t: StealthSetTempo(_t))
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
                                                                          s=TapeRecorderFiles[_i][0],
                                                                          FileLength=TapeRecorderFiles[_i][1],
                                                                          StartPos=int(TapeRecorderFiles[_i][3]*10)))
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
                                  command=register_hit_fun)
    if Device == "GunDrop":
        DeviceSubmenu.add_command(label="Register a Detection",
                                  command=GunDropped)
    if Device == "StealthSensor":
        DeviceSubmenu.add_command(label="Register a Detection",
                                  command=StealthStart)



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
    exit()
