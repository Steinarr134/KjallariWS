
import threading


class ListeningThread(threading.Thread):
    def __init__(self, listen2, react_with):
        threading.Thread.__init__(self)
        self.listen2 = listen2
        self.React_With = react_with

    def run(self):
        while True:
            incoming = self.listen2.readline().rstrip('\n')  # nota [:-1]?
            fire = self.React_With(incoming)
            fire.start()
