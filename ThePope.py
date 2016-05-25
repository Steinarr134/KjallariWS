from Config import *
from HostInterface import startInterface


def GreenDudeReceive(d):
    print(d)

GreenDude.bind(receive=GreenDudeReceive)


def getStatus(d):
    status = d.send_and_receive('Status')
    if status is None:
        raise Exception(d.Name + " did not respond when we checked for status")
    else:
        return status


def init_check_on_moteinos():
    for d in mynetwork.devices:
        getStatus(d)


class TalkingPillow(object):
    def __init__(self):
        self.Holder = None

    def give(self, device):
        assert self.Holder is None
        self.Holder = device
        device.send('ReceiveTheTalkingPillow')

    def reclaim(self):
        if self.Holder is not None:
            self.Holder.send('GiveTheTalkingPillow')
            self.Holder = None

talking_pillow = TalkingPillow()


class Quest(object):
    def __init__(self, next_quest):
        self.NextQuest = next_quest

    def cleanup(self):
        talking_pillow.reclaim()
        self.NextQuest.start()


class Elevator(Quest):
    def __init__(self, next_quest):
        Quest.__init__(self, next_quest)


startInterface()
