from ArduinoReader import Arduino

if __name__ == '__main__':
    import time
    arduino = Arduino("COM50", baudrate=38400)

    def f1():
        print "f1 was just run"

    arduino.bind_button1(rising=f1)

    while True:
        time.sleep(1)
        print "Slider: {}".format(arduino.SliderState)
