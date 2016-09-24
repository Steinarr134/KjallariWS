import serial

OPEN = 1
CLOSED = 0


class Door(object):
    def __init__(self, controller):
        self.Controller = controller
        self.State = OPEN
        self.Controller.add_door(self)

    def open(self):
        self.Controller.open(self)

    def close(self):
        self.Controller.close(self)


class DoorController(object):
    def __init__(self, port):
        self.Serial = serial.Serial(port, 115200)
        self.Doors = []

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
        self._set_(door, OPEN)

    def close(self, door):
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
        if len(self.Doors) == 8:
            raise ValueError("DoorController can only handle 8 doors")
        self.Doors.append(door)
