import os
import pygame
import time
from moteinopy import MoteinoNetwork
import sys
import logging

logging.basicConfig(level=logging.INFO)

sys.stderr=open("/home/pi/logs/" + time.strftime("%c") + ".txt", 'w+')

videofolder = "/home/pi/Videos/"


PLAYEVENT = pygame.USEREVENT + 1
def handle_command(stuff):
    logging.info("command received: " + str(stuff))
    if type(stuff) != dict:
        stuff = dict(stuff)
    if stuff['Command'] == "Play":
        print "putting in play event"
        play_event = pygame.event.Event(PLAYEVENT,
                                        message=videofolder + stuff['What2Play'].rstrip('\0').strip())
        pygame.event.post(play_event)
    elif stuff["Command"] == "Status":
        Pope.send("Status")

mynetwork = MoteinoNetwork("/dev/ttyUSB0", base_id=41, init_base=False)
Pope = mynetwork.add_node(1, "int Command;char What2Play[10];", "Pope")
Pope.add_translation("Command",
                     ('Play', 4101),
                     ('Status', 99))
Pope.bind(receive=handle_command)

pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

screen.fill((0, 0, 0))

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            elif event.key == pygame.K_a:
                os.popen("omxplayer small.mp4")
        elif event.type == PLAYEVENT:
            print("Play event, doing: " + "omxplayer " + event.message)
            os.popen("omxplayer " + event.message)

pygame.quit()
logging.debug("End of script")
