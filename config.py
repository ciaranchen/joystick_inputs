# coding: utf-8
"""
File to handle the Joystick Thumb Input
"""
import math
from code_table import CodeTable


class BasicConfig:
    lstart_arc = - math.pi / 4
    larc_number = 4
    rstart_arc = - math.pi / 8
    rarc_number = 8
    arc_threshold = 0.3
    l_arc_mapping = {
    }
    r_arc_mapping = {
    }

    def __init__(self):
        self.ct = CodeTable()

    @staticmethod
    def arc_distance(x, y):
        return math.dist((x, y), (0, 0))

    @staticmethod
    def whichArc(x, y, arc_num, start_arc):
        if BasicConfig.arc_distance(x, y) < BasicConfig.arc_threshold:
            return 0
        angle = math.atan2(-y, x)
        if angle < 0:
            angle += 2 * math.pi
        for i in range(arc_num):
            angle1 = start_arc + i * (2 / arc_num * math.pi)
            angle2 = angle1 + (2 / arc_num * math.pi)
            if angle1 < angle < angle2 or (angle1 - math.pi * 2) < angle < (angle2 - math.pi * 2):
                return i + 1
        return -1

    def get_key(self, lx, ly, rx, ry):
        la = BasicConfig.whichArc(lx, ly, BasicConfig.larc_number, BasicConfig.lstart_arc)
        ra = BasicConfig.whichArc(rx, ry, BasicConfig.rarc_number, BasicConfig.rstart_arc)
        print(la, ra)
        return "a"


if __name__ == '__main__':
    bc = BasicConfig()
    print(bc.get_key(0.6, 0.7, 0.2, 0.1))
