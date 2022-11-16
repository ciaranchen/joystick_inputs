# coding: utf-8
"""
File to handle the Joystick Thumb Input
"""
import math
from code_table import SingleEnglishCode as CodeTable


class BasicConfig:
    arc_threshold = 0.3

    def __init__(self, code_table):
        self.ct = code_table

    @staticmethod
    def start_arc(num):
        return - math.pi / num

    @staticmethod
    def arc_distance(x, y):
        return math.dist((x, y), (0, 0))

    @staticmethod
    def which_arc(x, y, arc_num, start_arc):
        if BasicConfig.arc_distance(x, y) < BasicConfig.arc_threshold:
            return 0
        angle = math.atan2(-y, x)
        if angle < start_arc:
            angle += 2 * math.pi
        for i in range(arc_num):
            angle1 = start_arc + i * (2 / arc_num * math.pi)
            angle2 = angle1 + (2 / arc_num * math.pi)
            if angle1 < angle < angle2 or (angle1 - math.pi * 2) < angle < (angle2 - math.pi * 2):
                return i + 1
        return -1

    def get_key(self, lx, ly, rx, ry):
        la = BasicConfig.which_arc(lx, ly, self.ct.LNum, self.start_arc(self.ct.LNum))
        ra = BasicConfig.which_arc(rx, ry, self.ct.RNum, self.start_arc(self.ct.RNum))
        return self.ct.get_code(la, ra)

    def get_recommend(self, lx, ly, rx, ry):
        la = BasicConfig.which_arc(lx, ly, self.ct.LNum, self.start_arc(self.ct.LNum))
        ra = BasicConfig.which_arc(rx, ry, self.ct.RNum, self.start_arc(self.ct.RNum))
        return self.ct.get_recommend(la, ra)


if __name__ == '__main__':
    bc = BasicConfig(CodeTable())
    print(bc.get_key(0.4, 0.2, 0.7, 0.1))
    print(bc.get_recommend(0.4, 0.2, 0.7, 0.1))
