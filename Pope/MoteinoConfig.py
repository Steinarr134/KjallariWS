from moteinopy import MoteinoNetwork, look_for_base
import logging
logging.basicConfig(level=logging.DEBUG)
import sys
import os

"""
ToDo:

 - Finish status reporting functions for all devices (see near bottom)


"""


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
        "unsigned long TimeLeft;"
        "int SmokeTime;"
        "boolean SmokeOn;"
        "boolean buzzerOn;",

    'Morser':
        "int Command;" +
        "int Temperature;" +
        "byte Passcode[15];",

    'Stealth':
        "int Command;" +
        "int Tempo;" +
        "byte Tripped;"
        "byte Sequence[50];",

    'GunBox':
        "int Command;" +
        "int Temperature;" +
        "int XYZ[3];",

    'ShootingRange':
        "int Command;" +
        "int Time;" +
        "int Target;" +
        "byte Colors[5];",
    
    'LockPicking':
        "int Command;" +
        "byte PickOrder[6];" +
        "int Temperature;" +
        "long Uptime;",

    'Elevator':
        "int Command;"
        "byte ActiveDoor;"
        "byte PassCode1[4];"
        "byte PassCode2[4];"
        "unsigned long Uptime;",

    'WineBoxHolder':
        "int Command;"
        "long Uptime;",

    'WineBox':
        "int Command;"
        "unsigned long Uptime;"
        "int BatteryStatus;"
        "int X;"
        "int Y;"
        "int Z;"
        "int Time2Solve;",

    'Sirens':
        "int Command;"
        "long Uptime",

    'TvPi':
        "int Command;"
        "char s[10];",
    
    'TapeRecorder':
        "int Command;"
        "char s[10];"
        "int Filelength;"
        "int LightValue;",
}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SplitFlap': 101,
    'TimeBomb': 170,
    'Stealth': 7,
    'Morser': 15,
    'ShootingRange': 31,
    'TestDevice': 0,
    'LockPicking': 176,
    'Elevator': 5,
    'WineBoxHolder': 36,
    'WineBox': 24,
    'Sirens': 37,
    'TvPi': 41,
    'TapeRecorder': 42,
    'LiePi1': 51,
    'LiePi2': 52,
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}

if "win" in sys.platform:
    port = raw_input("what port?")
    # mynetwork = MoteinoNetwork(port, network_id=7, encryption_key="HugiBogiHugiBogi")
else:
    ports = os.popen("ls /dev/ttyUSB*").read()
    if ports:
        for p in ports.split('\n'):
            ret, reason = look_for_base("/dev/ttyUSB0")
            if not ret:
                print reason
            else:
                port = p
                break
        
mynetwork = MoteinoNetwork(port, network_id=7, encryption_key="HugiBogiHugiBogi")

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

SplitFlap = mynetwork.add_node(MoteinoIDs['SplitFlap'],
                               MoteinoStructs['SplitFlap'],
                               'SplitFlap')
SplitFlap.add_translation('Command',
                          ('Disp', 10101),
                          ('Clear', 10102))

Morser = mynetwork.add_node(MoteinoIDs['Morser'],
                            MoteinoStructs['Morser'],
                            'Morser')
Morser.add_translation('Command',
                       ('SetPasscode', 155),
                       ('CorrectPasscode', 151))

LockPicking = mynetwork.add_node(MoteinoIDs['LockPicking'],
                                 MoteinoStructs['LockPicking'],
                                 'LockPicking')
LockPicking.add_translation('Command',
                            ('SetCorrectPickOrder', 17601),
                            ('LockWasPicked', 17602),
                            ('OpenYourself', 17603))

Stealth = mynetwork.add_node(MoteinoIDs['Stealth'],
                             MoteinoStructs['Stealth'],
                             'Stealth')
Stealth.add_translation('Command',
                        ('SetTempo', 73),
                        ('SetSequence', 72),
                        ("Triggered", 71))

TimeBomb = mynetwork.add_node(MoteinoIDs['TimeBomb'],
                              MoteinoStructs['TimeBomb'],
                              'TimeBomb')
TimeBomb.add_translation('Command',
                         ("BombDiffused", 17001),
                         ("BombExploded", 17002),
                         ("SetExplosionTime", 17003),
                         ("BombActivated", 17004),
                         ("SetOptions", 17005))

ShootingRange = mynetwork.add_node(MoteinoIDs['ShootingRange'],
                                   MoteinoStructs['ShootingRange'],
                                   "ShootingRange")
ShootingRange.add_translation("Command",
                              ("SetTime", 3101),
                              ("TargetHit", 3102),
                              ("dispColor", 3103))

Elevator = mynetwork.add_node(MoteinoIDs['Elevator'],
                              MoteinoStructs['Elevator'],
                              "Elevator")
Elevator.add_translation("Command",
                         ('SetPassCode', 501),
                         ('SolveDoor1', 503),
                         ('SolveDoor2', 504),
                         ('SetActiveDoor', 506),
                         ('Solved', 507))


WineBoxHolder = mynetwork.add_node(MoteinoIDs['WineBoxHolder'],
                                   MoteinoStructs['WineBoxHolder'],
                                   "WineBoxHolder")
WineBoxHolder.add_translation("Command", ("open", 3601), ("close", 0))


WineBox = mynetwork.add_node(MoteinoIDs['WineBox'],
                             MoteinoStructs['WineBox'],
                             'WineBox')
WineBox.add_translation("Command",
                        ("open", 2401),
                        ("IWasSolved", 2402),
                        ("SetTime2Solve", 2403))

TvPi = mynetwork.add_node(MoteinoIDs['TvPi'],
                          MoteinoStructs['TvPi'],
                          'TvPi')
TvPi.add_translation("Command",
                     ("PlayFile", 4101))

TapeRecorder = mynetwork.add_node(MoteinoIDs['TapeRecorder'],
                                  MoteinoStructs['TapeRecorder'],
                                  'TapeRecorder')
TapeRecorder.add_translation("Command",
                             ("Play", 4201),
                             ("Pause", 4202),
                             ("ShutDown", 4203),
                             ("Reboot", 4204),
                             ("Setlights", 4205),
                             ("Load", 4206),
                             ("Status", 99))

Sirens = mynetwork.add_node(MoteinoIDs['Sirens'],
                            MoteinoStructs['Sirens'],
                            'Sirens')
Sirens.add_translation("Command",
                       ("TogglePin1", 3701),
                       ("TogglePin2", 3702),
                       ("SetPin1High", 3703),
                       ("SetPin1Low", 3704),
                       ("SetPin2High", 3705),
                       ("SetPin2Low", 3706))


def StealthRec(d):
    if d['Command'] == 'Triggered':
        print "Slave {} Triggered".format(d['Tripped'])
        Sirens.send("TogglePin1")
    else:
        print "Stealth said: " + str(d)

def moteino_status(device):
    d = mynetwork.send_and_receive(device, Command="Status")
    if not d:
        return "No response from {}".format(device)

    if device == "Elevator":
        return "Elevator up and running, passcode is: {}".format(d['Passcode'])

    elif device == "GreenDude":

        return "GreenDude is up and running, Passcode is: "

Stealth.bind(receive=StealthRec)
