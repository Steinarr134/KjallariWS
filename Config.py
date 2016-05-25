from moteinopy import MoteinoNetwork


Moteinos = ['GreenDude']


MoteinoCommands = {
    'CorrectPasscode': 25,
    'Status': 99,
    'Test1': 1,
    'Test2': 2,
}

MoteinoStructs = {
    'GreenDude': "int Command;" + "byte Lights[7];" + "byte Temperature;",
    'SplitFlap': "int Command;" + "char Letters[11];" + "byte Temperature;"
}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SplitFlap': 101,
    'Stealth': 7,
    'TestDevice': 0
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}


class MyNetwork(MoteinoNetwork):
    def receive(self, sender, diction):
        print("Something was received!!!!!!")


# mynetwork = MyNetwork('/dev/ttyAMA0')
mynetwork = MyNetwork('COM50')


GreenDude = mynetwork.add_device(MoteinoIDs['GreenDude'],
                                 MoteinoStructs['GreenDude'],
                                 'GreenDude')
GreenDude.add_translation('Command',
                          ('Status', 99),
                          ('Disp', 1101),
                          ('GiveTalkingPillow', 42),
                          ('TakeAwayTalkingPillow', 43),
                          ('SetPassCode', 1102),)


SplitFlap = mynetwork.add_device(MoteinoIDs['SplitFlap'],
                                 MoteinoStructs['SplitFlap'],
                                 'SplitFlap')
SplitFlap.add_translation('Command',
                          ('Status', 99),
                          ('Disp', 10101),
                          ('ClearAll', 10102))

QuestList = [
    'Elevator',
    'LockPicking',
    'GreenDude',
    'WineCase',
    'ShootingRange'
]

