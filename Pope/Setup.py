from Config import mynetwork, GreenDude, SplitFlap, LockPicking, Morser, TimeBomb
from DoorControl import Door as _Door, DoorController as Dctrl

DoorController = Dctrl("Com50")
ElevatorDoor = _Door(DoorController, 0)
SafeDoor = _Door(DoorController, 1)



