##from Setup import *
##from HelperStuff import *
import HostInterface as gui
from Setup import *


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



gui.top.mainloop()

##
##startInterface()
##
##sleep_forever()
