#!/usr/bin/env python



import sys
import time
#sys.stderr = open("/home/pi/logs/" + str(time.time())+"_errrrr.txt", "w+")
import RPi.GPIO as GPIO
from arduino import Motor
import atexit
from pygame import mixer
import threading
from moteinopy import MoteinoNetwork
import demjson
import os
import logging
logging.basicConfig(level=logging.DEBUG)

print "imports done..."

GPIO.setmode(GPIO.BCM)
atexit.register(GPIO.cleanup)

motor = Motor()

mixer.init()
m = mixer.music
m.set_volume(0.5)

class File(object):
    def __init__(self):
        self.FileName = None
        self.PosOffset = 0
        self.FileLength = 10

f = File()
global StupidState
StupidState = True
ScrollSpeed = 4
last_press = None
last_press_time = None
something_is_being_pressed = False
playing_active = False
time.sleep(1)
motor.set_lights(35)
SomethingIsLoaded = False

HaveReleasedEvent = threading.Event()

def file_over():
    return abs(f.FileLength - realpos()) < 0.5 and SomethingIsLoaded

class NoFinishFileThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(0.1)
            if file_over() and playing_active:
                logging.debug("NoFinishThread intervening")
                # m.play(0, f.FileLength-0.5)
                stop()

noFinishFileThread = NoFinishFileThread()
noFinishFileThread.start()

def realpos():
    pos = m.get_pos()/float(1000)
    return pos - f.PosOffset


def until_end():
    return f.FileLength - realpos()


def skip(s):
    if SomethingIsLoaded:
        if s > until_end():
            logging.warning("to much of forward!!!")
        elif -s > realpos():
            logging.warning("too much rewind!!!")
        else:
            m.set_pos(realpos() + s)
            f.PosOffset -= s


def play():
    if StupidState:
        motor.play()
        return
    if file_over():
        return
    global playing_active
    playing_active = True
    logging.debug("play - realpos:{}".format(realpos()))
    m.unpause()
    motor.play()


def stop():
    m.pause()
    global playing_active
    playing_active = False
    motor.stop()


def forward():
    if StupidState:
        motor.forward()
        return
    if file_over():
        return
    m.pause()
    global last_press_time
    last_press_time = time.time()
    global last_press
    last_press = 'forward'
    global something_is_being_pressed
    if something_is_being_pressed:
        return
    else:
        something_is_being_pressed = True
    _until_end = until_end()
    print "until end: " + str(_until_end)
    motor.forward()
    HaveReleasedEvent.clear()
    print "waiting for release event"
    if not HaveReleasedEvent.wait(_until_end/float(ScrollSpeed)):
        print "Event.wait timeout occured"
        HaveReleasedEvent.set()
        skip(_until_end)
        stop()
    else:
        print "waiting ended"

def rewind():
    if StupidState:
        motor.rewind()
        return
    if not SomethingIsLoaded:
        return
    m.pause()
    global last_press_time
    last_press_time = time.time()
    global last_press
    last_press = 'rewind'
    global something_is_being_pressed
    if something_is_being_pressed:
        return
    else:
        something_is_being_pressed = True

    if f.FileName.split('/')[-1] == "1.ogg":
        _until_beginning = realpos() - 37
    else:
        _until_beginning = realpos()
    motor.rewind()
    HaveReleasedEvent.clear()
    print "waiting for release event"
    if not HaveReleasedEvent.wait(_until_beginning/float(ScrollSpeed)):
        print "Event.wait timeout occured"
        HaveReleasedEvent.set()
        skip(-_until_beginning)
        motor.stop()
    else:
        print "waiting ended"

def release():
    if StupidState:
        return
    global something_is_being_pressed
    something_is_being_pressed = False
    print "release()"
    if not HaveReleasedEvent.is_set():
        HaveReleasedEvent.set()
        global last_press
        global last_press_time
        if last_press == 'forward':
            print"skipping forward"
            skip((time.time() - last_press_time)*ScrollSpeed)
        elif last_press == 'rewind':
            print "skipping backwards"
            skip((last_press_time - time.time())*ScrollSpeed)
        else:
            print "noting last_press WTF!"

        # m.unpause()
        last_press = None
    if playing_active:
        play()
    else:
        stop()

# region stop Button
stop_button_pin = 13

def stop_button_press(channel):
    print "stop was pressed"
    stop()

GPIO.setup(stop_button_pin, GPIO.IN)
GPIO.add_event_detect(stop_button_pin,
                      GPIO.FALLING,
                      callback=stop_button_press,
                      bouncetime=100)
# endregion


class ExecutionThread(threading.Thread):
    def __init__(self, fun):
        threading.Thread.__init__(self)
        self.fun = fun
        
    def run(self):
        self.fun()

# region reverse Button
reverse_button_pin = 6

def reverse_button_press(channel):
    time.sleep(0.05)
    if not GPIO.input(reverse_button_pin):
        # rising edge
        print "reverse was pressed"
        e = ExecutionThread(rewind)
        e.start()
    else:
        # falling edge
        print "reverse was depressed"
        e = ExecutionThread(release)
        e.start()
        
GPIO.setup(reverse_button_pin, GPIO.IN)
GPIO.add_event_detect(reverse_button_pin,
                      GPIO.BOTH,
                      callback=reverse_button_press,
                      bouncetime=100)
# endregion


# region forward Button
forward_button_pin = 5


def forward_button_press(channel):
    time.sleep(0.05)
    if not GPIO.input(forward_button_pin):
        # rising edge
        print "forward was pressed"
        e = ExecutionThread(forward)
        e.start()
    else:
        # falling edge
        print "forward was depressed"
        e = ExecutionThread(release)
        e.start()
        
GPIO.setup(forward_button_pin, GPIO.IN)
GPIO.add_event_detect(forward_button_pin,
                      GPIO.BOTH,
                      callback=forward_button_press,
                      bouncetime=100)
# endregion

# region Play Button
play_button_pin = 19


def play_button_press(channel):
    print "Play was pressed"
    play()

GPIO.setup(play_button_pin, GPIO.IN)
GPIO.add_event_detect(play_button_pin,
                      GPIO.FALLING,
                      callback=play_button_press,
                      bouncetime=100)
##GPIO.add_event_detect(forward_button_pin, GPIO.RISING, callback=release, bouncetime=300)
##GPIO.add_event_detect(reverse_button_pin, GPIO.RISING, callback=release, bouncetime=300)

# endregion

def load(filename, filelength, start_pos):
    f.FileName = filename
    f.PosOffset = 0
    f.FileLength = float(filelength)-0.5
    m.load(f.FileName)
    m.play()
    m.pause()
    global SomethingIsLoaded
    SomethingIsLoaded = True
    skip(start_pos)

def handle_command(stuff):
    logging.debug("handle_command received: " + str(stuff) + " (" + str(type(stuff)) + ")")
    if type(stuff) != dict:
        stuff = dict(stuff)
    if stuff['Command'] == "Load":
        global StupidState
        StupidState = False
        print "loading: " + stuff['s'].strip("\0")
        load(filename="/home/pi/audio_files/" + stuff['s'].strip("\0").strip(),
             filelength=stuff['FileLength'],
             start_pos=stuff["StartPos"]/10.0)
        if stuff['s'].strip("\0").strip()[0] == "1":
            motor.set_current_pos_as_zero()
        elif stuff['s'].strip():
            play()
    elif stuff['Command'] == "Play":
        play()
    elif stuff['Command'] == "Pause":
        stop()
    elif stuff['Command'] == "Forward":
        forward()
    elif stuff['Command'] == "Rewind":
        rewind()
    elif stuff['Command'] == "ShutDown":
        os.system("sudo shutdown -h now")
    elif stuff['Command'] == "Reboot":
        os.system("sudo reboot")
    elif stuff['Command'] == "SetLights":
        motor.set_lights(stuff['value'])
    elif stuff['Command'] == "Status":
        Pope.send("Status")
    elif stuff['Command'] == "Reset":
        motor.return2zero()
        global StupidState
        StupidState = True
    elif stuff['Command'] == "SetCurrentPosAsZero":
        motor.set_current_pos_as_zero()
    elif stuff['Command'] == "SetStupidState":
        global StupidState
        StupidState = True
    else:
        logging.warning("did not understand command: " + str(stuff))

print "setting up moteinos"

if motor.Port == "/dev/ttyUSB0":
    Moteinos = MoteinoNetwork("/dev/ttyUSB1", base_id=42, baudrate=38400)
else:
    Moteinos = MoteinoNetwork("/dev/ttyUSB0", base_id=42, baudrate=38400)

Pope = Moteinos.add_node(1, "int Command;char s[10];int FileLength;int LightValue;int StartPos", "Pope")
Pope.bind(receive=handle_command)
Pope.add_translation("Command",
    ("Play", 4201),
    ("Pause", 4202),
    ("Forward", 4207),
    ("Rewind", 4208),
    ("ShutDown", 4203),
    ("Reboot", 4204),
    ("Setlights", 4205),
    ("Load", 4206),
    ("Status", 99),
    ("Reset", 98),
    ("SetCurrentPosAsZero", 4209),
    ("SetStupidState", 4210))

motor.set_params(3000, 800, 2200)


while True:
    time.sleep(100)
    
    # inn = raw_input("dfsadfhlkjkjjjTHESTUFFFFFFFFFF\n")
    # motor.set_params(*(int(s.strip()) for s in inn.strip().split(',')))
    
    # logging.debug(time.time())
