##from Setup import *
##from HelperStuff import *
import HostInterface as gui


def send_to_split_flap(event):
    stuff2send = gui.SplitFlapEntry.get().strip()
    print "I want to send this to splitflap: " + stuff2send
    gui.SplitFlapEntry.delete(0, len(stuff2send))

def keypress(event):
    print "you pressed key:" + event.char

def close_window(event):
    gui.top.destroy()

gui.top.bind("<Key>", keypress)
gui.top.bind("<Escape>", close_window)
gui.SplitFlapEntry.bind("<Return>", send_to_split_flap)


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
