Devices = [
    'SplitFlap',
    'Elevator',
    'TapeRecorder',
    'LockPicking',
    'GreenDude',
    'LiePiA',
    'LiePiB',
    'LieButtons',
    'Lie2Buttons',
    'TvPi',
    'WineBoxHolder',
    'WineBox',
    'ShootingRange',
    'Sirens',
    'Morser',
    'Stealth',
    'StealthSensor',
    'TimeBomb',
]

DeviceSubmenus = []


class Object(object):
    pass        # I do realize this seems pointless but it actually does something


def cumsum(l):
    new_l = []
    s = 0
    for number in l:
        s += number
        new_l.append(s)
    return new_l


# MaxPlayingTime = 60*60*1  # an hour
MaxPlayingTime = 60*60

MinBombTime = 3*60   # 3 minutes
MaxBombTime = 10*60  # 10 minutes

NofPlayers = 5

GreenDudeCorrectPassCode = [255, 1, 1, 255, 255, 1, 255]
LockPickCorrectPickOrder = [0, 1, 2, 3, 4, 5]
