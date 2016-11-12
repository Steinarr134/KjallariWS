from Setup import *
from HelperStuff import *
from HostInterface import gui
    

def elevator_receive(d):
    if d["Command"] == "CorrectPasscode":
        ElevatorDoor.open()
        run_after(ElevatorDoor.close(), seconds=2)

Elevator.bind(receive=elevator_receive)


def green_dude_receive(d):
    if d['Command'] == "CorrectPasscode":
        TapeRecorder.send("GreenDudeCorrect")


GreenDude.bind(receive=green_dude_receive)



def init_check_on_moteinos():
    for device in mynetwork.devices:
        get_status(device)






startInterface()

sleep_forever()
