import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import pygame
from pygame import JOYBUTTONUP, JOYBUTTONDOWN

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyController


class JoyStickInputFunctions(Enum):
    # basic action
    none = r'<None>'
    # layer switch action
    press_to_layer = r'<PressToLayer =(.*)>'
    hold_to_layer = r'<HoldToLayer =(.*)>'
    # axis action
    enter_axis = r'<EnterCode>'
    # mouse action
    mouse_move = r'<Mouse =(\d+)>'
    mouse_click = r'<MouseClick =(.*)>'

    @classmethod
    def get_function(cls, key: str) -> Optional[Tuple[str, re.Match]]:
        for name, reg in cls.__members__.items():
            match_res = re.fullmatch(reg, key)
            if match_res:
                return name, match_res
        return None

    @classmethod
    def is_function(cls, key: str, function: "JoyStickInputFunctions") -> bool:
        reg: str = function.value
        match_res = re.fullmatch(reg, key)
        return match_res is not None


class JoyStickBasicFunction:
    @staticmethod
    def none():
        # do nothing
        return lambda _, __, ___: None

    @staticmethod
    def __press_release(controller, key, event, types=None):
        if types is None:
            types = [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]
        if event == types[0]:
            controller.press(key)
        elif event == types[1]:
            controller.release(key)
        return None


@dataclass
class JoyStickKeyboardFunction(JoyStickBasicFunction):
    key_controller = KeyController()

    def press(self, key):
        return lambda _, __, e: self.__press_release(self.key_controller, key, e)

    def tap(self, key, _type=pygame.JOYBUTTONDOWN):
        def __tap(core, joy, event):
            if event == _type:
                self.key_controller.tap(key)

        return __tap

    @staticmethod
    def press_to_layer(layer):
        def _inner(core, joy, event):
            if event == JOYBUTTONDOWN:
                print(layer)
                core.layer = layer

        return _inner

    @staticmethod
    def hold_to_layer(layer):
        def _inner(core, _, event):
            if event == JOYBUTTONUP:
                core.layer = core.last_layer
            elif event == JOYBUTTONDOWN:
                core.last_layer = core.layer
                core.layer = layer

        return _inner

    @staticmethod
    def enter_axis():
        def __inner(core, joy, event):
            now_layer = core.config.layers[core.layer]
            l_index = core.which_arc(joy.lx, joy.ly, now_layer.L_NUM)
            r_index = core.which_arc(joy.rx, joy.ry, now_layer.R_NUM)
            func = now_layer.axis[l_index][r_index]
            return func(core, joy, event)

        return __inner


@dataclass
class JoyStickMouseFunction(JoyStickBasicFunction):
    mouse_controller = MouseController()

    mouse_orient = (0, 0)
    mouse_acceleration = (0.3, 0.1)
    mouse_tick = [0, 0]
    mouse_speed = [0, 0]

    def mouse_move(self, move):
        try:
            index = int(move)
        except:
            raise RuntimeError('Error config')
        # direction = [][index]

    def mouse_click(self, button):
        if not hasattr(Button, button):
            return self.none()
        b = Button[button]
        return lambda _, __, e: self.__press_release(self.mouse_controller, b, e)


class JoyStickFunctionController(JoyStickKeyboardFunction, JoyStickMouseFunction):
    pass
