import math
from InputConfig.input_config import ArcJoyStickConfig
from InputConfig.input_functions import JoyStickFunctionController


class InputManagerCore:
    arc_threshold = 0.3

    def __init__(self, config_location):
        self.config = ArcJoyStickConfig.load_from(config_location)
        self.layer = self.config.default_layer
        self.available_layer = list(self.config.layers.keys())
        print('default_layer:', self.layer)

        self.axis_function_layers = [name for name, layer in self.config.layers.items() if not layer.is_axis_layer]
        self.config.load_controller(JoyStickFunctionController())

    def action(self, joy, event_type, button=None, trigger=None, axis=False):
        # check_layer()
        now_layer = self.config.layers[self.layer]
        if axis:
            if now_layer in self.axis_function_layers:
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
    import pygame

    imc = InputManagerCore(r"C:\Users\ciaran\Desktop\Projects\joystick_inputs\configs\code6.json")
    imc.action(None, pygame.JOYBUTTONDOWN, trigger=False)
    imc.action(None, pygame.JOYBUTTONUP, trigger=False)
