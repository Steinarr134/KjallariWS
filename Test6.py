import pyodbc
from Dictionaries import *
from Imports import *
import Moteinos

if not __name__ == "__main__":
    raise Exception("ThePope must be run as a main module, no importing")

GroupID = 0

# proc2 = subprocess.Popen(['python', 'Asta.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# StdoutLock = threading.Lock()


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
        print("this is a test, the " + str(event.Name) +
              " raised this. Also, " + str(incoming))

    @staticmethod
    def test2(incoming, event=None):
        Moteinos.send({
            'ID': event.ID,
            'Command': 'Test2'
        })

    @staticmethod
    def execute(incoming, event=None):
        exec incoming['exec']

    class Moteinos:
        def __init__(self):
            pass

        class GreenDude:
            def __init__(self):
                pass

            @staticmethod
            def greendude_correct_passcode(incoming, event=None):
                # play message
                # start tape recorder
                # let faceZ know about it
                # stop tape recorder
                raise NotImplementedError

            handles = {
                MoteinoCommands['CorrectPasscode']: greendude_correct_passcode
            }

            @staticmethod
            def handle(incoming, event=None):
                Reactions.Moteinos.GreenDude.handles[incoming['Command']].__func__(incoming, event=None)

        class Test:
            def __init__(self):
                pass

            @staticmethod
            def test1(incoming, event=None):
                debug_print("moteino test recieved " + str(incoming))

            handles = {
                MoteinoCommands['Test1']: test1
            }

            @staticmethod
            def handle(incoming, event=None):
                Reactions.Moteinos.Test.handles[incoming['Command']].__func__(incoming, event=None)

        handles = {
            MoteinoIDs['TestDevice']: Test.handle,
            MoteinoIDs['GreenDude']: GreenDude
        }

        @staticmethod
        def handle(incoming, event=None):
            Reactions.Moteinos.handles[incoming['SenderID']](incoming, event=event)


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


events = {
    EventIDs['Execute']:
        Event(EventIDs['Execute'], "Execute", Reactions.execute, reportable=False),
    EventIDs['Test1']:
        Event(EventIDs['Test1'], 'Test1', Reactions.test, reportable=False),
    EventIDs['Test2']:
        Event(EventIDs['Test2'], 'Test2', Reactions.test2, reportable=False),
    EventIDs['RecievedFromMoteinoNetwork']:
        Event(EventIDs['RecievedFromMoteinoNetwork'], "RecievedFromMoteinoNetwork", Reactions.Moteinos.handle)
}


class FireEventThread(threading.Thread):
    def __init__(self, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming

    def run(self):
        events[self.Incoming['ID']].fire(self.Incoming)


class ProcessQueueThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.Q = q

    def run(self):
        while True:
            diction = self.Q.get()
            debug_print("ProcessQueueThread retrieved something from Q")
            fire = FireEventThread(diction)
            fire.start()


if __name__ == "__main__":
    Moteinos.start_listening()
    Qthread = ProcessQueueThread(Moteinos.Q)
    Qthread.start()

#     eitthvad meira....
