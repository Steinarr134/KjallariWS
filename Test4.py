import subprocess
import demjson
import sys

proc1 = subprocess.Popen(['python', 'ThePope.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

while True:
    incoming = sys.stdin.readline()[:-1]
    if incoming == "q":
        proc1.kill()
        sys.exit()
    else:
        a = {incoming}
        proc1.stdin.write(demjson.encode(a)+"\n")
