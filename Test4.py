import subprocess
import sys

# proc1 = subprocess.Popen(['python', 'ThePope.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)



class A:

    def __init__(self, a):
        self.ID = a

    def who(self):
        print self.ID


class B(A):
    def __init__(self):
        A.__init__(self, 2)
        self.num = 0

    def pr(self):
        print self.num

