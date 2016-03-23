
from MoteinoBeta import MoteinoNetwork
from Dictionaries import *
import time

"""
This is a script intended to show the usage of the module called MoteinoBeta

"""


# We start by creating a our own subclass of the MoteinoNetwork. Let's
# call our class MyNetwork. Notice that you should only make 1 instance
# of this class.
class MyNetwork(MoteinoNetwork):
    def __init__(self):
        # Just like all good subclasses it starts by initializing the superclass.
        # Here we'll also pass on the Serial port info
        MoteinoNetwork.__init__(self, port='COM51', baudrate=115200)

    # Here you should start thinking about what you want to do with the network.
    # There are three functions that you might want to overwrite. Those are:
    # receive() - run if something is received from the network
    # ack()     - run if BaseGets an ack after sending something
    # no_ack()  - run if Base sends something but doesn't receive an ack
    #
    # Here are the functions as they look in the source code:

    def receive(self, sender, diction):
        """
        User should overwrite this function
        :param diction: dict
        """
        print "MoteinoNetwork received: " + str(diction) + "from" + sender.Name

    def no_ack(self, sender, last_sent_diction):
        """
        User might want to overwrite this function
        :param sender: str
        :param last_sent_diction: dict
        """
        print "Oh no! We didn't recieve an ACK from " + sender + " when we sent " + str(last_sent_diction)

    def ack(self, sender, last_sent_diction):
        """
        This funcion is totally unnecessary.... mostly for debugging but maybe
        it will be usefull someday to overwrite this with something
        :param sender: str
        :param last_sent_diction: dict
        """
        if self.print_when_acks_recieved:
            print "yay! " + sender + " responded with an ack when we sent: " + str(last_sent_diction)

# Now you might be wandering what those dictions are... diction is my made up name for python's
# dictionary or dict() datatype. But what do thes dictionaries contain you might ask.


if __name__ == "__main__":

    # First let's instantiate our network:
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

    print "sdlfkj"

    mynetwork.send('GreenDude', {'Command': 99})
    raw_input("slkj")
    response = mynetwork.send_and_recieve('GreenDude', {'Command': 99})
    print response
