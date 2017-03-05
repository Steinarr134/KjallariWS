import threading
import time

class CloseLaterThread(threading.Thread):
    def __init__(self, door, close_after):
        threading.Thread.__init__(self)
        self.wait4 = close_after
        self.door = door
        self.start()

    def run(self):
        time.sleep(self.wait4)
        self.door.close()

OPEN = 1
CLOSED = 0


class RemoteDoor(object):
    OPEN = 1
    CLOSED = 0
    def __init__(self, send_fun, auto_close_time=None):
        self.send_fun = send_fun
        self.State = CLOSED
        self.AutoCloseTime = auto_close_time
        
    def is_open(self):
        return self.State == OPEN

    def open(self):
        self.State = OPEN
        self.send_fun("open")
        if self.AutoCloseTime:
            CloseLaterThread(self, self.AutoCloseTime)

    def close(self):
        self.State = CLOSED
        self.send_fun("close")
