# coding: utf-8
"""
File to handle the Joystick Thumb Input
"""
import math
from code_table import SingleEnglishCode as CodeTable


class BasicConfig:
    arc_threshold = 0.3

    @staticmethod
    def start_arc(num):
        return - math.pi / num - math.pi / 2

    @staticmethod
    def arc_distance(x, y):
        return math.dist((x, y), (0, 0))

    @staticmethod
    def which_arc(x, y, arc_num, start_arc):
        if BasicConfig.arc_distance(x, y) < BasicConfig.arc_threshold:
            return 0
        angle = math.atan2(y, x)
        if angle < start_arc:
            angle += 2 * math.pi
        for i in range(arc_num):
            angle1 = start_arc + i * (2 / arc_num * math.pi)
            angle2 = angle1 + (2 / arc_num * math.pi)
            if angle1 <= angle < angle2 or (angle1 - math.pi * 2) <= angle < (angle2 - math.pi * 2):
                return i + 1
        return -1

    def get_arcs(self, lx, ly, rx, ry, l_num, r_num):
        la = BasicConfig.which_arc(lx, ly, l_num, self.start_arc(l_num))
        ra = BasicConfig.which_arc(rx, ry, r_num, self.start_arc(r_num))
        return la, ra


if __name__ == '__main__':
    ct = CodeTable()
    bc = BasicConfig()
    print(ct.get_code(*bc.get_arcs(0.4, 0.2, 0.7, 0.1, ct.L_NUM, ct.R_NUM)))
    print(ct.get_recommend(*bc.get_arcs(0.4, 0.2, 0.7, 0.1, ct.L_NUM, ct.R_NUM)))
