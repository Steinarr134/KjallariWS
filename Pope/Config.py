from moteinopy import MoteinoNetwork
import logging
logging.basicConfig(level=logging.DEBUG)

Moteinos = ['GreenDude',
            'SplitFlap',
            'TimeBomb',
            'Morser',
            'Stealth',
            'LockPicking']


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
        "int Temperature;" +
        "byte Passcode[15]",

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
        "int Score;",

    'LockPicking':
        "int Command;" +
        "byte PickOrder[6];" +
        "int Temperature;" +
        "long Uptime;"

}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SplitFlap': 101,
    'TimeBomb': 170,
    'Stealth': 7,
    'Morser': 15,
    'TestDevice': 0,
    'LockPicking': 176,
    # 'GunBox': ??,
    # 'ShootingRange': ??
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}


mynetwork = MoteinoNetwork('/dev/ttyUSB0', network_id=7, encryption_key="HugiBogiHugiBogi")
# mynetwork = MoteinoNetwork('COM11', network_id=7, encryption_key="HugiBogiHugiBogi")

mynetwork.add_global_translation('Command',
                                 ('Status', 99),
                                 ('Reset', 98))

GreenDude = mynetwork.add_node(MoteinoIDs['GreenDude'],
                               MoteinoStructs['GreenDude'],
                               'GreenDude')
GreenDude.add_translation('Command',
                          ('Disp', 1101),
                          ('SetPasscode', 1102),
                          ('CorrectPasscode', 1103))

# LockPicking = mynetwork.add_node(MoteinoIDs['LockPicking'],
#                                  MoteinoStructs['LockPicking'],
#                                  'LockPicking')

SplitFlap = mynetwork.add_node(MoteinoIDs['SplitFlap'],
                               MoteinoStructs['SplitFlap'],
                               'SplitFlap')
SplitFlap.add_translation('Command',
                          ('Disp', 10101),
                          ('Clear', 10102))

TimeBomb = mynetwork.add_node(MoteinoIDs['TimeBomb'],
                              MoteinoStructs['TimeBomb'],
                              'TimeBomb')
TimeBomb.add_translation('Command',
                         ('BombIsDiffused', 17001),
                         ('BombExploded', 17002))

Morser = mynetwork.add_node(MoteinoIDs['Morser'],
                            MoteinoStructs['Morser'],
                            'Morser')
Morser.add_translation('Command',
                       ('SetPasscode', 155),
                       ('CorrectPasscode', 151))
LockPicking = mynetwork.add_node(MoteinoIds['LockPicking'],
                                 MoteinoStructs['LockPicking'],
                                 'LockPicking')
LockPicking.add_transtlation('Command',
                             ('SetCorrectPickOrder', 17601),
                             ('LockWasPicked', 17602))


# QuestList = [
#     'Elevator',
#     'LockPicking',
#     'GreenDude',
#     'WineCase',
#     'ShootingRange'
# ]

