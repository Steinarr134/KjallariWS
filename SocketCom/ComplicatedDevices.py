from SocketCom import Client, Server
import threading
import random
import json
import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def ascii_encode_dict(data):
    ascii_encode = lambda x: x.encode('ascii') if type(x) is not int else x
    return dict(map(ascii_encode, pair) for pair in data.items())


class ComplicatedClient(object):
    def __init__(self, ip, port, arglist=["Command"]):
        assert "_ReturnPort_" not in arglist
        assert "_ReturnIP_" not in arglist
        self.ReturnPort = port+random.randint(1, 1000)
        self.ReturnServer = Server(self._rec, self.ReturnPort, ip=get_ip())
        self.Client = Client(port, ip)
        self.arglist = arglist
        self.ReceiveWithSendAndReceive = False
        self.SendAndReceiveEvent = threading.Event()
        self.ReceiveFunc = None
        self.StuffReceived = None
        self.max_wait = 0.5

        self.Client.send(json.dumps({"_ReturnPort_":self.ReturnPort,
                                     "_ReturnIP_": get_ip()}))

    def bind(self, receive=None):
        self.ReceiveFunc = receive

    def _receive_func(self, stuff):
        if self.ReceiveFunc is not None:
            self.ReceiveFunc(stuff)
        else:
            print "ComplicatedClient received: ", stuff

    def _rec(self, stuff):
        if self.ReceiveWithSendAndReceive:
            self.StuffReceived = str(stuff)
            self.SendAndReceiveEvent.set()
        else:
            self._receive_func(stuff)

    def send(self, *args, **kwargs):
        tosend = {}
        for i, arg in enumerate(args):
            tosend[self.arglist[i]] = arg
        for (kw, kwarg) in kwargs.items():
            tosend[kw] = kwarg

        self.Client.send(json.dumps(tosend))

    def send_and_receive(self, *args, **kwargs):
        self.send(*args, **kwargs)
        self.ReceiveWithSendAndReceive = True
        self.SendAndReceiveEvent.clear()
        self.SendAndReceiveEvent.wait(self.max_wait)
        self.ReceiveWithSendAndReceive = False
        received = str(self.StuffReceived)
        return json.loads(received, object_hook=ascii_encode_dict)


class ComplicatedServer(object):
    def __init__(self, port, arglist=["Command"]):
        self.Server = Server(self._handle, port, ip=get_ip())
        self.handle_shit = None
        self.arglist = arglist
        self.ReturnClient = None
        self.ReturnClientPort = None
        self.ReturnClientIP = None

    def _setup_return(self, d):
        # print "setupReturn"
        self.ReturnClientPort = d["_ReturnPort_"]
        self.ReturnClientIP = d["_ReturnIP_"]
        self.ReturnClient = Client(self.ReturnClientPort, self.ReturnClientIP)

    def bind(self, receive=None):
        self.handle_shit = receive

    def send(self, *args, **kwargs):
        if self.ReturnClient:
            tosend = {}
            for i, arg in enumerate(args):
                tosend[self.arglist[i]] = arg
            for (kw, kwarg) in kwargs.items():
                tosend[kw] = kwarg

            self.ReturnClient.send(json.dumps(tosend))

    def _handle(self, stuff):
        try:
	    print stuff
            d = json.loads(stuff, object_hook=ascii_encode_dict)
            # print "d=", d
            if "_ReturnPort_" in d:
                self._setup_return(d)
                return
        except (ValueError, TypeError):
            pass
        self.handle_shit(json.loads(stuff, object_hook=ascii_encode_dict))


if __name__ == '__main__':

    s = ComplicatedServer(12345)
    c = ComplicatedClient("localhost", 12345)

    def h(ble):
        print "received:  " + str(ble)
        if ble["Command"] == "hello there":
            s.send("hi")
    s.bind(h)

    def ch(bla):
        print "ClientReceived: " + str(bla)
    c.bind(ch)

    import time
    time.sleep(1)
    c.send("hello")
    time.sleep(1)
    c.send("hello there")
    time.sleep(5)
