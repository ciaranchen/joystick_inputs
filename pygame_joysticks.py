# coding: utf-8
import pygame


def limit_to(number, lower, upper):
    if number < lower:
        return lower
    if number > upper:
        return upper
    return number


class Handler:
    """
    Base class for handler
    """

    def __init__(self):
        self.binding = False
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0

    def refresh(self, joysticks):
        raise NotImplementedError

    def handle_trigger(self, events, callback):
        raise NotImplementedError

    def handle_axis(self, events):
        raise NotImplementedError


class XBoxHandler(Handler):
    LR_AXIS = (0, 1, 2, 3)

    def __init__(self):
        super().__init__()
        self.joy = None

    def refresh(self, joysticks, name="Xbox 360 Controller"):
        if self.binding:
            if self.joy.get_id() not in joysticks:
                self.binding = False
                return
        else:
            for joy in joysticks.values():
                if joy.get_name() == name:
                    self.joy = joy
                    self.binding = True
                    return

    def handle_trigger(self, events, callback):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                # TODO: button type
                # get axis state
                lx, ly = self.joy.get_axis(self.LR_AXIS[0]), self.joy.get_axis(self.LR_AXIS[1])
                rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                callback(lx, ly, rx, ry)

    def handle_axis(self, events):
        for e in events:
            if e.type == pygame.JOYAXISMOTION:
                if e.instance_id == self.joy.get_instance_id() and e.axis in self.LR_AXIS:
                    if e.axis == self.LR_AXIS[0]:
                        self.lx = limit_to(e.value, -1, 1)
                    elif e.axis == self.LR_AXIS[1]:
                        self.ly = limit_to(e.value, -1, 1)
                    elif e.axis == self.LR_AXIS[2]:
                        self.rx = limit_to(e.value, -1, 1)
                    elif e.axis == self.LR_AXIS[3]:
                        self.ry = limit_to(e.value, -1, 1)


class JoyConHandler(Handler):
    def __init__(self):
        super().__init__()
        self.l_joy = None
        self.r_joy = None

    def refresh(self, joysticks):
        if self.binding:
            pass
        else:
            # TODO: fixme.
            if len(joysticks) == 2:
                self.r_joy, self.l_joy = joysticks.values()
                self.binding = True
                return

    def handle_trigger(self, events, callback):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                if e.button == '8' and e.instance_id != self.l_joy.get_instance_id():
                    self.l_joy, self.r_joy = self.r_joy, self.l_joy
                    return
                # TODO: button type
                _lx, _ly = self.l_joy.get_hat(0)
                lx, ly = _ly, _lx
                _rx, _ry = self.r_joy.get_hat(0)
                rx, ry = -_ry, -_rx
                print(lx, ly, rx, ry)
                callback(lx, ly, rx, ry)

    def handle_axis(self, events):
        for e in events:
            if e.type == pygame.JOYHATMOTION:
                if e.instance_id == self.l_joy.get_instance_id():
                    self.lx, self.ly = e.value[1], e.value[0]
                elif e.instance_id == self.r_joy.get_instance_id():
                    self.rx, self.ry = -e.value[1], -e.value[0]
