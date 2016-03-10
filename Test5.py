
from MoteinoBeta import MoteinoNetwork
from Dictionaries import *


class MyNetwork(MoteinoNetwork):
    def __init__(self):
        MoteinoNetwork.__init__(self, port='COM50', baudrate=9600)

    def receive(self, diction):
        print "we got: " + str(diction)


if __name__ == "__main__":
    mynetwork = MyNetwork()

    mynetwork.add_device('GreenDude', 11,   "unsigned int Command;" +
                                            "byte Lights[7];" +
                                            "byte Temperature;")
    mynetwork.add_device('TestDevice', 10, "char stafir[10];"
                                           "int tolur[5];")

    mynetwork.print_when_acks_recieved = True

    # mynetwork.send('GreenDude', {'Command': 99,
    #                              'Lights': [1, 2, 3, 4, 5],
    #                              'Temperature': 37})
    response = mynetwork.send_and_recieve('TestDevice', {})
    print response
