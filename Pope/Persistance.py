import sys
import os
import pickle


path = "/home/pope/PopePersistance/"
filename = path + "PreviousGroupState.pkl"


class Perri(object):
    def __init__(self):
        self.vars = []
        self.names = []

    def get(self, name, default=None):
        if name in self.names:
            return self.vars[self.names.index(name)]
        else:
            self.put(default, name)
            return default

    def put(self, var, name):
        self.vars.append(var)
        self.names.append(name)

    def save(self):
        with open(filename, "w+") as f:
            pickle.dump(self.__dict__, f)
        print "Perri was saved"

    def load(self):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                thing = pickle.load(f)
                self.__dict__.update(thing)
        print "Perri loaded from file"
        print self.names

    def reset(self):
        thing = Perri()
        self.__dict__.update(thing.__dict__)


class Object(object):
    pass


if __name__ == '__main__':
    p = Perri()
    c = Object()
    c.a = 30
    c.b = 20
    c = p.get("c", default=c)
    c.a = 10
    p.save()

    del c
    p.reset()
    print p.names

    p.load()
    c = p.get("c", object())
    print c.a, c.b