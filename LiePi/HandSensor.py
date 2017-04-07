import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO
import sys, time, atexit, threading


class HandSensor:

    IRQ_PIN = 4 
    ADDR_PIN = 17
    sensor = None
    MAX_EVENT_WAIT_SECONDS = 0.5
    EVENT_WAIT_SLEEP_SECONDS = 0.1
    handLastFound = 0.0
    handLastNotFound = 5.0
    MAX_TIME_BETWEEN_HANDS = 0.3
    handPresent = True
    lying = False

    def __init__(self):
        self.sensor = MPR121.MPR121()
        if not self.sensor.begin():
            print("Could not begin MPR121 sensor")
            sys.exit(0)
            # needs proper error handling
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.IRQ_PIN, GPIO.FALLING)
        atexit.register(GPIO.cleanup)
        # Clear any pending interrupts by reading touch state.
        self.sensor.touched()

    def init(self):
        self.isRunning = True
        threading.Thread(target=self.sense, name="_handsensor_").start()

    def sense(self):
        while self.isRunning:
            # Wait for the IRQ pin to drop or too much time ellapses (to help prevent
            # missing an IRQ event and waiting forever).
            start = time.time()
            while (time.time() - start) < self.MAX_EVENT_WAIT_SECONDS and not GPIO.event_detected(self.IRQ_PIN):
                time.sleep(self.EVENT_WAIT_SLEEP_SECONDS)
            # Read touch state.
            sensorVector = self.sensor.touched()
            self.lying = sensorVector%2 == 1
            sensorVector = [1 for i in bin(sensorVector) if i=='1']
            handPresent = sum(sensorVector) >= 3
            if handPresent:
                self.handLastFound = time.time()
            if not handPresent:
                self.handLastNotFound = time.time()
            self.handPresent = not (self.handLastNotFound - self.handLastFound > self.MAX_TIME_BETWEEN_HANDS)

    def isPresent(self):
        return self.handPresent, self.lying

    def close(self):
        isRunning = False


