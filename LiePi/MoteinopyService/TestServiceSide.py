import threading
import time
import socket
import json
import logging
# from moteinopy import MoteinoNetwork


PORT = 16485
logging.basicConfig()

# if __name__ == '__main__':
#     sys.stderr = open("/home/pi/logs/MoteinoService_err.txt", 'a+')


class MoteinoClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ConnectionActive = None
        self.socket = socket.socket()
        self.logger = logging.getLogger("MoteinoClient")
        self.logger.setLevel(logging.DEBUG)
        self.WriteLock = threading.Lock()

        self.on_connection_lost = None
        self.on_connection_made = None
        self.on_received = None

        # self.Network = MoteinoNetwork("/dev/ttyUSB0", base_id=53, init_base=False)  # breyta ID
        # self.Pope = self.Network.add_node(1, "int Command;", "DaPope")
        # self.Pope.add_translation("Command",
        #                           ("Status", 99),
        #                           ("Reset", 98),
        #                           ("Start", 50))
        #
        # def pope_receive(d):
        #     if d['Command'] == "Status":
        #         self.Pope.send("Status")
        #     if d['Command'] == "Reset":
        #         self.cmd_reset()
        #     if d['Command'] == "Start":
        #         self.cmd_start()
        #
        # self.Pope.bind(receive=pope_receive)

        self.start()

    def cmd_start(self):
        self.logger.debug("ligths on!")
        self.write({"Command": "Start"})

    def cmd_reset(self):
        self.logger.debug("ligths off!")
        self.write({"Command": "Reset"})

    def run(self):
        self.logger.debug("Started")
        while True:
            if not self.ConnectionActive:
                self.connect()
            time.sleep(0.5)

    def write(self, msg):
        self.logger.debug("Writing: {}".format(msg))
        with self.WriteLock:
            if self.ConnectionActive:
                try:
                    self.socket.send(json.dumps(msg))
                except socket.error:
                    self.connection_lost()

    def receive(self, msg):
        self.logger.debug("Received: {}".format(msg))
        if self.on_received is not None:
            self.on_received(json.loads(msg))

    def connection_made(self):
        self.logger.debug("Connection made!")
        self.ConnectionActive = True
        if self.on_connection_made is not None:
            self.on_connection_made()

    def connection_lost(self):
        self.logger.debug("Connection lost!")
        self.ConnectionActive = False
        if self.on_connection_lost is not None:
            self.on_connection_lost()

    def connect(self):
        self.logger.debug("Connecting to LightServer...")
        if not self.ConnectionActive:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect(('localhost', PORT))
            except socket.error as e:
                self.logger.debug(e)
                return
            self.connection_made()
        else:
            self.logger.debug("\tConnection already active.")


if __name__ == '__main__':
    Client = MoteinoClient()


