# coding: utf-8
"""
Joystick management class
"""
import enum
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Set

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


class SingletonJoystickHandler(metaclass=ABCMeta):
    _instance = None

    @classmethod
    def joy_add(cls, joy, state):
        """
        bind joystick while JOY DEVICE ADDED
        """
        # Singleton
        if cls._instance:
            return cls._instance

        raise NotImplementedError

    @abstractmethod
    def is_joy(self, instance_id: int):
        raise NotImplementedError


@dataclass
class JoystickEventHandler(SingletonJoystickHandler):
    state = None

    axis_mapping: Dict[str, int]
    button_mapping: Dict[int, int]

    @classmethod
    def joy_add(cls, joy, state):
        """
        bind joystick while JOY DEVICE ADDED
        :param joy:
        :param state:
        """
        raise NotImplementedError

    @abstractmethod
    def is_joy(self, instance_id: int):
        raise NotImplementedError

    def handle_events(self, event, callback):
        if hasattr(event, 'instance_id') and self.is_joy(event.instance_id):
            self.handle_button(event, callback)
            self.handle_trigger(event, callback)
            self.handle_axis(event, callback)

    def handle_button(self, e, cb):
        raise NotImplementedError

    def handle_trigger(self, e, cb):
        raise NotImplementedError

    def handle_axis(self, e, cb):
        raise NotImplementedError


@dataclass
class XBoxEventHandler(JoystickEventHandler):
    joy: pygame.joystick.Joystick = None
    state = None
    type_name: str = "Xbox 360 Controller"

    TRIGGER_THRESHOLD: float = 0.3
    AXIS_THRESHOLD: float = 0.3
    LR_AXIS: List[int] = (0, 1, 2, 3)

    @classmethod
    def joy_add(cls, joy, state):
        if joy.get_name() != XBoxEventHandler.type_name:
            return None
        if cls._instance:
            return cls._instance

        res = cls(axis_mapping={
            'lx': 0, 'ly': 1, 'rx': 2, 'ry': 3,
            'lt': 4, 'rt': 5
        }, button_mapping={**{
            k: k for k in range(6)
        }, **{
            8: 10, 9: 11
        }})
        res.joy = joy
        res.state = state
        cls._instance = res
        return res

    def is_joy(self, instance_id: int):
        return instance_id == self.joy.get_instance_id()

    def handle_button(self, e, cb):
        if e.type == pygame.JOYBUTTONDOWN or e.type == pygame.JOYBUTTONUP:
            b = self.button_mapping[e.button]
            print(e)
            is_pressed = e.type == pygame.JOYBUTTONDOWN
            self.state.buttons[b] = is_pressed
            cb(self.state, e.type, button=b)

    def handle_trigger(self, e, cb):
        if e.type != pygame.JOYAXISMOTION:
            return
        for t in ['lt', 'rt']:
            if e.axis == self.axis_mapping[t]:
                if not getattr(self.state, t) and e.value >= self.TRIGGER_THRESHOLD:
                    state_pressed = True
                elif getattr(self.state, t) and e.value < self.TRIGGER_THRESHOLD:
                    state_pressed = False
                else:
                    return
                setattr(self.state, t, state_pressed)
                cb(self.state, pygame.JOYBUTTONDOWN if state_pressed else pygame.JOYBUTTONUP, trigger=(t == 'lr'))

    def handle_axis(self, e, cb):
        if e.type != pygame.JOYAXISMOTION:
            return
        if e.axis == self.axis_mapping['lx']:
            self.state.lx = limit_to(e.value, -1, 1)
        elif e.axis == self.axis_mapping['ly']:
            self.state.ly = limit_to(e.value, -1, 1)
        elif e.axis == self.axis_mapping['rx']:
            self.state.rx = limit_to(e.value, -1, 1)
        elif e.axis == self.axis_mapping['ry']:
            self.state.ry = limit_to(e.value, -1, 1)
        cb(self.state, e.type, axis=True)


class JoyConEventHandler(JoystickEventHandler):

    @classmethod
    def joy_add(cls, joy):
        if joy.get_name() != "Wireless Gamepad":
            return None

        if cls._instance:
            res = cls._instance
        #     TODO: 手柄按键映射

        res = cls.singleton()
        if res.l_joy and res.l_joy != joy:
            res.r_joy = joy
        else:
            res.l_joy = joy
        return res

    def is_joy(self, instance_id: int):
        return instance_id == self.l_joy.get_instance_id() or instance_id == self.r_joy.get_instance_id()

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
                        _rx, _ry = self.r_joy.get_hat(1)
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

    def handle_axis(self, e):
        if e.instance_id == self.l_joy.get_instance_id():
            self.lx, self.ly = e.value[1], e.value[0]
        elif e.instance_id == self.r_joy.get_instance_id():
            self.rx, self.ry = -e.value[1], -e.value[0]
