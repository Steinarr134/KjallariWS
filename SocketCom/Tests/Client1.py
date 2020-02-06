from SocketCom import ComplicatedClient as CC
import time

c = CC("192.168.21.104", 12345, ["Command", "s"])

c.send_and_receive("Status")

time.sleep(2)

c.send("Play", "1.ogg")

time.sleep(2)

quit()
