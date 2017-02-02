import socket
import threading
import select
import logging
import os
import time


class WaitableEvent:
    """
    Provides an abstract object that can be used to resume select loops with
    indefinite waits from another thread or process. This mimics the standard
    threading.Event interface.
    """

    def __init__(self):
        self._read_fd, self._write_fd = os.pipe()

    def wait(self, timeout=None):
        rfds, wfds, efds = select.select([self._read_fd], [], [], timeout)
        return self._read_fd in rfds

    def isSet(self):
        return self.wait(0)

    def clear(self):
        if self.isSet():
            os.read(self._read_fd, 1)

    def set(self):
        if not self.isSet():
            os.write(self._write_fd, b'1')

    def fileno(self):
        """
        Return the FD number of the read side of the pipe, allows this object to
        be used with select.select().
        """
        return self._read_fd

    def __del__(self):
        os.close(self._read_fd)
        os.close(self._write_fd)

StopEvent = WaitableEvent()
StopEvent.clear()


class SocketThread(threading.Thread):
    def __init__(self, client_con, react_fun):
        threading.Thread.__init__(self)
        self.React = react_fun
        self.ClientCon = client_con
        logging.debug("SocketThread started")
        self.start()

    def run(self):
        while not StopEvent.isSet():
            read, write, e = select.select([self.ClientCon, StopEvent], [], [])
            for r in read:
                if r is self.ClientCon:
                    incoming = r.recv(1024)
                    if not incoming:
                        return
                    else:
                        self.React(incoming)


class SocketAcceptingThread(threading.Thread):
    def __init__(self, react_fun, address):
        threading.Thread.__init__(self)
        self.React = react_fun
        self.Port = address
        logging.debug("SocketAcceptingThread started")
        self.start()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(self.Port)
        sock.listen(1)
        while not StopEvent.isSet():
            connection, client_address = sock.accept()
            SocketThread(connection, self.React)


class KeepAliveThread(threading.Thread):
    def __init__(self, react_fun, address):
        threading.Thread.__init__(self)
        self.React = react_fun
        self.Port = address
        logging.debug("KeepAliveThread Started")
        self.start()

    def run(self):
        while not StopEvent.isSet():
            t = SocketAcceptingThread(self.React, self.Port)
            t.join()


def bind(react_fun, address=('192.168.1.69', 1234)):
    KeepAliveThread(react_fun, address)


def stop():
    StopEvent.set()


def nothing(input):
    print "nothing..."
    print input


if __name__ == "__main__":
    bind(nothing)
    time.sleep(1000000000000)

print "goodbye"
