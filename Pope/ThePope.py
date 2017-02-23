##from Setup import *
##from HelperStuff import *
import HostInterface as gui
from Setup import *

"""
TODO:

Set up a new logger that prints valuable and readable information to the host
it probably needs a thread or some cool method to be able to print to LogTextWidget

Complete the form about player info

Control the lights

Set up wifi network for pi to pi communication

Set up Database

Be able to abruptly stop and resume as if nothing happened
    First clearly define a state space
    rest will come 'EZ'

    



"""


def initialize_room():
    LockPicking.send("Reset")
    time.sleep(1)
    LockPicking.send("SetCorrectPickOrder", [0, 1, 2, 3, 4, 5])


def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get(1.0, gui.tk.END).strip()
##    print "I want to send this to splitflap: " + stuff2send
    Send2SplitFlapThread(str(stuff2send))
    gui.SplitFlapEntry.delete(0., float(len(stuff2send)))

#gui.SplitFlapEntry.bind("<Return>", send_to_split_flap)
gui.SplitFlapEntryButton.bind("<Button-1>", send_to_split_flap)


def door_button_callback(event=None):
    button = event.widget
    door = Doors[gui.DoorNameList.index(button.config("text")[-1])]
    if door.is_open():
        door.close()
        button.configure(bg='green')
    else:
        door.open()
        button.configure(bg='red')
        

for b in gui.DoorButtons:
    b.bind("<Button-1>", door_button_callback)

    
def update_door_buttons(event=None):
    for door in Doors:
        pass

def lockpicking_receive(d):
    if d["Command"] == "LockWasPicked":
        print "YEAH!!!"
    



##def elevator_receive(d):
##    if d["Command"] == "CorrectPasscode":
##        ElevatorDoor.open()
##        run_after(ElevatorDoor.close(), seconds=2)
##
##Elevator.bind(receive=elevator_receive)
##
##
##def green_dude_receive(d):
##    if d['Command'] == "CorrectPasscode":
##        TapeRecorder.send("GreenDudeCorrect")
##
##
##GreenDude.bind(receive=green_dude_receive)
##
##
##
##def init_check_on_moteinos():
##    for device in mynetwork.devices:
##        get_status(device)


if __name__ == "__main__":
    initialize_room()
    gui.top.mainloop()

##
##startInterface()
##
##sleep_forever()
