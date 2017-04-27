import os
import pygame
import time
from RasPiCommunication import Receiver


PLAYEVENT = pygame.USEREVENT + 1
def handle_command(stuff):
    if type(stuff) != dict:
        stuff = dict(stuff)
    if stuff['Command'] == "play":
        play_event = pygame.event.Event(PLAYEVENT, message=stuff['What2Play'])
        pygame.event.post(play_event)
    else:
        print "command received: " + str(stuff)


rec = Receiver()
rec.bind(handle_command, ('192.168.1.91', 1234))

pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

screen.fill((0, 0, 0))

done = False
while not done:
    for event in pygame.event.get():
        print "loop"
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            elif event.key == pygame.K_a:
                os.popen("omxplayer small.mp4")
        elif event.type == PLAYEVENT:
            os.popen("omxplayer " + event.message)

pygame.quit()


print "sdfsdf"
