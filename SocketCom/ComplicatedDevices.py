from SocketCom import Client, Server
import threading
import json


class ComplicatedClient(object):
    def __init__(self, ip, port, arglist=["Command"]):
        assert "_ReturnPort_" not in arglist
        assert "_ReturnIP_" not in arglist
        self.ReturnPort = port+10
        self.ReturnServer = Server(self._rec, self.ReturnPort)
        self.Client = Client(port, ip)
        self.arglist = arglist
        self.ReceiveWithSendAndReceive = False
        self.SendAndReceiveEvent = threading.Event()
        self.ReceiveFunc = None
        self.StuffReceived = None
        self.max_wait = 0.5

        self.Client.send(json.dumps({"_ReturnPort_":self.ReturnPort,
                                     "_ReturnIP_": "localhost"}))

    def bind(self, receive=None):
        self.ReceiveFunc = receive

    def _receive_func(self, stuff):
        if self.ReceiveFunc is not None:
            self.ReceiveFunc(stuff)

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
        return json.loads(received)


class ComplicatedServer(object):
    def __init__(self, port, arglist=["Command"]):
        self.Server = Server(self._handle, port)
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

    def send(self, stuff):
        # print "ServerSend"
        if self.ReturnClient:
            self.ReturnClient.send(json.dumps(stuff))

    def _handle(self, stuff):
        try:
            d = json.loads(stuff)
            # print "d=", d
            if "_ReturnPort_" in d:
                self._setup_return(d)
                return
        except (ValueError, TypeError):
            pass
        self.handle_shit(json.loads(stuff))


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
