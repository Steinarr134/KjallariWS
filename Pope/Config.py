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
    'Morser',
    'Stealth',
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


MaxPlayingTime = 60*60*1.5  # an hour and a half
