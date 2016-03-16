
from MoteinoBeta import MoteinoNetwork
from Dictionaries import *
import time


class MyNetwork(MoteinoNetwork):
    def __init__(self):
        MoteinoNetwork.__init__(self, port='COM10', baudrate=115200)

    def receive(self, diction):
        print "we got: " + str(diction)


if __name__ == "__main__":
    mynetwork = MyNetwork()
    mynetwork.max_wait = 5000

    mynetwork.add_device('GreenDude', 11,   "unsigned int Command;" +
                                            "byte Lights[7];" +
                                            "byte Temperature;")
    mynetwork.add_device('TestDevice', 10, "char stafir[10];"
                                           "int tolur[5];")

    mynetwork.print_when_acks_recieved = True

    # mynetwork.send('GreenDude', {'Command': 99,
    #                              'Lights': [1, 2, 3, 4, 5],
    #                              'Temperature': 37})
    # mynetwork.send('GreenDude', {'Command': 122, 'Lights': [0, 0, 0, 0, 0, 0, 0]})

    mynetwork.send('GreenDude', {'Command': 99})
    raw_input("slkj")
    response = mynetwork.send_and_recieve('GreenDude', {'Command': 99})
    print response
