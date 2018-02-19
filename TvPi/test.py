import subprocess
import pygame
import time
from moteinopy import MoteinoNetwork
import sys
import logging
import threading


logging.basicConfig(level=logging.DEBUG)

videofolder = "/home/pi/usbdrv/"


PLAYEVENT = pygame.USEREVENT + 1
def handle_command(stuff):
    logging.info("command received: " + str(stuff))
    if type(stuff) != dict:
        stuff = dict(stuff)
    if stuff['Command'] == "Play":
        print "putting in play event"
        play_event = pygame.fastevent.Event(PLAYEVENT,
                                        message=videofolder + stuff['What2Play'].rstrip('\0').strip())
        pygame.fastevent.post(play_event)
    elif stuff["Command"] == "Status":
        Pope.send("Status")

mynetwork = MoteinoNetwork("/dev/ttyUSB0", base_id=41, init_base=False, baudrate=38400)
Pope = mynetwork.add_node(1, "int Command;char What2Play[10];", "Pope")
Pope.add_translation("Command",
                     ('Play', 4101),
                     ('Status', 99))


class PopenThread(threading.Thread):
    def __init__(self, command):
        threading.Thread.__init__(self)
        self.Command = command
        self.Running = None
        self.start()
        self.Done = False

    def run(self):
        self.Running = subprocess.Popen(self.Command.split(" "), stdin=subprocess.PIPE)
        

    def die(self):
        self.Running.stdin.write('q')
        self.Running.kill()
        self.Done = True

def doit():
    t1 = PopenThread("omxplayer /home/pi/usbdrv/B1.mov")
    print t1.Done
    time.sleep(5)
    t1.die()
    print t1.Done
    time.sleep(0.5)
    print t1.Done

