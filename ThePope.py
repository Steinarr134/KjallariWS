
import subprocess
import threading
import sys
import pickle
import pyodbc
# import time

GroupID = 0

# proc1 = subprocess.Popen(['python', 'Test2.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# proc2 = subprocess.Popen(['python', 'Asta.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

SerialLock = threading.Lock()
StdoutLock = threading.Lock()


# This static class was created to hold all reactions without clustering the global namespace
class Reactions:
    def __init__(self):
        pass

#   All Reactions must be defined here
    @staticmethod
    def no_reaction(incoming=None, event=None):
        pass

    @staticmethod
    def test(incoming, event=None):
        print( "this is a test, the " + str(event.Name) +
               " raised this. Also, " + str(incoming))

    @staticmethod
    def execute(incoming, event=None):
        exec incoming['exec']

    @staticmethod
    def greendude_correct_passcode(incoming, event=None):
        print "program missing"
        # play message
        # start tape recorder
        # let faceZ know about it
        # stop tape recorder



# A class describing the Event object,
class Event(object):
    def __init__(self, _id, name, react_fun, reportable=True):
        self.React_fun = react_fun
        self.ID = _id
        self.Name = name
        self.Reportable = reportable

    def report(self):
        _cnxn = pyodbc.connect(r'Driver={SQL Server};'
                              r'Server=.\SQLEXPRESS;'
                              r'Database=KjallariDB;'
                              r'Trusted_Connection=yes;')
        _cursor = _cnxn.cursor()
        _cursor.execute("EXEC ReportEvent %d, %d"%(self.ID, GroupID))
        _cnxn.close()

    def fire(self, incoming=None):
        if self.Reportable:
            self.report()
        self.React_fun(incoming, event=self)


# Populate events from database
'''
events = list()
cnxn = pyodbc.connect(r'Driver={SQL Server};'
                      r'Server=.\SQLEXPRESS;'
                      r'Database=KjallariDB;'
                      r'Trusted_Connection=yes;')
cursor = cnxn.cursor()
cursor.execute("SELECT [ID], [Name], [Reaction] FROM [EventType]")
while True:
    row = cursor.fetchone()
    if not row:
        break
    else:
        r = None
        exec "r = Reactions."+row.Reaction
        events.append(Event(row.ID, row.Name, r))
cnxn.close()
events.append(Event(100, "Execute", Reactions.execute, reportable=False))
'''

events = {
    1: Event(1, "execute", Reactions.execute, reportable=False)
}


class FireEventThread(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        incoming = pickle.loads(self.Incoming)
        events[incoming['id']].fire(incoming)


class ListeningThread(threading.Thread):
    def __init__(self, listen2):
        threading.Thread.__init__(self)
        self.listen2 = listen2

    def run(self):
        while True:
            incoming = self.listen2.readline()[:-1] # nota .strip()?
            fire = FireEventThread(incoming)
            fire.start()



# SerialThread = BasicThread(Serial, moteinos.react)
TestThread = ListeningThread(sys.stdin)

# SerialThread.start()
TestThread.start()


