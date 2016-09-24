# import pygame
#
#
# "C:\Users\SteinarrHrafn\Google Drive\Kjallari William Stephenssonar\Camp Z\Lygamælir\Tape_ogg\\1_audio_WELCOME_INTRODUCTION"


import DoorControl

DoorController = DoorControl.DoorController('COM50')

ElevatorDoor = DoorControl.Door(DoorController)
BlaBlaDoor = DoorControl.Door(DoorController)


ElevatorDoor.open()
BlaBlaDoor.close()

DoorController.open_all()


