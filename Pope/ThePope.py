from Setup import *
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Configurate logging module
logging.basicConfig(level=logging.DEBUG)


# A nice little quick hand function to run something at a later time using the Scheduler.
def run_after(func, seconds=0, minutes=0):
    scheduler.add_job(func,
                      'date',
                      run_date=datetime.fromtimestamp(time.time() + seconds + 60*minutes))


# This is supposed to hold the player info
CurrentPlayerInfo = {}


"""
TODO:


Laga forrit a lockpicking, koma i veg fyrir ad hann sendi aftur og aftur
og passa ad hann sleppi pinnunum svo ad their haldi ekki afram ad hitna
- buid ad laga forritis, a eftir ad uploada thvi

Spola taperecorder til baka thegar herbergid initializast
Baeta vid styringuf fyrir taperecorder i pafanum,
haegt ad loada hvada file sem er og haegt ad yta a play/pause
Fara yfir lengd a fileum fyrir taperecorder

Laga GreenDude, lata hann senda lykilord med status
- buid ad laga forritid, a eftir ad uploada thvi



Control the lights


Set up Database

Be able to abruptly stop and resume as if nothing happened
    First clearly define a state space
    rest will come 'EZ'

    

Takkar sem thurfa ad vera til:
    Sleppa ur lyftunni (intro mission failed)

    Setja i gang TapeRecorder

    Opna Safe (mission theivery failed)

    TapeRecorder og svoleidis(Mission GreenDude failed)

    Opna Vinkassann
    
    
"""

# Functions to open windows to input and edit group info


def save_group_info(player_info=()):  # kannski ad nota {} i stadinn fyrir ()
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
def initialize_room(player_info=()):
    """
    This function should set everything up
    That includes resetting any variables
    """
    t = time.time()

    player_info['room initialization time'] = t
    save_group_info(player_info)

    LockPicking.send("Reset")
    LockPicking.send("SetCorrectPickOrder", [0, 1, 2, 3, 4, 5])

    TimeBomb.send("Reset")

    Elevator.send("SetActiveDoor", 1)

    Stealth.send("Reset")
    LiePiA.send("Reset")
    LiePiB.send("Reset")

    # TapeRecorder.send("Reset")
    # taperecorder load 1 and pauses

    display_status_all_devices()

    dt = time.time() - t
    if dt < 10:
        time.sleep(10 - dt)
    ElevatorDoor.close()
    # gui.notify("Test warning", warning=True)
    # gui.notify("Test solved", solved=True)
    # gui.notify("Test Fail", fail=True)


# Some helper functions

def display_status_all_devices():
    for device in Devices:
        display_status(device)
        time.sleep(0.1)


def nextFailButton(button=None):
    global currentFailButton
    while True:
        print gui.MissionFailButtons[currentFailButton].config("text")
        b_text = gui.MissionFailButtons[currentFailButton].config("text")[-1]
        gui.MissionFailButtons[currentFailButton].config(state=gui.tk.DISABLED)
        currentFailButton += 1
        print "comparing {} and {}".format(b_text, button)
        if b_text == button:
            gui.MissionFailButtons[currentFailButton].config(state=gui.tk.NORMAL)
            break
        if currentFailButton > 20:
            break


def display_status(device):
    print("display status", device)
    status = moteino_status(device)
    if status[:11] == "No response":
        color = 'red'
    else:
        color = 'green'

    for _i in range(len(gui.DeviceSubmenus)):
        if gui.DeviceMenu.entrycget(_i, 'label') == device:
            gui.DeviceMenu.entryconfig(_i, background=color)
    gui.notify(status)


# SplitFlap

def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get(1.0, gui.tk.END).strip().upper()
    print "I want to send this to splitflap: " + stuff2send
    Send2SplitFlapThread(str(stuff2send))
    gui.SplitFlapEntry.delete(0., float(len(stuff2send)))
    gui.notify("'" + stuff2send.replace('\n', ' / ') + "' sent to SplitFlap", fail=True)


# gui.SplitFlapEntry.bind("<Return>", send_to_split_flap)
gui.SplitFlapEntryButton.bind("<Button-1>", send_to_split_flap)


# Elevator


def ElevatorEscaped(fail=False):
    # passcodes are 4132 and 1341

    # Escaping Elevator starts the room.
    # clock starts now and intro message from TapeRecorder
    # should start in a bit

    if progressor.log("Elevator"):

        ElevatorDoor.open()
        run_after(StartTapeRecorderIntroMessage, seconds=20)
        gui.ClockStartTime = time.time()
        gui.ClockHasStarted = True
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
TapeRecorderFiles = [("1.ogg", 50), ("2.ogg", 15), ("3.ogg", 17), ("4.ogg", 15), ("5.ogg", 21), ("6.ogg", 37)]


def StartTapeRecorderIntroMessage(timeout=False, fail=False):
    if progressor.log("TapeRecorder"):
        global TapeRecorderIntroMessageStarted
        if not TapeRecorderIntroMessageStarted:
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
        TapeRecorder.send(Command='Load', s="5.ogg" + "\0"*5, FileLength=21)
        nextFailButton("GreenDude Fail")


def green_dude_receive(d):
    print "GreenDude Receive"
    if d['Command'] == "CorrectPasscode":
        print "CorrectPassCode"
        GreenDudeCompleted()


GreenDude.bind(receive=green_dude_receive)


# Lie Detector


def LieDetectorActivated(fail=False):
    if progressor.log("LieDetector"):
        gui.notify("Lie Detector Activated", fail=fail, solved=not fail)
        TapeRecorder.send(Command='Load', s="6.ogg" + "\0"*5, FileLength=37)

        nextFailButton("Start Lie Detector")
        run_after(TurnLieDetectorOn, seconds=5)


LieDetectorHasBeenActivated = False
LieDetectorVideos = ["B1.mov", "B2.mov", "B3.mov"]
LieDetectorVideoPosition = -1

TvPiFiles = ["B1.mov",
             "B2.mov",
             "B3.mov",
             "PP1.mov",
             "PP2.mov",
             "PP3.mov",
             "SOS.mov"]


def TurnLieDetectorOn():
    print "TurnLieDetectorOn()"
    LiePiA.send("Start")
    LiePiB.send("Start")


def LieDetectorCompleted(fail=False):
    gui.notify("Lie Detector Completed", fail=fail, solved=not fail)
    TapeRecorder.send(Command='Load', s="7.ogg" + "\0"*5, FileLength=38)
    nextFailButton("Lie Detector Fail")
    run_after(OpenWineBoxHolder, seconds=3)


def liebuttons_receive(d):
    if d['Command'] == "CorrectPassCode":
        LieDetectorActivated()


LieButtons.bind(receive=liebuttons_receive)


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


Lie2Buttons.bind(receive=lie_2_buttons_receive)


# WineBox


def OpenWineBoxHolder():
    WineBoxHolder.send("Open")


def WineBoxCompleted(fail=False):
    gui.notify("Wine Box opened", fail=fail, solved=not fail)
    nextFailButton("Open WineBox")


def winebox_receive(d):
    pass


WineBox.bind(receive=winebox_receive)


# Shooting Range


def ShootingRangeCompleted(fail=False):
    gui.notify("Shooting Range Completed", fail=fail, solved=not fail)
    # Herna vantar eitthvad
    nextFailButton("Shooting Range Fail")


def shooting_range_receive(d):
    if d['Command'] == "TargetHit":
        gui.ShootingCirclesSetColor(d['Target'], 'green')
    elif d['Command'] == "WrongTarget":
        for _i in range(5):
            gui.ShootingCirclesSetColor(_i, 'red')
    elif d['Command'] == "MissionCompleted" or d['Command'] == "PuzzleFinished":
        ShootingRangeCompleted()


ShootingRange.bind(receive=shooting_range_receive)


# Morser

MorseSequence = [63, 0, 2, 0, 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0, 63, 0, 2, 0,
                 3, 5, 5, 5, 14, 10, 10, 10, 20, 20, 20, 40, 40, 40, 48, 16, 16, 16, 0, 0, 0]


def MorseCompleted(fail=False):
    gui.notify("Morse Completed", fail=fail, solved=not fail)
    nextFailButton("Morse Fail")
    Stealth.send("SetSequence", Sequence=MorseSequence)
    Sirens.send("SetPin1Low")


def morse_receive(d):
    pass


Morser.bind(receive=morse_receive)


# Stealth

def StealthRetry():
    MorseCompleted()


def StealthTripped(lasernr):
    Sirens.send("SetPin1High")
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
    pass


def BombDiffused():
    pass


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
    if Device == "Sirens":
        DeviceSubmenu.add_command(label="Turn on",
                                  command=lambda: Sirens.send("SetPin2High"))
        DeviceSubmenu.add_command(label="Turn off",
                                  command=lambda: Sirens.send("SetPin2Low"))

    if Device == "TapeRecorder":
        subsubmenu = gui.tk.Menu(DeviceSubmenu, tearoff=False)
        DeviceSubmenu.add_cascade(label="Play file", menu=subsubmenu)
        for i in range(5):
            subsubmenu.add_command(label=TapeRecorderFiles[i][0],
                                   command=lambda _i=i: TapeRecorder.send("Load",
                                                                          s=TapeRecorderFiles[_i][0] + "\0"*5,
                                                                          FileLength=TapeRecorderFiles[_i][1]))
        DeviceSubmenu.add_command(label="Set Zero Position",
                                  command=lambda: TapeRecorder.send("SetCurrentPosAsZero"))
        DeviceSubmenu.add_command(label="Engage Stupid State",
                                  command=lambda: TapeRecorder.send("SetStupidState"))
    if Device == "LieButtons":
        DeviceSubmenu.add_command(label="Set Active",
                                  command=lambda: LieButtons.send("SetActive"))
        DeviceSubmenu.add_command(label="Set Inactive",
                                  command=lambda: LieButtons.send("SetInactive"))
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
