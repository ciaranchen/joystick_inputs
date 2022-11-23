# coding: utf-8
import enum
import pygame
from pynput.keyboard import Controller as Keyboard, Key
from pynput.mouse import Controller as Mouse, Button
from input_method_config import IMCoreForAlternativeSix as InputMethodCore
from code_table import CodeExtension as CodeTable


def limit_to(number, lower, upper):
    if number < lower:
        return lower
    if number > upper:
        return upper
    return number


class JoyMode(enum.Enum):
    NORMAL_MODE = 0
    MOTION_MODE = 1
    MOUSE_MODE = 2


class Handler:
    """
    Base class for handler
    """

    def __init__(self):
        self.code_table = CodeTable()
        self.imc = InputMethodCore()
        self.keyboard = Keyboard()
        self.binding = False
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0

        pygame.init()

    def press_key(self, la, ra):
        print(la, ra, self.code_table.code[la, ra])
        code = self.code_table.get_code(la, ra)
        self.keyboard.tap(code)

    def refresh(self, joysticks):
        raise NotImplementedError

    def handle_button(self, events):
        raise NotImplementedError

    def handle_trigger(self, events):
        pass

    def handle_axis(self, events):
        raise NotImplementedError

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

            self.handle_button(events)
            if self.binding:
                self.handle_axis(events)
                self.handle_trigger(events)

            l_arc_id, r_arc_id = self.imc.get_arcs(self.lx, self.ly, self.rx, self.ry,
                                                   self.code_table.L_NUM, self.code_table.R_NUM)
            l_keys, r_keys = self.code_table.get_recommend(l_arc_id, r_arc_id)

            self.draw_gui(l_arc_id, r_arc_id, l_keys, r_keys)

            pygame.display.flip()
            clock.tick(30)

    def gui_init(self):
        raise NotImplementedError

    def draw_gui(self, l_arc_id, r_arc_id, l_keys, r_keys):
        raise NotImplementedError

    def handle_mouse(self, events):
        raise NotImplementedError


class XBoxHandler(Handler):
    LR_AXIS = (0, 1, 2, 3)
    TRIGGER_THRESHOLD = 0.3
    AXIS_THRESHOLD = 0.3

    def __init__(self):
        super().__init__()

        self.joy = None
        self.LT_pressed = False
        self.RT_pressed = False

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

    def handle_button(self, events):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                print(e.button)
                if e.button < 4:
                    # map single key.
                    self.keyboard.tap(self.code_table.right_mapping[e.button])

    def handle_trigger(self, events):
        for e in events:
            if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                # Left Trigger mapping
                if e.axis == 4:
                    if not self.LT_pressed and e.value >= self.TRIGGER_THRESHOLD:
                        self.keyboard.press(self.code_table.LT_mapping)
                        self.LT_pressed = True
                    if self.LT_pressed and e.value < self.TRIGGER_THRESHOLD:
                        self.keyboard.release(self.code_table.LT_mapping)
                        self.LT_pressed = False
                elif e.axis == 5:
                    if not self.RT_pressed and e.value >= self.TRIGGER_THRESHOLD:
                        self.RT_pressed = True
                        lx, ly = self.joy.get_axis(self.LR_AXIS[0]), self.joy.get_axis(self.LR_AXIS[1])
                        rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                        la, ra = self.imc.get_arcs(lx, ly, rx, ry, self.code_table.L_NUM, self.code_table.R_NUM)
                        self.press_key(la, ra)
                    if self.RT_pressed and e.value < self.TRIGGER_THRESHOLD:
                        self.RT_pressed = False
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                if e.button == 4 or e.button == 5:
                    self.keyboard.press(self.code_table.bumper_mapping[e.button - 4])
            if e.type == pygame.JOYBUTTONUP and e.instance_id == self.joy.get_instance_id():
                if e.button == 4 or e.button == 5:
                    self.keyboard.release(self.code_table.bumper_mapping[e.button - 4])

    def handle_axis(self, events):
        for e in events:
            if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
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
                print("Binding: ", self.binding)
                return

    def handle_button(self, events):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                print(e.instance_id, e.button)
                if e.button == 8 and e.instance_id != self.l_joy.get_instance_id():
                    self.l_joy = pygame.joystick.Joystick(e.instance_id)
                if e.button == 9 and e.instance_id != self.r_joy.get_instance_id():
                    self.r_joy = pygame.joystick.Joystick(e.instance_id)
                if e.instance_id == self.r_joy.get_instance_id():
                    if e.button < 4:
                        self.keyboard.tap(self.code_table.right_mapping[[1, 3, 0, 2][e.button]])
                if e.button == 12:
                    self.keyboard.tap(Key.esc)

    def handle_trigger(self, events):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                if e.instance_id == self.l_joy.get_instance_id():
                    # Left trigger
                    if e.button == 15:
                        self.keyboard.press(self.code_table.LT_mapping)
                    elif e.button == 14:
                        self.keyboard.press(self.code_table.bumper_mapping[0])
                if e.instance_id == self.r_joy.get_instance_id():
                    if e.button == 15:
                        _lx, _ly = self.l_joy.get_hat(0)
                        lx, ly = _ly, _lx
                        _rx, _ry = self.r_joy.get_hat(0)
                        rx, ry = -_ry, -_rx
                        la, ra = self.imc.get_arcs(lx, ly, rx, ry, self.code_table.L_NUM, self.code_table.R_NUM)
                        self.press_key(la, ra)
                    elif e.button == 14:
                        self.keyboard.press(self.code_table.bumper_mapping[1])
            if e.type == pygame.JOYBUTTONUP:
                if e.instance_id == self.r_joy.get_instance_id() and e.button == 14:
                    self.keyboard.release(self.code_table.bumper_mapping[1])
                elif e.instance_id == self.l_joy.get_instance_id():
                    if e.button == 15:
                        self.keyboard.release(self.code_table.LT_mapping)
                    elif e.button == 14:
                        self.keyboard.release(self.code_table.bumper_mapping[0])

    def handle_axis(self, events):
        for e in events:
            if e.type == pygame.JOYHATMOTION:
                if e.instance_id == self.l_joy.get_instance_id():
                    self.lx, self.ly = e.value[1], e.value[0]
                elif e.instance_id == self.r_joy.get_instance_id():
                    self.rx, self.ry = -e.value[1], -e.value[0]


class XBoxExtend(XBoxHandler):
    def __init__(self):
        super().__init__()
        self.mode = JoyMode.NORMAL_MODE
        self.motion_pressed = None
        self.mouse = Mouse()
        self.mouse_orient = (0, 0)
        self.mouse_acceleration = (0.3, 0.1)
        self.mouse_tick = [0, 0]
        self.mouse_speed = [0, 0]

    def handle_button(self, events):
        super().handle_button(events)
        for e in events:
            if e.type == pygame.JOYHATMOTION and e.instance_id == self.joy.get_instance_id():
                hx, hy = e.value
                if hy == 1:
                    print("Motion mode...")
                    self.mode = JoyMode.MOTION_MODE
                if hy == -1:
                    print("Mouse mode...")
                    self.mode = JoyMode.MOUSE_MODE
                    self.mouse_orient = (0, 0)
                    self.mouse_acceleration = (0.03, 0.01)
                    self.mouse_tick = [0, 0]
                    self.mouse_speed = [0, 0]
                if hy == 0 and hx == 0:
                    print("Normal mode ...")
                    self.mode = JoyMode.NORMAL_MODE
                print(hx, hy)

    def handle_axis(self, events):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_axis(events)
        if self.mode == JoyMode.MOTION_MODE:
            for e in events:
                if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                    if e.axis == self.LR_AXIS[2] or e.axis == self.LR_AXIS[3]:
                        rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                        ra = self.imc.which_arc(rx, ry, 4, self.imc.start_arc(4))
                        # print('ra: ', ra)
                        if ra == 0:
                            if self.motion_pressed is not None:
                                self.keyboard.tap(self.motion_pressed)
                                self.motion_pressed = None
                        else:
                            self.motion_pressed = self.code_table.MOTION[ra - 1]
        if self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                    if e.axis == self.LR_AXIS[2] or e.axis == self.LR_AXIS[3]:
                        rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                        ox, oy = self.mouse_orient
                        self.mouse_orient = (rx, ry)
                        sign = lambda a: (a > 0) - (a < 0)
                        self.mouse_tick[0] = 0 if sign(ox) != sign(rx) else self.mouse_tick[0] + 1
                        self.mouse_tick[1] = 0 if sign(oy) != sign(ry) else self.mouse_tick[1] + 1
                        for i in range(2):
                            self.mouse_speed[i] = self.mouse_speed[i] + self.mouse_tick[i] * self.mouse_acceleration[i]
                    if e.axis == self.LR_AXIS[0] or e.axis == self.LR_AXIS[1]:
                        lx, ly = self.joy.get_axis(self.LR_AXIS[0]), self.joy.get_axis(self.LR_AXIS[1])
                        self.mouse.scroll(0, lx)
                        self.mouse.scroll(1, ly)
            self.mouse.move(self.mouse_speed[0] * self.mouse_orient[0], self.mouse_speed[1] * self.mouse_orient[1])

    def handle_trigger(self, events):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_trigger(events)
        if self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                    if e.axis == 4:
                        if not self.LT_pressed and e.value >= self.TRIGGER_THRESHOLD:
                            self.mouse.press(Button.left)
                            self.LT_pressed = True
                        if self.LT_pressed and e.value < self.TRIGGER_THRESHOLD:
                            self.mouse.release(Button.left)
                            self.LT_pressed = False
                    elif e.axis == 5:
                        if not self.RT_pressed and e.value >= self.TRIGGER_THRESHOLD:
                            self.mouse.press(Button.right)
                            self.RT_pressed = True
                        if self.RT_pressed and e.value < self.TRIGGER_THRESHOLD:
                            self.mouse.release(Button.right)
                            self.RT_pressed = False
                if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                    if e.button == 4:
                        self.mouse.press(Button.left)
                    if e.button == 5:
                        self.mouse.press(Button.right)
                if e.type == pygame.JOYBUTTONUP and e.instance_id == self.joy.get_instance_id():
                    if e.button == 4:
                        self.mouse.release(Button.left)
                    if e.button == 5:
                        self.mouse.release(Button.right)


class JoyConExtend(JoyConHandler):
    def __init__(self):
        super().__init__()
        self.mode = JoyMode.NORMAL_MODE
        self.motion_pressed = None
        self.mouse = Mouse()
        self.mouse_acceleration = (0.3, 0.1)
        self.mouse_orient = (0, 0)
        self.mouse_tick = [0, 0]
        self.mouse_speed = [0, 0]

    def handle_button(self, events):
        super().handle_button(events)
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.l_joy.get_instance_id():
                print(e)
                if e.button == 2:
                    self.mode = JoyMode.MOTION_MODE
                if e.button == 1:
                    self.mode = JoyMode.MOUSE_MODE
            if e.type == pygame.JOYBUTTONUP and e.instance_id == self.l_joy.get_instance_id() and e.button < 4:
                self.mode = JoyMode.NORMAL_MODE

    def handle_axis(self, events):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_axis(events)
        elif self.mode == JoyMode.MOTION_MODE:
            for e in events:
                if e.type == pygame.JOYHATMOTION:
                    if e.instance_id == self.r_joy.get_instance_id():
                        rx, ry = -e.value[1], -e.value[0]
                        if rx == -1:
                            self.keyboard.tap(self.code_table.MOTION[3])
                        elif rx == 1:
                            self.keyboard.tap(self.code_table.MOTION[1])
                        if ry == -1:
                            self.keyboard.tap(self.code_table.MOTION[0])
                        elif ry == 1:
                            self.keyboard.tap(self.code_table.MOTION[2])
        elif self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYHATMOTION and e.instance_id == self.r_joy.get_instance_id():
                    rx, ry = -e.value[1], -e.value[0]
                    ox, oy = self.mouse_orient
                    self.mouse_tick[0] = 0 if ox != rx else self.mouse_tick[0] + 1
                    self.mouse_tick[1] = 0 if oy != ry else self.mouse_tick[1] + 1
                    self.mouse_orient = (rx, ry)
                    for i in range(2):
                        self.mouse_speed[i] = self.mouse_speed[i] + self.mouse_tick[i] * self.mouse_acceleration[i]
                if e.type == pygame.JOYHATMOTION and e.instance_id == self.l_joy.get_instance_id():
                    x, y = e.value[1], e.value[0]
                    if x != 0:
                        self.mouse.scroll(0, x)
                    if y != 0:
                        self.mouse.scroll(1, -y)
        self.mouse.move(self.mouse_speed[0] * self.mouse_orient[0], self.mouse_speed[1] * self.mouse_orient[1])

    def handle_trigger(self, events):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_trigger(events)
        elif self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYBUTTONDOWN:
                    if e.button == 15 or e.button == 14:
                        if e.instance_id == self.l_joy.get_instance_id():
                            self.mouse.press(Button.left)
                        if e.instance_id == self.r_joy.get_instance_id():
                            self.mouse.press(Button.right)
                if e.type == pygame.JOYBUTTONUP:
                    if e.button == 15 or e.button == 14:
                        if e.instance_id == self.l_joy.get_instance_id():
                            self.mouse.release(Button.left)
                        if e.instance_id == self.r_joy.get_instance_id():
                            self.mouse.release(Button.right)


class ClickModeJoyCon(JoyConHandler):
    def __init__(self):
        super().__init__()
        self.last_left = 0
        self.last_right = 0

    def press_key(self, la, ra):
        print(self.last_left, self.last_right, self.code_table.code[self.last_left, self.last_right])
        code = self.code_table.get_code(self.last_left, self.last_right)
        self.keyboard.tap(code)
        self.last_left, self.last_right = 0, 0

    def handle_button(self, events):
        super().handle_button(events)
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.button == 13:
                if e.instance_id == self.l_joy.get_instance_id():
                    self.last_left = 0
                elif e.instance_id == self.r_joy.get_instance_id():
                    self.last_right = 0

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

            self.handle_button(events)
            if self.binding:
                self.handle_axis(events)
                self.handle_trigger(events)

            l_arc_id, r_arc_id = self.imc.get_arcs(self.lx, self.ly, self.rx, self.ry,
                                                   self.code_table.L_NUM, self.code_table.R_NUM)
            if l_arc_id != 0:
                self.last_left = l_arc_id
            if r_arc_id != 0:
                self.last_right = r_arc_id
            l_keys, r_keys = self.code_table.get_recommend(self.last_left, self.last_right)

            self.draw_gui(self.last_left, self.last_right, l_keys, r_keys)

            pygame.display.flip()
            clock.tick(30)
