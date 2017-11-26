import threading
import time

OPEN = 1
CLOSED = 0


class CloseLaterThread(threading.Thread):
    def __init__(self, door, close_after):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.wait4 = close_after
        self.door = door
        self.start()

    def run(self):
        time.sleep(self.wait4)
        if self.door.AutoClose:
            self.door.close()
        else:
            self.door.State = CLOSED


class RemoteDoor(object):
    OPEN = 1
    CLOSED = 0

    def __init__(self, node, send_fun = None,
                 auto_close=False, auto_close_time=4):
        self.node = node
        self.send_fun = send_fun if send_fun is not None else node.send
        self.State = CLOSED
        self.AutoCloseTime = auto_close_time
        self.AutoClose = auto_close
        
    def is_open(self):
        return self.State == OPEN

    def open(self):
        self.State = OPEN
        self.send_fun("open")
        if self.AutoClose:
            CloseLaterThread(self, self.AutoCloseTime)

    def close(self):
        self.State = CLOSED
        self.send_fun("close")
