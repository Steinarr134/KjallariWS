import SocketServer
import json
import socket
import threading

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(name)s: %(message)s',
#                     )

PORT = 3010


class Server(SocketServer.TCPServer):
    def __init__(self, handle_shit, port=PORT, ip="localhost"):

        class RequestHandler(SocketServer.BaseRequestHandler):
            def handle(self):
                while True: # allows for more then 1 message through 1 connection
                    try:
                        data = self.request.recv(1024)
                    except socket.error:
                        return
                    if not data:
                        return
                    # print data
                    handle_shit(data.strip())

        address = (ip, port)
        SocketServer.TCPServer.__init__(self, address, RequestHandler)

        self.Thread = threading.Thread(target=self.serve_forever)
        self.Thread.setDaemon(True)
        self.Thread.start()

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class Client(object):
    def __init__(self, port, ip="localhost"):
        self.s = socket.socket()
        self.port = port
        self.ip = ip

    def send(self, shit):
        try:
            self.s.send(str(shit))
        except socket.error:
            try:
                self._connect()
                self.s.send(str(shit))
            except socket.error as e:
                print "had a problem: " + str(e)
                return

    def _connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))


if __name__ == '__main__':
    import time
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # address = (socket.gethostname(), 3010)
    # address = ("10.75.53.170", 3010)
    address = ("", 3010)
    ip_adress, port = address

    def bla(message):
        logger = logging.getLogger("client")
        logger.info('Server on %s:%s', ip_adress, port)

        # Connect to the server
        logger.debug('creating socket')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug('connecting to server')
        s.connect((ip_adress, port))

        # Send the data
        logger.debug('sending data: "%s"', message)
        len_sent = s.send(message)

        # Receive a response
        logger.debug('waiting for response')
        response = s.recv(1024)
        logger.debug('response from server: "%s"', response)

        # Clean up
        logger.debug('closing socket')
        s.close()
        logger.debug('done')


    def h(data):
        print "received: " + str(data)

    server = Server(h, PORT)

    client = Client(PORT)

    time.sleep(1)
    client.send("Hello there")
    time.sleep(1)
    client.send("Hello some more")
    time.sleep(3)
    print "...shutting down..."
    # server.shutdown()
    print "goodbye"