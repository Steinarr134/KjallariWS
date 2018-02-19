import SocketServer
import socket
import json
import threading

PORT = 16485


class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        while True:
            try:
                data = self.request.recv(1024)
            except socket.error:
                return
            if not data:
                return
            # print data
            data = json.loads(data)

            if "Command" not in data:
                self.request.send(json.dumps("Must contain 'Command'"))
                return
            if data['Command'] == "Start":
                # start_event = Event(StartEventType)
                # pygame.fastevent.post(start_event)
                print "Do START!"
            elif data['Command'] == "Reset":
                # stop_event = Event(StopEventType)
                # pygame.fastevent.post(stop_event)
                print "Do RESET!"


class Server(SocketServer.TCPServer):
    def __init__(self):
        address = ("localhost", PORT)
        self.allow_reuse_address = True
        SocketServer.TCPServer.__init__(self, address, RequestHandler)

        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.setDaemon(True)
        self.thread.start()

MoteinoServer = Server()

raw_input("press enter to exit")
