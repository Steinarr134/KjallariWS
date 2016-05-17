from Config import *
from HostInterface import startInterface


def GreenDudeReceive(d):
    print(d)

GreenDude.bind(receive=GreenDudeReceive)


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



class Quest(object):
    def __init__(self, next_quest):
        self.NextQuest = next_quest

    def cleanup(self):
        talking_pillow.reclaim()
        self.NextQuest.start()


class Elevetor(Quest):
    def __init__(self):
        Quest.__init__(self)


startInterface()
