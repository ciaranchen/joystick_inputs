# coding: utf-8
import pygame
from input_method_config import BasicConfig as InputMethodCore
from code_table import SingleEnglishCode as CodeTable
from pynput.keyboard import Controller


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


class InputController(JoyConHandler):
    def __init__(self):
        pygame.init()
        super().__init__()
        self.code_table = CodeTable()
        self.imc = InputMethodCore()
        self.keyboard = Controller()

    def main(self):
        self.gui_init()
        clock = pygame.time.Clock()
        joysticks = {}

        while True:
            events = pygame.event.get()
            # print(events)
            for event in events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    exit()

                # Handle hotplugging
                if event.type == pygame.JOYDEVICEADDED:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks[joy.get_instance_id()] = joy
                    print(f"Joystick {joy.get_instance_id()} connencted")

                if event.type == pygame.JOYDEVICEREMOVED:
                    del joysticks[event.instance_id]
                    print(f"Joystick {event.instance_id} disconnected")

            self.refresh(joysticks)
            self.handle_mouse(events)

            if self.binding:
                self.handle_axis(events)
                self.handle_trigger(events, self.press_key)

            l_arc_id, r_arc_id = self.imc.get_arcs(self.lx, self.ly, self.rx, self.ry,
                                                   self.code_table.LNum, self.code_table.RNum)
            l_keys, r_keys = self.code_table.get_recommend(l_arc_id, r_arc_id)

            self.draw_gui(l_arc_id, r_arc_id, l_keys, r_keys)

            pygame.display.flip()
            clock.tick(30)

    def press_key(self, lx, ly, rx, ry):
        la, ra = self.imc.get_arcs(lx, ly, rx, ry, self.code_table.LNum, self.code_table.RNum)
        code = self.code_table.get_code(la, ra)
        self.keyboard.tap(code)

    def gui_init(self):
        raise NotImplementedError

    def draw_gui(self, l_arc_id, r_arc_id, l_keys, r_keys):
        raise NotImplementedError

    def handle_mouse(self, events):
        raise NotImplementedError


class ClickModeJoyCon(InputController):
    pass
