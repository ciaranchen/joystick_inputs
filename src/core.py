import math
from InputConfig import ArcJoyStickConfig, JoyStickFunctionController


class Arc:
    """
    Arc的中心区域为0，周围区域为1-NUM。
    另外确保区域1在正上方
    """
    arc_threshold = 0.3

    @staticmethod
    def start_arc(num):
        return - math.pi / num - math.pi / 2

    @classmethod
    def arcs(cls, num):
        return [cls.start_arc(num) + i * (2 * math.pi / num) for i in range(num + 1)]

    @staticmethod
    def arc_distance(x, y):
        return math.sqrt(x * x + y * y)

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


class ArcInputCore(Arc):
    def __init__(self, config_location):
        self.config = ArcJoyStickConfig.load_from(config_location)
        print('default_layer:', self.config.default_layer)
        self.layer = self.config.default_layer
        self.available_layer = list(self.config.layers.keys())
        self.config.load_controller(JoyStickFunctionController())

    def action(self, joy, event_type, button=None, trigger=None, axis=False):
        now_layer = self.config.layers[self.layer]
        if axis:
            if not now_layer.is_axis_layer:
                # Axis 的位置暂时不会产生输出
                return
            # handle axis_move
            func = now_layer.axis[axis]
            func(self, joy, event_type)
        if trigger is not None:
            func = now_layer.trigger[0 if trigger else 1]
            func(self, joy, event_type)
        elif button is not None:
            func = now_layer.buttons[button]
            func(self, joy, event_type)
        else:
            print(button, trigger, axis)
            raise RuntimeError('Not valid call.')


if __name__ == '__main__':
    import pygame

    aic = ArcInputCore(r"C:\Users\ciaran\Desktop\Projects\joystick_inputs\configs\code6.json")
    aic.action(None, pygame.JOYBUTTONDOWN, trigger=False)
    aic.action(None, pygame.JOYBUTTONUP, trigger=False)
