import subprocess
import sys

# proc1 = subprocess.Popen(['python', 'ThePope.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


a = [1, 2, 3, 4, 5]
b = "abcde"

for (A,B) in map(None, a,b):
    print str(A) + ": " + B