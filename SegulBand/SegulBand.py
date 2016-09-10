import RPi.GPIO as GPIO
from arduino import Motor
import atexit
import time
from pygame import mixer
import threading

print "running..."
GPIO.setmode(GPIO.BCM)
atexit.register(GPIO.cleanup)

motor = Motor()

mixer.init()
m = mixer.music

CurrentFile = "C:\Users\SteinarrHrafn\Google Drive\Kjallari William Stephenssonar\Camp Z\Lygamælir\Tape_ogg\\1_audio_WELCOME_INTRODUCTION"
m.load(CurrentFile)
PosOffset = 0
FileLength = 50
ScrollSpeed = 2

last_press = None
last_press_time = None

HaveReleasedEvent = threading.Event()

class NoFinishFileThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(0.5)
            if m.get_pos() < 0:
                m.play(0, FileLength)
                m.pause()

noFinishFileThread = NoFinishFileThread()
noFinishFileThread.start()


def realpos():
    global PosOffset
    pos = m.get_pos()/float(1000)
    return pos - PosOffset


def until_end():
    return FileLength - realpos()


def skip(s):
    if s > until_end():
        print "to much of forward!!!"
    elif -s > realpos():
        print "too much rewind!!!"
    else:
        global PosOffset
        m.set_pos(realpos() + s)
        PosOffset -= s


def play():
    pass


def stop():
    pass


def forward():
    m.pause()
    global last_press_time
    last_press_time = time.time()
    global last_press
    last_press = 'forward'
    _until_end = until_end()
    HaveReleasedEvent.clear()
    if not HaveReleasedEvent.wait(_until_end/float(ScrollSpeed)):
        HaveReleasedEvent.set()
        skip(_until_end)


def rewind():
    m.pause()
    global last_press_time
    last_press_time = time.time()
    global last_press
    last_press = 'rewind'
    _until_end = until_end()
    HaveReleasedEvent.clear()
    if not HaveReleasedEvent.wait(_until_end/float(ScrollSpeed)):
        HaveReleasedEvent.set()
        skip(_until_end)


def release(channel):
    if not HaveReleasedEvent.is_set():
        HaveReleasedEvent.set()
        global last_press
        global last_press_time
        if last_press == 'forward':
            skip((time.time() - last_press_time)*ScrollSpeed)
        elif last_press == 'rewind':
            skip((last_press_time - time.time())*ScrollSpeed)
        else:
            print "noting last_press WTF!"

        m.unpause()
        last_press = None


# region stop Button
stop_button_pin = 6


def stop_button_press(channel):
    print "stop was pressed"
    stop()

GPIO.setup(stop_button_pin, GPIO.IN)
GPIO.add_event_detect(stop_button_pin, GPIO.FALLING, callback=stop_button_press, bouncetime=300)
# endregion


# region reverse Button
reverse_button_pin = 13


def reverse_button_press(channel):
    print "reverse was pressed"
    rewind()

GPIO.setup(reverse_button_pin, GPIO.IN)
GPIO.add_event_detect(reverse_button_pin, GPIO.FALLING, callback=reverse_button_press, bouncetime=300)
# endregion


# region forward Button
forward_button_pin = 19


def forward_button_press(channel):
    print "forward was pressed"
    forward()

GPIO.setup(forward_button_pin, GPIO.IN)
GPIO.add_event_detect(forward_button_pin, GPIO.FALLING, callback=forward_button_press, bouncetime=300)
# endregion

# region Play Button
play_button_pin = 5


def play_button_press(channel):
    print "Play was pressed"
    play()

GPIO.setup(play_button_pin, GPIO.IN)
GPIO.add_event_detect(play_button_pin, GPIO.FALLING, callback=play_button_press, bouncetime=300)
GPIO.add_event_detect(forward_button_pin, GPIO.RISING, callback=release, bouncetime=300)
GPIO.add_event_detect(reverse_button_pin, GPIO.RISING, callback=release, bouncetime=300)

# endregion

time.sleep(100)
