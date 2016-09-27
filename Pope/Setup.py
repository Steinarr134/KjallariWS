
from Config import mynetwork, GreenDude, SplitFlap, LockPicking, Morser, TimeBomb
from DoorControl import Door, DoorController as Dctrl

DoorController = Dctrl("Com50")
ElevatorDoor = Door(DoorController)
SafeDoor = Door(DoorController)


