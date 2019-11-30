import sys
sys.path.append("/home/campz/KjallariWS")
with open("/home/pope/itworks.txt" , "w+") as f:
    f.write("title")


from SocketCom import Server, Client
import serial
import threading
import json
import time
from Arduino8RelayControl import DoorController


class SerialHandler(object):
    """
    One Way serial parser (from Socket to Serial)
    """
    def __init__(self):
        self.Serial = None
        self.SerialWriteLock = threading.Lock()

    def aquire_serial(self, port):
        if self.Serial is None:
            with self.SerialWriteLock:
                self.Serial = serial.Serial(port, 115200)

    def _write(self, stuff):
        if self.Serial is None:
            print "Problemo!! asked to write but don't have serial port"
            return
        with self.SerialWriteLock:
            print "writing {} to serial".format(stuff.encode('ascii'))
            self.Serial.write(stuff.encode('ascii') +"\n")

    def handle(self, msg):
        print "DoorSerial msg: '" + msg + "'"
        msg = json.loads(msg)
        if not "Command" in msg:
            return
        if msg["Command"] == "Connect":
            self.aquire_serial(msg["Port"])
        elif msg["Command"] == "Write":
            self._write(msg["Stuff"])


class SocketDoorController(DoorController):
    SocketPort = 3011

    def _aquire_serial(self, serial_port):
        self.Serial = Client(self.SocketPort)
        self.Serial.send(json.dumps({"Command": "Connect", "Port": serial_port}))

    def _fs(self, s):
        self.Serial.send(json.dumps({"Command": "Write", "Stuff": s}))

    def _send(self):
        s = ''
        for door in self.Doors:
            s += str(door.State)

        print "(socket)Sending: {}".format(s)
        self.Serial.send(json.dumps({"Command": "Write", "Stuff": s}))


if __name__ == '__main__':
    handler = SerialHandler()
    server = Server(handler.handle, 3011)

    print "serving forever..."

    def fun():
        while True:
            time.sleep(1)
            with open("/home/pope/itworks.txt", "a+") as f:
                f.write("{}\n".format(time.time()))

    tlkjt = threading.Thread(target=fun)
    tlkjt.start()

    # t = threading.Thread(target=server.serve_forever())
    # t.start()
    time.sleep(10)
    # quit()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print "shutting down"
    server.shutdown()
    quit()
