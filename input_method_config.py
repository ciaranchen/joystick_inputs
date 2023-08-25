# coding: utf-8
"""
File to handle the Joystick Thumb Input
"""
import math
from code_table import CodeExtension
from dataclasses import dataclass
from typing import List


@dataclass
class ArcComputation:
    arc_num: int

    @property
    def start_arc(self):
        return - math.pi / self.arc_num - math.pi / 2

    @property
    def arcs(self):
        return [self.start_arc + i * (2 * math.pi / self.arc_num) for i in range(self.arc_num + 1)]

    def which_arc(self, x, y):
        angle = math.atan2(y, x)
        if angle < self.start_arc:
            angle += 2 * math.pi
        for i, a1, a2 in zip(range(self.arc_num), self.arcs, self.arcs[1:]):
            if a1 <= angle < a2 or a1 <= (angle - math.pi * 2) < a2:
                return i + 1
        return -1


@dataclass
class InputManagerCore:
    # status

    def __init__(self, config):

        self.config = config
        self.layer = config.layers
    @staticmethod
    def _press_to_layer(layer_name):
        pass

    @staticmethod
    def arc(self, x, y, arc):
        pass

    def action(self, now_state, event):
        pass


class BasicInputMethodCore:
    arc_threshold = 0.3

    @staticmethod
    def start_arc(num):
        return - math.pi / num - math.pi / 2

    @staticmethod
    def arc_distance(x, y):
        return math.sqrt(x * x + y * y)

    @classmethod
    def arcs(cls, num):
        return [cls.start_arc(num) + i * (2 * math.pi / num) for i in range(num + 1)]

    @classmethod
    def which_arc(cls, x, y, arc_num):
        if cls.arc_distance(x, y) < cls.arc_threshold:
            return 0
        angle = math.atan2(y, x)
        if angle < cls.arcs(arc_num)[0]:
            angle += 2 * math.pi
        for i, a1, a2 in zip(range(arc_num), cls.arcs(arc_num), cls.arcs(arc_num)[1:]):
            if a1 <= angle < a2 or a1 <= (angle - math.pi * 2) < a2:
                return i + 1
        return -1

    def get_arcs(self, lx, ly, rx, ry, l_num, r_num):
        la = self.which_arc(lx, ly, l_num)
        ra = self.which_arc(rx, ry, r_num)
        # print("arcs: ", la, ra)
        return la, ra


class IMCoreForAlternativeSix(BasicInputMethodCore):

    @classmethod
    def arcs(cls, num: int):
        if num != 6:
            return [cls.start_arc(num) + i * (2 * math.pi / num) for i in range(num + 1)]
        else:
            return [
                - 11 * math.pi / 18,  # -15
                8 * math.pi / 18 - 11 * math.pi / 18,  # 85
                13 * math.pi / 18 - 11 * math.pi / 18,
                math.pi - 11 * math.pi / 18,
                math.pi + 8 * math.pi / 18 - 11 * math.pi / 18,
                math.pi + 13 * math.pi / 18 - 11 * math.pi / 18,
                2 * math.pi - 11 * math.pi / 18
            ]


if __name__ == '__main__':
    ct = CodeExtension()
    bc = IMCoreForAlternativeSix()
    print(ct.get_code(*bc.get_arcs(1, -1, 0, 0, ct.L_NUM, ct.R_NUM)))
    # print(ct.get_recommend(*bc.get_arcs(0.4, 0.2, 0.7, 0.1, ct.L_NUM, ct.R_NUM)))
