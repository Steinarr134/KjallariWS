import serial

OPEN = 0
CLOSED = 1

    
class Door(object):
    OPEN = 0
    CLOSED = 1
    def __init__(self, controller, position):
        self.Controller = controller
        self.Position = position
        self.State = CLOSED
        self.Controller.add_door(self)

    def is_open(self):
        return self.State == OPEN

    def open(self):
        self.Controller.open(self)

    def close(self):
        self.Controller.close(self)


class EmptyDoorSlot(object):
    def __init__(self):
        self.State = OPEN


class DoorController(object):
    def __init__(self, port):
        self.Serial = serial.Serial(port, 115200)
        self.Doors = [EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot(),
                      EmptyDoorSlot()]

    def _send_(self):
        s = ''
        for door in self.Doors:
            s += str(door.State)
        self.Serial.write(s + '\n')

    def _set_(self, door, state):
        if not isinstance(door, Door):
            raise ValueError("Expected a Door instance, but got a " + str(type(door)))
        door.State = state
        self._send_()

    def open(self, door):
        print "opening door"
        self._set_(door, OPEN)

    def close(self, door):
        print "closing door"
        self._set_(door, CLOSED)

    def open_all(self):
        for door in self.Doors:
            door.State = OPEN
        self._send_()

    def close_all(self):
        for door in self.Doors:
            door.State = CLOSED
        self._send_()

    def add_door(self, door):
        if not isinstance(door, Door):
            raise ValueError("Expected a Door instance but got a " + str(door))
        if not isinstance(self.Doors[door.Position], EmptyDoorSlot):
            raise ValueError("Another door is already in that position!")

        self.Doors[door.Position] = door
