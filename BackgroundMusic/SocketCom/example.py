from SocketCommunication import Server


def handle(data):
    if data == "checkpoint 1":
        print "checkpoint 1 reached"
        # raise proper event
    elif data == "Stealth Activated":
        print "You get the idea"


server = Server(handle)

