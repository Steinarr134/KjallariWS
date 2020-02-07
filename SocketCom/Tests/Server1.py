from SocketCom import ComplicatedServer as CS

s = CS(12345, ["Command", "s"])


def handle(bla):
    print bla
    if bla:
        if bla["Command"] == "Status":
            s.send("Status", s="blabla")
        elif bla["Command"] == "Play":
            print "Playing: " + bla["s"]

s.bind(handle)

