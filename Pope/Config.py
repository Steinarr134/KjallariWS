import MoteinoPY


Moteinos = ['GreenDude',
            'SplitFlap',
            'TimeBomb',
            'Morser',
            'Stealth']


MoteinoStructs = {
    'GreenDude':
        "int Command;" +
        "byte Lights[7];" +
        "int Temperature;",

    'SplitFlap':
        "int Command;" +
        "char Letters[11];" +
        "int Temperature;",

    'TimeBomb':
        "int Command;" +
        "unsigned long TimeLeft;" +
        "int Temperature;",

    'Morser':
        "int Command;" +
        "int Temperature;",

    'Stealth':
        "int Command;" +
        "int Temperatures[8]" +
        "int Tempo" +
        "byte Lightshow[50]",

    'GunBox':
        "int Command;" +
        "int Temperature;" +
        "int XYZ[3];",

    'ShootingRange':
        "int Command;" +
        "int Temperature;" +
        "int Score;"

}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SplitFlap': 101,
    'TimeBomb': 170,
    'Stealth': 7,
    'Morser': 5,
    'TestDevice': 0,
    # 'GunBox': ??,
    # 'ShootingRange': ??
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}


class MyNetwork(MoteinoPY.MoteinoNetwork):
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

# QuestList = [
#     'Elevator',
#     'LockPicking',
#     'GreenDude',
#     'WineCase',
#     'ShootingRange'
# ]

