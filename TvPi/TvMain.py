import subprocess
import pygame
import time
from moteinopy import MoteinoNetwork
import sys
import logging
import threading

logging.basicConfig(level=logging.DEBUG)

# sys.stderr=open("/home/pi/logs/" + time.strftime("%c") + ".txt", 'w+')

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
Pope.bind(receive=handle_command)

pygame.init()
pygame.fastevent.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

screen.fill((0, 0, 0))


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

Threads = []

done = False
while not done:
    time.sleep(0.1)
    for thread in Threads:
        if thread.Done:
            Threads.remove(thread)

    for event in pygame.fastevent.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        elif event.type == PLAYEVENT:
            for thread in Threads:
                if not thread.Done:
                    thread.die()
            print("Play event, doing: " + "omxplayer " + event.message)
            Threads.append(PopenThread("omxplayer " + event.message))


pygame.quit()
logging.debug("End of script")
