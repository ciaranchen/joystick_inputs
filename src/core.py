import math
from functools import reduce
from typing import Callable

import pygame
from pygame import JOYBUTTONUP, JOYBUTTONDOWN

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyController

from InputConfig.input_config import ArcJoyStickConfig


class JoyStickFunctionController:
    mouse_orient = (0, 0)
    mouse_acceleration = (0.3, 0.1)
    mouse_tick = [0, 0]
    mouse_speed = [0, 0]

    def __init__(self) -> None:
        super().__init__()
        self.mouse_controller = MouseController()
        self.key_controller = KeyController()

    @staticmethod
    def __tap(controller, key, event, types=None):
        if types is None:
            types = [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]
        if event == types[0]:
            controller.press(key)
        elif event == types[1]:
            controller.release(key)
        return None

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

    def enter_axis(self):
        def __inner(core, joy, event):
            now_layer = core.config.layers[core.layer]
            l_index = core.which_arc(joy.lx, joy.ly, now_layer.L_NUM)
            r_index = core.which_arc(joy.rx, joy.ry, now_layer.R_NUM)
            func = now_layer.axis[l_index][r_index]
            return func(core, joy, event)

        return __inner

    @staticmethod
    def none():
        # do nothing
        return lambda _, __, ___: None

    def mouse_move(self, input):
        try:
            index = int(input)
        except:
            raise RuntimeError('Error config')
        # direction = [][index]

    def mouse_click(self, button):
        b = {'left': Button.left, 'right': Button.right, 'middle': Button.middle}[button]
        return lambda _, __, e: self.__tap(self.mouse_controller, b, e)

    def press(self, key):
        return lambda _, __, e: self.__tap(self.key_controller, key, e)


class InputManagerCore:
    arc_threshold = 0.3

    def __init__(self, config_location):
        self.config = ArcJoyStickConfig.load_from(config_location)
        self.layer = self.config.default_layer
        self.available_layer = list(self.config.layers.keys())
        print('default_layer:', self.layer)

        self.function_axises = []
        for name, layer in self.config.layers.items():
            axs = reduce(lambda x, y: x + y, layer._axis, [])
            if any([isinstance(a, tuple) for a in axs]):
                self.function_axises.append(name)

        self.config.load_controller(JoyStickFunctionController())

    def action(self, joy, event_type, button=None, trigger=None, axis=False):
        # check_layer()
        now_layer = self.config.layers[self.layer]
        if axis:
            if now_layer in self.function_axises:
                # handle axis_move
                func = now_layer.axis[axis]
                func(self, joy, event_type)
            return
        if trigger is not None:
            func = now_layer.trigger[0 if trigger else 1]
            func(self, joy, event_type)
        elif button is not None:
            func = now_layer.buttons[button]
            func(self, joy, event_type)
        else:
            print(button, trigger, axis)
            raise RuntimeError('Not valid call.')

    @staticmethod
    def start_arc(num):
        return - math.pi / num - math.pi / 2

    @staticmethod
    def arcs(num):
        return [InputManagerCore.start_arc(num) + i * (2 * math.pi / num) for i in range(num + 1)]

    @staticmethod
    def arc_distance(x, y):
        return math.sqrt(x * x + y * y)

    @staticmethod
    def which_arc(x, y, arc_num):
        if InputManagerCore.arc_distance(x, y) < InputManagerCore.arc_threshold:
            return 0
        angle = math.atan2(y, x)
        if angle < InputManagerCore.arcs(arc_num)[0]:
            angle += 2 * math.pi
        for i, a1, a2 in zip(range(arc_num), InputManagerCore.arcs(arc_num), InputManagerCore.arcs(arc_num)[1:]):
            if a1 <= angle < a2 or a1 <= (angle - math.pi * 2) < a2:
                return i + 1
        return -1


if __name__ == '__main__':
    imc = InputManagerCore(r"C:\Users\ciaran\Desktop\Projects\joystick_inputs\configs\code6.json")
    imc.action(None, JOYBUTTONDOWN, trigger=False)
    imc.action(None, JOYBUTTONUP, trigger=False)
