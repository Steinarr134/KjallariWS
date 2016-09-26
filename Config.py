import moteinopy
import apscheduler

scheduler = None # skilgreina seinna


Moteinos = ['GreenDude',
            'SplitFlap',
            'TimeBomb']


MoteinoCommands = {
    'CorrectPasscode': 25,
    'Status': 99,
    'Test1': 1,
    'Test2': 2,
}

MoteinoStructs = {
    'GreenDude': "int Command;" +
                 "byte Lights[7];" +
                 "byte Temperature;",
    'SplitFlap': "int Command;" +
                 "char Letters[11];" +
                 "byte Temperature;",
    'TimeBomb': "int Command;" +
                "unsigned long TimeLeft;" +
                "int Temperature;",

}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SplitFlap': 101,
    'TimeBomb': 170,
    'Stealth': 7,
    'TestDevice': 0
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}


class MyNetwork(moteinopy.MoteinoNetwork):
    def receive(self, sender, diction):
        print("Something was received!!!!!!")


# mynetwork = MyNetwork('/dev/ttyAMA0')
mynetwork = MyNetwork('COM50')

mynetwork.add_global_translation('Command',
                                 ('Status', 99),
                                 ('Reset', 98),
                                 ('HereIsTheTalkingPillowTakeIt', 42),
                                 ('GiveMeTheTalkinPillow', 43))

GreenDude = mynetwork.add_device(MoteinoIDs['GreenDude'],
                                 MoteinoStructs['GreenDude'],
                                 'GreenDude')
GreenDude.add_translation('Command',
                          ('Disp', 1101),
                          ('SetPasscode', 1102),
                          ('CorrectPasscode', 1103))

LockPicking = mynetwork.add_device(MoteinoIDs['LockPicking'],
                                   MoteinoStructs['LockPicking'],
                                   'LockPicking')

SplitFlap = mynetwork.add_device(MoteinoIDs['SplitFlap'],
                                 MoteinoStructs['SplitFlap'],
                                 'SplitFlap')
SplitFlap.add_translation('Command',
                          ('Disp', 10101),
                          ('Clear', 10102))

TimeBomb = mynetwork.add_device(MoteinoIDs['TimeBomb'],
                                MoteinoStructs['TimeBomb'],
                                'TimeBomb')
TimeBomb.add_translation('Command',
                         ('BombIsDiffused', 17001),
                         ('BombExploded', 17002))

QuestList = [
    'Elevator',
    'LockPicking',
    'GreenDude',
    'WineCase',
    'ShootingRange'
]

