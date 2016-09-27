from Config import *
from HostInterface import gui
    

def elevator_receive(d):
    if d["Command"] == "CorrectPasscode":
        doors.open("ElevatorCampZ")
        aotj(doors.close("ElevatorCampZ"), seconds=2)

Elevator.bind(receive=elevator_receive)
        
def green_dude_receive(d):
    if d['Command'] == "CorrectPasscode":
        TapeRecorder.send("GreenDudeCorrect")


GreenDude.bind(receive=green_dude_receive)



def init_check_on_moteinos():
    for device in mynetwork.devices:
        getStatus(device)





class ElevatorQuest


startInterface()

sleep_forever()
