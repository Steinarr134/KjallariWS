from Setup import *
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

scheduler = BackgroundScheduler()
scheduler.start()


def run_after(func, seconds=0, minutes=0):
    scheduler.add_job(func,
                      'date',
                      run_date=datetime.fromtimestamp(time.time() + seconds + 60*minutes))

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

def save_group_info(player_info={}):
    print "save_group_info() wants to save:{} but need programming".format(player_info)
    pass

def new_group():
    result = gui.askquestion("Start new group?",
                             "Do you want to start a new group?",
                             icon='warning')
    if result == 'yes':
        # make sure everything about the previous group has been saved
        gui.player_info(initialize_room)

def edit_group_info():
    gui.player_info(save_group_info, CurrentPlayerInfo)

def initialize_room(player_info={}):
    """
    This function should set everything up
    That includes resetting any variables
    """
    player_info['room initialization time'] = time.time()
    save_group_info(player_info)
    
    LockPicking.send("Reset")
    LockPicking.send("SetCorrectPickOrder", [0, 1, 2, 3, 4, 5])

    Elevator.send("SetActiveDoor", 1)

    display_status_all_devices()

    # gui.notify("Test warning", warning=True)
    # gui.notify("Test solved", solved=True)
    # gui.notify("Test Fail", fail=True)
    
def display_status_all_devices():
    for device in Devices:
        display_status(device)


def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get(1.0, gui.tk.END).strip()
    print "I want to send this to splitflap: " + stuff2send
    Send2SplitFlapThread(str(stuff2send))
    gui.SplitFlapEntry.delete(0., float(len(stuff2send)))

#gui.SplitFlapEntry.bind("<Return>", send_to_split_flap)
gui.SplitFlapEntryButton.bind("<Button-1>", send_to_split_flap)


def update_door_button_colors(recall=True):
    for i in range(len(gui.DoorNameList)):
        if Doors[i].is_open():
            gui.DoorButtons[i].configure(bg='green')
        else:
            gui.DoorButtons[i].configure(bg='red')
    if recall:
        gui.top.after(500, update_door_button_colors)


def door_button_callback(event=None):
    button = event.widget
    
    door = Doors[gui.DoorNameList.index(button.config("text")[-1])]
    if door.is_open():
        door.close()
    else:
        door.open()
    update_door_button_colors(recall=False)

for b in gui.DoorButtons:
    b.bind("<Button-1>", door_button_callback)

update_door_button_colors(recall=True)
    

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
    else:
        print "Don't know what happened but b_text was: " + b_text
for b in gui.MissionFailButtons:
    b.bind("<Button-1>", mission_fail_callback)



def ElevatorEscaped(fail=False):
    # passcodes are 4132 and 1341

    # Escaping Elevator starts the room.
    # clock starts now and intro message from TapeRecorder
    # should start in a bit
    print "ELevator Escape running"
    ElevatorDoor.open()
    run_after(StartTapeRecorderIntroMessage, seconds=20)
    gui.ClockHasStarted = True
    gui.ClockStartTime = time.time()
    run_after(ElevatorDoor.close, seconds=15)
    if fail:
        gui.notify("Elevator failed, opened manually", fail=True)
    else:
        gui.notify("Elevator Successfully Escaped", solved=True)
    gui.MissionFailButtons[0].config(state=gui.tk.DISABLED)
    gui.MissionFailButtons[1].config(state=gui.tk.NORMAL)
    logging.debug("starting clock")


def LockPickingCompleted(fail=False):
    LockPicking.send("OpenYourself")
    if fail:
        gui.notify("LockPicking failed, opened manually", fail=True)
    else:
        gui.notify("LockPicking Successfully Completed", solved=True)
    gui.MissionFailButtons[1].config(state=gui.tk.DISABLED)


def PLayLockPickingHint(fail=False):
    TapeRecorder.send(Command='Load', s="3.ogg"+ "\0"*5, filelength=50)


TapeRecorderIntroMessageStarted = False
def StartTapeRecorderIntroMessage(timeout=False, fail=False):
    global TapeRecorderIntroMessageStarted
    if not TapeRecorderIntroMessageStarted:
        TapeRecorderIntroMessageStarted = True
        TapeRecorder.send(Command='Load', s="1.ogg"+ "\0"*5, filelength=50)
        gui.notify("TapeRecorder Intro Message Started")
        run_after(PLayLockPickingHint, seconds=5+50)


def GreenDudeCompleted(fail=False):
    TapeRecorder.send(Command='Load', s="5.ogg"+ "\0"*5, filelength=40)


def LieDetectorActivated():
    TapeRecorder.send("next message??")


def LieDetectorCompleted(fail=False):
    TapeRecorder.send("sdfkj2??")
    WineCaseHolderDoor.open()


def ShootingRangeCompleted():
    pass # ??


def MorseCompleted(fail=False):
    TapeRecorder.send("FDSS??")
    StealthDoor.open()


def StealthCompleted(fail=False):
    pass #??


def BombActivated():
    pass


def BombDiffused():
    pass


def elevator_receive(d):
    if d["Command"] == "SolveDoor1":
        ElevatorEscaped()

    else:
        print "elevator receive: " + str(d)
Elevator.bind(receive=elevator_receive)


def lockpicking_receive(d):
    if d["Command"] == "LockWasPicked":
        gui.notify("Safe successfully opened")
LockPicking.bind(receive=lockpicking_receive)


def green_dude_receive(d):
    if d['Command'] == "CorrectPasscode":
        GreenDudeCompleted()
GreenDude.bind(receive=green_dude_receive)


def display_status(device):
    print("display status", device)
    gui.notify(moteino_status(device))


for DeviceSubmenu, Device in zip(gui.DeviceSubmenus, Devices):
    DeviceSubmenu.add_command(label="Get Status for {}".format(Device), command=lambda Device=Device: display_status(Device))
    print Device

gui.ActionMenu.add_command(label="Check All Device Status", command=display_status_all_devices)  # vantar command=sdafsaf
# gui.ActionMenu.add_command(label="Reset Room")
gui.ActionMenu.add_command(label="New Group", command=new_group)
gui.ActionMenu.add_command(label="Edit Group info", command=edit_group_info)


if __name__ == "__main__":
    run_after(initialize_room, seconds=1)
    gui.top.mainloop()

##
##startInterface()
##
##sleep_forever()
