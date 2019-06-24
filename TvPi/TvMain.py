import subprocess
import pygame
import time
import sys
sys.path.append("/home/pi/moteinopy")
from moteinopy import MoteinoNetwork
import logging
import threading

logging.basicConfig(level=logging.DEBUG)

# sys.stderr=open("/home/pi/logs/" + time.strftime("%c") + ".txt", 'w+')

videofolder = "/home/pi/usbdrv/"


PLAYEVENT = pygame.USEREVENT + 1
RESETEVENT = pygame.USEREVENT + 2


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
    elif stuff["Command"] == "Reset":
        reset_event = pygame.fastevent.Event(RESETEVENT)
        pygame.fastevent.post(reset_event)

print "starting network"
mynetwork = MoteinoNetwork("/dev/ttyUSB0", base_id=41, init_base=False, baudrate=38400)
mynetwork.logger.setLevel(logging.DEBUG)
Pope = mynetwork.add_node(1, "int Command;char What2Play[10];", "Pope")
Pope.add_translation("Command",
                     ('Play', 4101),
                     ('Status', 99),
                     ("Reset", 98))
Pope.bind(receive=handle_command)

pygame.init()
pygame.fastevent.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# screen = pygame.display.set_mode((500, 500))

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
	if self.Running is None:
	    return
        if self.Running.poll() is None:
            #print "Killing myself #######################"
            self.Running.stdin.write('q')
            time.sleep(0.1)
        else:
            #print "444444444444444444 I'm already dead, bith!"
            pass
        self.Done = True


Threads = []

done = False
while not done:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        break
    t2remove = []
    for thread in Threads:
        if thread.Done:
            t2remove.append(thread)
    for thread in reversed(t2remove):
        #print "================= removing thread"
        Threads.remove(thread)
    for event in pygame.fastevent.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        elif event.type == RESETEVENT:
            for thread in Threads:
                thread.die()
        elif event.type == PLAYEVENT:
            for thread in Threads:
                thread.die()
            #print("---------------------Play event, doing: " + "omxplayer " + event.message)
            Threads.append(PopenThread("omxplayer " + event.message + " -o local --win 0,0,720,440"))
        


pygame.quit()
logging.debug("End of script")
