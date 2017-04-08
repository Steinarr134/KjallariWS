import socket
import threading
import select
import logging
import os
import time
import atexit
import demjson
import pickle

logging.basicConfig(level=logging.DEBUG)

_cleanups = list()
_events = list()


def cleanup():
    for c in _cleanups:
        c.shutdown(socket.SHUT_RDWR)
        c.close()
        _cleanups.pop(c)
    logging.info("RaspiCom cleanup done")
    for e in _events:
        e.set()

atexit.register(cleanup)


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


class SocketThread(threading.Thread):
    def __init__(self, client_con, react_fun, stopevent):
        threading.Thread.__init__(self)
        self.React = react_fun
        self.ClientCon = client_con
        self.StopEvent = stopevent
        logging.debug("SocketThread started")
        self.start()

    def run(self):
        while not self.StopEvent.isSet():
            read, write, e = select.select([self.ClientCon, self.StopEvent], [], [])
            for r in read:
                if r is self.ClientCon:
                    incoming = r.recv(1024)
                    if not incoming:
                        return
                    else:
                        self.React(incoming)


class SocketAcceptingThread(threading.Thread):
    def __init__(self, react_fun, address, stopevent):
        threading.Thread.__init__(self)
        self.React = react_fun
        self.Port = address
        self.StopEvent = stopevent
        logging.debug("SocketAcceptingThread started")
        self.start()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.Port)
        sock.listen(1)
        _cleanups.append(sock)
        while not self.StopEvent.isSet():
            try:
                sock.settimeout(1)
                connection, client_address = sock.accept()
                logging.info("Connection with {} accepted".format(client_address))
                SocketThread(connection, self.React, self.StopEvent)
            except socket.timeout:
                pass
        cleanup()


class KeepAliveThread(threading.Thread):
    def __init__(self, react_fun, address, stopevent):
        threading.Thread.__init__(self)
        self.React = react_fun
        self.Port = address
        self.StopEvent = stopevent
        logging.debug("KeepAliveThread Started")
        self.start()

    def run(self):
        while not self.StopEvent.isSet():
            t = SocketAcceptingThread(self.React, self.Port, self.StopEvent)
            t.join()
            print "vesen"
            time.sleep(10)


class Receiver(object):
    def __init__(self):
        self.StopEvent = WaitableEvent()
        self.StopEvent.clear()

    def bind(self, react_fun, address=('192.168.1.69', 1234)):
        KeepAliveThread(react_fun, address, self.StopEvent)

    def stop(self):
        self.StopEvent.set()


class Sender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.StopEvent = WaitableEvent()
        self.ResetEvent = WaitableEvent()
        self.Address = None
        self.start()
        _events.append(self.StopEvent)
        _events.append(self.ResetEvent)

    def run(self):
        while not self.StopEvent.isSet():
            if self.is_disconnected():
                logging.info("connection disconnected, trying to reconnect...")
                self.reconnect()
            else:
                logging.debug("connection seems active")

    def is_disconnected(self, timeout=None):
        logging.debug("Checking on connection...")
        read, write, e = select.select([self.Sock,
                                        self.StopEvent,
                                        self.ResetEvent], [], [], timeout)
        logging.debug("select done...{}".format(read))
        for r in read:
            if r is self.Sock:
                # socket sould never say anything
                return True
            elif r is self.ResetEvent:
                self.ResetEvent.clear()
        if not read:
            try:
                self.Sock.getpeername()
            except socket.error as e:
                return True
        return False

    def connect(self, address):
        self.Address = address
        self.ResetEvent.set()
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.Sock.connect(address)
        except socket.error as e:
            logging.warning("connection unsuccessfull: {}".format(e))

    def reconnect(self):
        if self.Address is None:
            return
        self.Sock.close()
        time.sleep(0.1)
        self.connect(self.Address)

    def disconnect(self):
        self.Sock.close()

    def send(self, data):
        self.Sock.sendall(pickle.dumps(data))


    def stop(self):
        self.StopEvent.set()
