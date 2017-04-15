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


"""
TODO:


Complete the form about player info

Control the lights

Set up wifi network for pi to pi communication -- needs more work :/

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





def initialize_room():
##    LockPicking.send("Reset")
    time.sleep(1)
##    LockPicking.send("SetCorrectPickOrder", [0, 1, 2, 3, 4, 5])


def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get(1.0, gui.tk.END).strip()
##    print "I want to send this to splitflap: " + stuff2send
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
    b_text = button.config("text")[-1]
    if b_text == "Elevator Escape":
        result = tkMessageBox.askquestion("Elevator", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            Elevator.send("SolveDoor1")
            ElevatorEscaped()
    elif b_text == "Start TapeRecorder":
        result = tkMessageBox.askquestion("Elevator", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            StartTapeRecorderIntroMessage()
    elif b_text == "Open Safe":
        result = tkMessageBox.askquestion("Elevator", "Are you sure want to skip this mission?", icon='warning')
        if result == 'yes':
            LockPicking.send("OpenYourself")
    else:
        print "Don't know what happened but b_text was: " + b_text
for b in gui.MissionFailButtons:
    b.bind("<Button-1>", mission_fail_callback)




    
def ElevatorEscaped():
    # passcodes are 4132 and 1341
    run_after(StartTapeRecorderIntroMessage, seconds=20)
    gui.ClockHasStarted = True
    gui.ClockStartTime = time.time()
    gui.notify("Elevator Successfully Escaped")
    logging.debug("starting clock")
        

TapeRecorderIntroMessageStarted = False
def StartTapeRecorderIntroMessage(timeout=False):
    global TapeRecorderIntroMessageStarted
    if not TapeRecorderIntroMessageStarted:
        TapeRecorderIntroMessageStarted = True
        TapeRecorder.send(
            {'Command': 'Load', 'filename':"1.ogg",
                           'StartPlaying':True, 'filelength':50})
        gui.notify("TapeRecorder Intro Message Started")

def GreenDudeCompleted():
    TapeRecorder.send("start next??")
    
def LieDetectorActivated():
    TapeRecorder.send("next message??")

def LieDetectorCompleted():
    TapeRecorder.send("sdfkj2??")
    WineCaseHolderDoor.open()

def ShootingRangeCompleted():
    pass # ??

def MorseCompleted():
    TapeRecorder.send("FDSS??")
    StealthDoor.open()

def StealthCompleted():
    pass #??

def BombActivated():
    pass

def BombDiffused():
    pass


def elevator_receive(d):
    if d["Command"] == "Solved":
        ElevatorEscaped()
Elevator.bind(receive=elevator_receive)


def lockpicking_receive(d):
    if d["Command"] == "LockWasPicked":
        notify("Safe successfully opened")
LockPicking.bind(receive=lockpicking_receive)


def green_dude_receive(d):
    if d['Command'] == "CorrectPasscode":
        TapeRecorder.send("GreenDudeCorrect")
        time.sleep(1)
        BookDrawerDoor.open()
GreenDude.bind(receive=green_dude_receive)


def init_check_on_moteinos():
    for device in mynetwork.devices:
        get_status(device)


if __name__ == "__main__":
    initialize_room()
    gui.top.mainloop()

##
##startInterface()
##
##sleep_forever()
