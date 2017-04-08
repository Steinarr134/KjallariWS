
class A(object):
    def __init__(self, s):
        self.stuff = s

    def p(self):
        print "blablabla and also: " + str(self.stuff)



a = A("test")

a.p()


def p2(self):
    print "i've changed my mind about " + str(self.stuff)

a.p = p2

a.p()