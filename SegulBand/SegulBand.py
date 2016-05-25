import RPi.GPIO as GPIO
from arduino import Motor
import atexit

motor = Motor()


# States:
#       Begin / Entrance to room
#
# region Play Button
play_button_pin = 5


def play_button_press():
    print "Play was pressed"
    motor.play()

GPIO.setup(play_button_pin, GPIO.IN)
GPIO.add_event_detect(play_button_pin, GPIO.FALLING, callback=play_button_press, bouncetime=300)
# endregion


# region stop Button
stop_button_pin = 6


def stop_button_press():
    print "stop was pressed"
    motor.stop()

GPIO.setup(stop_button_pin, GPIO.IN)
GPIO.add_event_detect(stop_button_pin, GPIO.FALLING, callback=stop_button_press, bouncetime=300)
# endregion


# region reverse Button
reverse_button_pin = 13


def reverse_button_press():
    print "reverse was pressed"
    motor.rewind()

GPIO.setup(reverse_button_pin, GPIO.IN)
GPIO.add_event_detect(reverse_button_pin, GPIO.FALLING, callback=reverse_button_press, bouncetime=300)
# endregion


# region forward Button
forward_button_pin = 19


def forward_button_press():
    print "forward was pressed"
    motor.forward()

GPIO.setup(forward_button_pin, GPIO.IN)
GPIO.add_event_detect(forward_button_pin, GPIO.FALLING, callback=forward_button_press, bouncetime=300)
# endregion


atexit.register(GPIO.cleanup)
