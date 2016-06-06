from Config import *
from HostInterface import startInterface

class TalkingPillow(object):
    def __init__(self):
        self.Holder = None

    def give(self, device):
        assert self.Holder is None
        if type(device) is str:
            device = mynetwork.devices[device]
        self.Holder = device
        device.send('ReceiveTheTalkingPillow')

    def reclaim(self):
        if self.Holder is not None:
            self.Holder.send('GiveTheTalkingPillow')
            self.Holder = None

talking_pillow = TalkingPillow()
    

def ElevatorReceive(d):
    if d["Command"] == "CorrectPasscode":
        doors.open("ElevatorCampZ")
        aotj(doors.close("ElevatorCampZ"), seconds=2)
        
        talking_pillow.reclaim()
        talking_pillow.give(LockPicking)
        
        
def GreenDudeReceive(d):
    if d['Command'] == "CorrectPasscode":
        TapeRecorder.play("GreenDudeCorrect")

        talking_pillow.reclaim()

GreenDude.bind(receive=GreenDudeReceive)


def getStatus(d):
    status = d.send_and_receive('Status')
    if status is None:
        raise Exception(d.Name + " did not respond when we checked for status")
    else:
        return status


def init_check_on_moteinos():
    for device in mynetwork.devices:
        getStatus(device)





class ElevatorQuest


startInterface()

sleep_forever()
