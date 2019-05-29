import sys
if "win" in sys.platform:
    sys.path.append("C:\Users\SteinarrHrafn\Documents\GitHub\moteinopy")
else:
    sys.path.append("/home/campz/moteinopy")
from moteinopy import MoteinoNetwork, look_for_base
import logging
logging.basicConfig(level=logging.DEBUG)
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
        "unsigned int Command;" +
        "byte Lights[7];" +
        "byte Temperature;" +
        "byte PassCode[7];",

    'SplitFlap':
        "int Command;" +
        "char Letters[11];" +
        "int Temperature;",

    'TimeBomb':
        "int Command;" +
        "unsigned long Time;"
        "int SmokeTime;"
        "byte SmokeOn;"
        "byte buzzerOn;",

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
        "byte Colors[5];" +
        "int Sequence[5];",
    
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
        "int FileLength;"
        "int LightValue;"
        "int StartPos",

    'LieButtons':
        "int Command;"
        "byte PassCode[3];"
        "byte Lights[7];"
        "byte Button",

    'Lie2Buttons':
        "int Command;"
        "byte Temperature;",

    'StealthSensor':
        "int Command;"
        "byte Trigger;"
        "long Uptime;",
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
    'LieButtons': 51,
    'Lie2Buttons': 54,
    'LiePiA': 53,
    'LiePiB': 52,
    'StealthSensor': 63
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}
port = None
ProbablyDoorSerialPort = None
if "win" in sys.platform:
    port = raw_input("what port?")
    # mynetwork = MoteinoNetwork(port, network_id=7, encryption_key="HugiBogiHugiBogi")
else:
    ports = os.popen("ls /dev/ttyUSB*").read().split('\n')
    print ports
    if ports:
        for p in ports:
            if not p:
                continue
            ret, reason = look_for_base(p)
            if not ret:
                print "No base on {} because: {}".format(p, reason)
            else:
                print "Found base on port: {}".format(p)
                port = p
                break
        for p in ports:
            print " are ProbablyDoors maybe on {}".format(p)
            if p and p != port:
                print "YES!"
                ProbablyDoorSerialPort = p
if port is None:
    print("No Base found, using fake base")

mynetwork = MoteinoNetwork(port, network_id=7, encryption_key="HugiBogiHugiBogi")
mynetwork.logger.setLevel(logging.DEBUG)
mynetwork.default_max_wait = 1000

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
                       ('SetPasscode', 1505),
                       ('CorrectPasscode', 1501))

LockPicking = mynetwork.add_node(MoteinoIDs['LockPicking'],
                                 MoteinoStructs['LockPicking'],
                                 'LockPicking')
LockPicking.add_translation('Command',
                            ('SetCorrectPickOrder', 17601),
                            ('LockWasPicked', 17602),
                            ('OpenYourself', 17603),
                            ('Open', 17603),
                            ('SetActive', 17604),
                            ('SetInactive', 17605))

Stealth = mynetwork.add_node(MoteinoIDs['Stealth'],
                             MoteinoStructs['Stealth'],
                             'Stealth')
Stealth.add_translation('Command',
                        ('SetTempo', 73),
                        ('SetSequence', 72),
                        ("Triggered", 71),
                        ("SetThresholds", 74),
                        ("GetPhotovalues", 75),
                        ("SetSkipdelay", 76))

TimeBomb = mynetwork.add_node(MoteinoIDs['TimeBomb'],
                              MoteinoStructs['TimeBomb'],
                              'TimeBomb')
TimeBomb.add_translation('Command',
                         ("BombDiffused", 17001),
                         ("BombExploded", 17002),
                         ("SetExplosionTime", 17003),
                         ("BombActivated", 17004),
                         ("SetOptions", 17005),
                         ("CalibrateSolution", 17006))

ShootingRange = mynetwork.add_node(MoteinoIDs['ShootingRange'],
                                   MoteinoStructs['ShootingRange'],
                                   "ShootingRange")

# Shooting Range target numbers:
#   2   4
#     3
#   1   0
ShootingRange.add_translation("Command",
                              ("SetTime", 3101),  # Not used anymore
                              ("TargetHit", 3102),  # gets sent when user hits correct target
                              ("DispColors", 3103),  # To use for whatever
                              ("WrongTarget", 3104),  # Gets sent when user hits incorrect target
                              ("MissionComplete", 3105),  # Will be sent when users win the game
                              ("NewSequence", 3106),  # to use to change sequence
                              ("PuzzleFinished", 3107))  #

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
WineBoxHolder.add_translation("Command", ("Open", 3601), ("Close", 0))


WineBox = mynetwork.add_node(MoteinoIDs['WineBox'],
                             MoteinoStructs['WineBox'],
                             'WineBox')
WineBox.add_translation("Command",
                        ("Open", 2401),
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
                             ("Forward", 4207),
                             ("Reverse", 4208),
                             ("ShutDown", 4203),
                             ("Reboot", 4204),
                             ("Setlights", 4205),
                             ("Load", 4206),
                             ("Status", 99),
                             ("Reset", 98),
                             ("SetCurrentPosAsZero", 4209),
                             ("SetStupidState", 4210))

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

LieButtons = mynetwork.add_node(MoteinoIDs['LieButtons'],
                                MoteinoStructs['LieButtons'],
                                'LieButtons')
LieButtons.add_translation("Command",
                           ("CorrectPassCode", 5101),
                           ("ChangePassCode", 5102),
                           ("Disp", 5103),
                           ("SetListenToPasscode", 5104),
                           ("SetListenToButtonPresses", 5105),
                           ("CorrectLightShow", 5106),
                           ("IncorrectLightShow", 5107),
                           ("ButtonPress", 5108)
                           )

LiePiA = mynetwork.add_node(MoteinoIDs['LiePiA'], "int Command;", "LiePiA")
LiePiA.add_translation("Command", ("Start", 50))

LiePiB = mynetwork.add_node(MoteinoIDs['LiePiB'], "int Command;", "LiePiB")
LiePiB.add_translation("Command", ("Start", 50))

Lie2Buttons = mynetwork.add_node(MoteinoIDs['Lie2Buttons'],
                                 MoteinoStructs['Lie2Buttons'],
                                 'Lie2Buttons')
Lie2Buttons.add_translation("Command",
                            ('Button1Press', 5401),
                            ('Button2Press', 5402))

StealthSensor = mynetwork.add_node(MoteinoIDs['StealthSensor'],
                                   MoteinoStructs['StealthSensor'],
                                   'StealthSensor')
StealthSensor.add_translation("Command",
                              ('Triggered', 6301),
                              ('MonitorTrigger', 6302),
                              ('StopMonitoring', 6303))


def StealthRec(d):
    if d['Command'] == 'Triggered':
        print "Slave {} Triggered".format(d['Tripped'])
        Sirens.send("TogglePin1")
    else:
        print "Stealth said: " + str(d)


def moteino_status(device):
    d = mynetwork.send_and_receive(device, Command="Status")
    
    print("{} Received from {}".format(d, device))
    if not d:
        return "No response from {}".format(device)
    sender = d["Sender"].Name
    if sender != device:
        return "Wrong sender: " + sender + ", expected: " + device
    ret = ""

    if device == "Elevator":
        ret += "Elevator up and running, passcode is: {}".format(d['PassCode1'])

    elif device == "GreenDude":
        passcode = str(d['Lights']).replace('255', 'Red').replace('0', 'Black').replace('1', 'Yellow')
        
        ret += "GreenDude is up and running, currently showing: {}".format(passcode)
    elif device == "SplitFlap":
        letters = d['Letters'].replace('\x00', ' ') # sendir ekki til baka hvad hann er ad birta
        ret += "SplitFlap is up and running"
    elif device == "ShootingRange":
        lights = str(d['Colors']).replace('-1', "Red").replace('0', 'off').replace('1', 'Green')
        ret += "ShootingRange is up and running, current colors: {}".format(lights)
    elif device == "LockPicking":
        pickorder = str(d['PickOrder'])
        ret += "LockPicking is up and running, current pick order: {}".format(pickorder)
    elif device == "Stealth":
        tripped = d["Tripped"]
        if tripped == 0:
            ret += "Stealth is up and running, all lasers working {}".format(d["Sequence"][:6])
        elif 10 < tripped < 20:
            ret = "Stealth: Slave {} is not answering over i2c".format(tripped-10)
        else:
            ret += "Stealth: slave{} is tripping {}".format(tripped, d["Sequence"][:6])
    elif device == "StealthSensor":
        if d["Trigger"]:
            ret = "Stealth Sensor is triggering"
        else:
            ret = "Stealth Sensor is not triggering"
    else:
        ret += device + " is up and running"


    # ret += str(d)

    if 'RSSI' in d:
        ret += "   RSSI: {}".format(d['RSSI'])
        
    return ret


Stealth.bind(receive=StealthRec)


def test(d, n, **kwargs):
    ret = 0
    for i in range(n):
        ret += int(d.send(0, **kwargs))
    print "{} successfull out of {}     ({:.1%})".format(ret, i+1, ret/float(i+1))
    return ret


if __name__ == '__main__':
    mynetwork.shut_down()