# coding: utf-8
import enum
from abc import ABCMeta, abstractmethod
import pygame
from pynput.keyboard import Key
from pynput.mouse import Button

from input_method_config import BasicInputMethodCore


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


class JoystickEventHandler(metaclass=ABCMeta):
    def __init__(self):
        self.binding = False

    @classmethod
    def joy_add(cls, joy):
        """
        bind joystick while JOY DEVICE ADDED
        """
        raise NotImplementedError

    @abstractmethod
    def joy_del(self, event):
        """
        remove binding of joystick while JOY DEVICE REMOVED
        """
        raise NotImplementedError

    @abstractmethod
    def handle_button(self, events, keyboard, code_table):
        raise NotImplementedError

    @abstractmethod
    def handle_trigger(self, events, keyboard, code_table, press_key):
        raise NotImplementedError

    @abstractmethod
    def handle_axis(self, events, keyboard, code_table, axis):
        raise NotImplementedError


class XBoxEventHandler(JoystickEventHandler):
    @classmethod
    def joy_add(cls, joy):
        if joy.get_name() != "Xbox 360 Controller":
            return None
        res = cls()
        res.joy = joy
        return res

    def joy_del(self, event):
        return event.instance_id == self.joy.get_instance_id()

    LR_AXIS = (0, 1, 2, 3)
    TRIGGER_THRESHOLD = 0.3
    AXIS_THRESHOLD = 0.3

    def __init__(self):
        super().__init__()

        self.joy = None
        self.trigger_pressed = [False, False]

    def handle_button(self, events, keyboard, code_table):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                print(e.button)
                if e.button < 4:
                    # map single key.
                    keyboard.tap(code_table.right_mapping[e.button])

    def trigger_handler(self, i, value, cb1, cb2):
        if not self.trigger_pressed[i] and value >= self.TRIGGER_THRESHOLD:
            cb1(value)
            self.trigger_pressed[i] = True
        elif self.trigger_pressed[i] and value < self.TRIGGER_THRESHOLD:
            cb2(value)
            self.trigger_pressed[i] = False

    def handle_trigger(self, events, keyboard, code_table, press_key):
        for e in events:
            if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                # Left Trigger mapping
                if e.axis == 4:
                    self.trigger_handler(0, e.value,
                                         lambda _: keyboard.press(code_table.LT_mapping),
                                         lambda _: keyboard.release(code_table.LT_mapping))
                elif e.axis == 5:
                    def do_press_key(_):
                        lx, ly = self.joy.get_axis(self.LR_AXIS[0]), self.joy.get_axis(self.LR_AXIS[1])
                        rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                        press_key(lx, ly, rx, ry)

                    self.trigger_handler(1, e.value,
                                         do_press_key,
                                         lambda x: None)
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                if e.button == 4 or e.button == 5:
                    keyboard.press(code_table.bumper_mapping[e.button - 4])
            if e.type == pygame.JOYBUTTONUP and e.instance_id == self.joy.get_instance_id():
                if e.button == 4 or e.button == 5:
                    keyboard.release(code_table.bumper_mapping[e.button - 4])

    def handle_axis(self, events, keyboard, code_table, axis):
        for e in events:
            if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                if e.axis == self.LR_AXIS[0]:
                    axis['lx'] = limit_to(e.value, -1, 1)
                elif e.axis == self.LR_AXIS[1]:
                    axis['ly'] = limit_to(e.value, -1, 1)
                elif e.axis == self.LR_AXIS[2]:
                    axis['rx'] = limit_to(e.value, -1, 1)
                elif e.axis == self.LR_AXIS[3]:
                    axis['ry'] = limit_to(e.value, -1, 1)


class JoyConEventHandler(JoystickEventHandler):
    _instance = None

    @classmethod
    def singleton(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    @classmethod
    def joy_add(cls, joy):
        if joy.get_name() == "Wireless Gamepad":
            res = cls.singleton()
            if res.l_joy and res.l_joy != joy:
                res.r_joy = joy
            else:
                res.l_joy = joy
            return res
        else:
            return None

    def joy_del(self, event):
        if self.l_joy.get_instance_id() == event.instance_id:
            self.l_joy = None
        elif self.r_joy.get_instance_id() == event.instance_id:
            self.r_joy = None
        return self.r_joy is None and self.r_joy is None

    def __init__(self):
        super().__init__()
        self.l_joy = None
        self.r_joy = None

    def handle_button(self, events, keyboard, code_table):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                print(e.instance_id, e.button)
                if e.button == 8 and e.instance_id != self.l_joy.get_instance_id():
                    self.l_joy = pygame.joystick.Joystick(e.instance_id)
                if e.button == 9 and e.instance_id != self.r_joy.get_instance_id():
                    self.r_joy = pygame.joystick.Joystick(e.instance_id)
                if e.instance_id == self.r_joy.get_instance_id():
                    if e.button < 4:
                        keyboard.tap(code_table.right_mapping[[1, 3, 0, 2][e.button]])
                if e.button == 12:
                    keyboard.tap(Key.esc)

    def handle_trigger(self, events, keyboard, code_table, press_key):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                if e.instance_id == self.l_joy.get_instance_id():
                    # Left trigger
                    if e.button == 15:
                        keyboard.press(code_table.LT_mapping)
                    elif e.button == 14:
                        keyboard.press(code_table.bumper_mapping[0])
                if e.instance_id == self.r_joy.get_instance_id():
                    if e.button == 15:
                        _lx, _ly = self.l_joy.get_hat(0)
                        lx, ly = _ly, _lx
                        _rx, _ry = self.r_joy.get_hat(0)
                        rx, ry = -_ry, -_rx
                        press_key(lx, ly, rx, ry)
                    elif e.button == 14:
                        keyboard.press(code_table.bumper_mapping[1])
            if e.type == pygame.JOYBUTTONUP:
                if e.instance_id == self.r_joy.get_instance_id() and e.button == 14:
                    keyboard.release(code_table.bumper_mapping[1])
                elif e.instance_id == self.l_joy.get_instance_id():
                    if e.button == 15:
                        keyboard.release(code_table.LT_mapping)
                    elif e.button == 14:
                        keyboard.release(code_table.bumper_mapping[0])

    def handle_axis(self, events, keyboard, code_table, axis):
        for e in events:
            if e.type == pygame.JOYHATMOTION:
                if e.instance_id == self.l_joy.get_instance_id():
                    axis['lx'], axis['ly'] = e.value[1], e.value[0]
                elif e.instance_id == self.r_joy.get_instance_id():
                    axis['rx'], axis['ry'] = -e.value[1], -e.value[0]


class JoystickExtendInterface(metaclass=ABCMeta):
    def __init__(self):
        self.mode = JoyMode.NORMAL_MODE
        self.motion_pressed = None
        self.mouse_orient = (0, 0)
        self.mouse_acceleration = (0.3, 0.1)
        self.mouse_tick = [0, 0]
        self.mouse_speed = [0, 0]

    @abstractmethod
    def ex_handle_axis(self, events, keyboard, code_table, axis, mouse):
        pass

    @abstractmethod
    def ex_handle_trigger(self, events, keyboard, code_table, press_key, mouse):
        pass


class XBoxExtendMode(JoystickExtendInterface, XBoxEventHandler):
    def __init__(self):
        super(XBoxExtendMode, self).__init__()
        super(JoystickExtendInterface, self).__init__()

    def handle_button(self, events, keyboard, code_table):
        super().handle_button(events, keyboard, code_table)
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

    def ex_handle_axis(self, events, keyboard, code_table, axis, mouse):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_axis(events, keyboard, code_table, axis)
        if self.mode == JoyMode.MOTION_MODE:
            for e in events:
                if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                    if e.axis == self.LR_AXIS[2] or e.axis == self.LR_AXIS[3]:
                        rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                        ra = BasicInputMethodCore.which_arc(rx, ry, 4)
                        # print('ra: ', ra)
                        if ra == 0:
                            if self.motion_pressed is not None:
                                keyboard.tap(self.motion_pressed)
                                self.motion_pressed = None
                        else:
                            self.motion_pressed = code_table.MOTION[ra - 1]
        if self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                    if e.axis == self.LR_AXIS[2] or e.axis == self.LR_AXIS[3]:
                        rx, ry = self.joy.get_axis(self.LR_AXIS[2]), self.joy.get_axis(self.LR_AXIS[3])
                        ox, oy = self.mouse_orient
                        self.mouse_orient = (rx, ry)

                        def sign(a):
                            return (a > 0) - (a < 0)

                        self.mouse_tick[0] = 0 if sign(ox) != sign(rx) else self.mouse_tick[0] + 1
                        self.mouse_tick[1] = 0 if sign(oy) != sign(ry) else self.mouse_tick[1] + 1
                        for i in range(2):
                            self.mouse_speed[i] = self.mouse_speed[i] + self.mouse_tick[i] * self.mouse_acceleration[i]
                    if e.axis == self.LR_AXIS[0] or e.axis == self.LR_AXIS[1]:
                        lx, ly = self.joy.get_axis(self.LR_AXIS[0]), self.joy.get_axis(self.LR_AXIS[1])
                        mouse.scroll(0, lx)
                        mouse.scroll(1, ly)
            mouse.move(self.mouse_speed[0] * self.mouse_orient[0], self.mouse_speed[1] * self.mouse_orient[1])

    def ex_handle_trigger(self, events, keyboard, code_table, press_key, mouse):

        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_trigger(events, keyboard, code_table, press_key)
        if self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYAXISMOTION and e.instance_id == self.joy.get_instance_id():
                    if e.axis == 4:
                        self.trigger_handler(0, e.value,
                                             lambda _: mouse.press(Button.left),
                                             lambda _: mouse.release(Button.left))
                    elif e.axis == 5:
                        self.trigger_handler(1, e.value,
                                             lambda _: mouse.press(Button.right),
                                             lambda _: mouse.release(Button.right))
                if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                    if e.button == 4:
                        mouse.press(Button.left)
                    if e.button == 5:
                        mouse.press(Button.right)
                if e.type == pygame.JOYBUTTONUP and e.instance_id == self.joy.get_instance_id():
                    if e.button == 4:
                        mouse.release(Button.left)
                    if e.button == 5:
                        mouse.release(Button.right)


class JoyConExtendMode(JoystickExtendInterface, JoyConEventHandler):
    def __init__(self):
        super(JoyConExtendMode, self).__init__()
        super(JoystickExtendInterface, self).__init__()

    def handle_button(self, events, keyboard, code_table):
        super().handle_button(events, keyboard, code_table)
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.l_joy.get_instance_id():
                print(e)
                if e.button == 2:
                    self.mode = JoyMode.MOTION_MODE
                if e.button == 1:
                    self.mode = JoyMode.MOUSE_MODE
            if e.type == pygame.JOYBUTTONUP and e.instance_id == self.l_joy.get_instance_id() and e.button < 4:
                self.mode = JoyMode.NORMAL_MODE

    def ex_handle_axis(self, events, keyboard, code_table, axis, mouse):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_axis(events, keyboard, code_table, axis)
        elif self.mode == JoyMode.MOTION_MODE:
            for e in events:
                if e.type == pygame.JOYHATMOTION:
                    if e.instance_id == self.r_joy.get_instance_id():
                        rx, ry = -e.value[1], -e.value[0]
                        if rx == -1:
                            keyboard.tap(code_table.MOTION[3])
                        elif rx == 1:
                            keyboard.tap(code_table.MOTION[1])
                        if ry == -1:
                            keyboard.tap(code_table.MOTION[0])
                        elif ry == 1:
                            keyboard.tap(code_table.MOTION[2])
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
                        mouse.scroll(0, x)
                    if y != 0:
                        mouse.scroll(1, -y)
        mouse.move(self.mouse_speed[0] * self.mouse_orient[0], self.mouse_speed[1] * self.mouse_orient[1])

    def ex_handle_trigger(self, events, keyboard, code_table, press_key, mouse):
        if self.mode == JoyMode.NORMAL_MODE:
            super().handle_trigger(events, keyboard, code_table, press_key)
        elif self.mode == JoyMode.MOUSE_MODE:
            for e in events:
                if e.type == pygame.JOYBUTTONDOWN:
                    if e.button == 15 or e.button == 14:
                        if e.instance_id == self.l_joy.get_instance_id():
                            mouse.press(Button.left)
                        if e.instance_id == self.r_joy.get_instance_id():
                            mouse.press(Button.right)
                if e.type == pygame.JOYBUTTONUP:
                    if e.button == 15 or e.button == 14:
                        if e.instance_id == self.l_joy.get_instance_id():
                            mouse.release(Button.left)
                        if e.instance_id == self.r_joy.get_instance_id():
                            mouse.release(Button.right)


class JoystickClickInterface(metaclass=ABCMeta):
    def click_handle_button(self, events, keyboard, code_table, last_axis):
        pass


class JoyConClickMode(JoyConExtendMode, JoystickClickInterface):
    def click_handle_button(self, events, keyboard, code_table, last_axis):
        super(JoyConExtendMode, self).handle_button(events, keyboard, code_table)
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.button == 13:
                if e.instance_id == self.l_joy.get_instance_id():
                    last_axis[0] = 0
                elif e.instance_id == self.r_joy.get_instance_id():
                    last_axis[1] = 0


class XBoxClickMode(JoystickClickInterface, XBoxExtendMode):

    def click_handle_button(self, events, keyboard, code_table, last_axis):
        super(XBoxExtendMode, self).handle_button(events, keyboard, code_table)
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN and e.instance_id == self.joy.get_instance_id():
                if e.button == 8:
                    last_axis[0] = 0
                elif e.button == 9:
                    last_axis[1] = 0