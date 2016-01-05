
import subprocess
import threading
import sys
import demjson
import pyodbc
from Dictionaries import EventIDs
from Imports import ListeningThread

# import time

GroupID = 0

# proc2 = subprocess.Popen(['python', 'Asta.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

StdoutLock = threading.Lock()


class Moteino:
    def __init__(self):
        self.Proc = subprocess.Popen(['python', 'Moteinos.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.Lock = threading.Lock()

    def send(self, diction):
        with self.Lock:
            self.Proc.stdin.write(demjson.encode(diction) + '\n')


moteino = Moteino()


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
    def test2(incoming, event=None):
        moteino.send({
            'ID': event.ID,
            'Command': 'Test2'
        })

    @staticmethod
    def execute(incoming, event=None):
        exec incoming['exec']

    @staticmethod
    def greendude_correct_passcode(incoming, event=None):
        # play message
        # start tape recorder
        # let faceZ know about it
        # stop tape recorder
        raise NotImplementedError


def report_info(event_id, info2log):
        _cnxn = pyodbc.connect(r'Driver={SQL Server};'
                               r'Server=.\SQLEXPRESS;'
                               r'Database=KjallariDB;'
                               r'Trusted_Connection=yes;')
        _cursor = _cnxn.cursor()
        for (s, i) in info2log:
            _cursor.execute("EXEC ReportInfo %d, \'%s\', %d" % (event_id, s, i))
        _cnxn.close()


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
        _cursor.execute("EXEC ReportEvent %d, %d" % (self.ID, GroupID))
        _cnxn.close()

    def fire(self, incoming=None):
        if self.Reportable:
            self.report()
        self.React_fun(incoming, event=self)


# Populate events from database.......... haettur vid thetta hehehe
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
    EventIDs['Execute']: Event(EventIDs['Execute'], "Execute", Reactions.execute, reportable=False),
    EventIDs['Test1']: Event(EventIDs['Test1'], 'Test1', Reactions.test, reportable=False),
    EventIDs['Test2']: Event(EventIDs['Test2'], 'Test2', Reactions.test2, reportable=False)

}


class FireEventThread(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        try:
            incoming = demjson.decode(self.Incoming)
            events[incoming['ID']].fire(incoming)
        except:
            print "incoming: " + str(self.Incoming)


# TestThread = ListeningThread(sys.stdin, FireEventThread)
# TestThread.start()
MoteinoThread = ListeningThread(moteino.Proc.stdout, FireEventThread)
MoteinoThread.start()

