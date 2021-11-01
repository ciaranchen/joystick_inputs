import pygame
import sys
import time
import math
from code_table import CodeTable
from xinput import XInputJoystick
from pynput.keyboard import Key, Controller
from operator import itemgetter, attrgetter

eucli_dist = lambda x, y: math.sqrt((x[0]-y[0]) ** 2 + (x[1]-y[1]) ** 2)


class JoystickInput(object):
    def __init__(self):
        self.window_size = 600
        self.joystick = self.get_joystick()
        self.gui_config = {
            'x_inner_radius': self.window_size / 6,
            'x_outer_radius': self.window_size / 2,
            'y_inner_radius': self.window_size / 24,
            'y_outer_radius': self.window_size / 8,
            'yh_inner_radius': self.window_size / 12,
            'yh_outer_radius': self.window_size / 4,
            'trigger_threshold': 0.3
        }
        assert self.gui_config['x_outer_radius'] > self.gui_config['x_inner_radius'] and self.gui_config['y_outer_radius'] > self.gui_config['y_inner_radius'] and self.gui_config['yh_outer_radius'] > self.gui_config['yh_inner_radius']
        assert self.gui_config['y_outer_radius'] / self.gui_config['y_inner_radius'] == self.gui_config['yh_outer_radius'] / self.gui_config['yh_inner_radius']
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0
        self.lt, self.rt = 0, 0
        self.lastLTPress = False
        self.lastRTPress = False
        self.font = pygame.font.Font(None, 30)
        self.code_table = CodeTable
        self.keyboard = Controller()

    
    def get_joystick(self):
        joysticks = XInputJoystick.enumerate_devices()
        device_numbers = list(map(attrgetter('device_number'), joysticks))

        print('found %d devices: %s' % (len(joysticks), device_numbers))

        if not joysticks:
            return None
        return joysticks[0]


    def draw_arc(self, i, cx, cy, cr1, cr2, color = (255, 255, 255), text = None):
        angle1 = i * math.pi / 4 + math.pi / 8
        angle2 = angle1 + math.pi / 4

        pygame.draw.line(self.screen, color, (cx + cr1 * math.cos(angle1), cy - cr1 * math.sin(angle1)), (cx + cr2 * math.cos(angle1), cy - cr2 * math.sin(angle1)), 1)
        pygame.draw.line(self.screen, color, (cx + cr1 * math.cos(angle2), cy - cr1 * math.sin(angle2)), (cx + cr2 * math.cos(angle2), cy - cr2 * math.sin(angle2)), 1)
        pygame.draw.arc(self.screen, color, (cx - cr1, cy - cr1, 2 * cr1, 2 * cr1), angle1, angle2, 1)
        pygame.draw.arc(self.screen, color, (cx - cr2, cy - cr2, 2 * cr2, 2 * cr2), angle1, angle2, 1)


        if text:
            point_xs = sum([cx + cr1 * math.cos(angle1), cx + cr1 * math.cos(angle2), cx + cr2 * math.cos(angle1), cx + cr2 * math.cos(angle2)]) / 4
            point_ys = sum([cy - cr1 * math.sin(angle1), cy - cr1 * math.sin(angle2), cy - cr2 * math.sin(angle1), cy - cr2 * math.sin(angle2)]) / 4
            textImage = self.font.render(text, True, color)
            self.screen.blit(textImage, (point_xs, point_ys))

    def draw_arc_y(self, i, cx, cy, cr1, cr2, color, condition_func1=lambda: False, condition_func2=lambda x: False):
        angle1 = i * math.pi / 4 + math.pi / 8
        angle2 = angle1 + math.pi / 4
        aa = (angle1 + angle2) / 2
        cxp, cyp = cx + (cr1 + cr2) / 2 * math.cos(aa), cy - (cr1 + cr2) / 2 * math.sin(aa)
        if not condition_func1():
            rr, rr2 = self.gui_config['y_outer_radius'], self.gui_config['y_inner_radius']
        else:
            rr, rr2 = self.gui_config['yh_outer_radius'], self.gui_config['yh_inner_radius']
            cxp, cyp = (cx + cxp) / 2, (cyp + cy) / 2
        for j in range(8):
            if not condition_func2(j):
                self.draw_arc(j, cxp, cyp, rr, rr2, color = color, text=self.code_table.return_code(i, j))
        return cxp, cyp

    # def get_inputkey(self):
    #     return [self.joystick.get_axis(i) for i in range(6)]

    def whichArc(self, x, y):
        angle = math.atan2(-y, x)
        if angle < 0:
            angle += 2 * math.pi
        for i in range(8):
            angle1 = i * math.pi / 4 + math.pi / 8
            angle2 = angle1 + math.pi / 4
            if angle1 < angle < angle2 or (angle1 - math.pi * 2) < angle < (angle2 - math.pi * 2):
                return i
        return -1


    def draw_gui(self):
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        pygame.display.set_caption("Hello World!")

        circle_center = self.window_size / 2

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            @self.joystick.event
            def on_button(button, pressed):
                pass


            @self.joystick.event
            def on_axis(axis, value):
                # print('axis', axis, value)
                if axis == 'l_thumb_x':
                    self.lx = value * 2
                elif axis == 'l_thumb_y':
                    self.ly = - value * 2
                elif axis == 'r_thumb_x':
                    self.rx = value * 2
                elif axis == 'r_thumb_y':
                    self.ry = - value * 2
                elif axis == 'left_trigger':
                    self.lt = value
                elif axis == 'right_trigger':
                    self.rt = value


            # self.lx, self.ly, self.rx, self.ry, self.lt, self.rt = self.get_inputkey()
            isLTPress = self.lt > self.gui_config['trigger_threshold']
            isRTPress = self.rt > self.gui_config['trigger_threshold']

            # thumbL location
            pygame.draw.circle(self.screen, (255,0,0), (circle_center + self.lx * self.gui_config['x_outer_radius'], circle_center + self.ly * self.gui_config['x_outer_radius']), 10)

            isLActivate = eucli_dist((self.lx * self.gui_config['x_outer_radius'], self.ly * self.gui_config['x_outer_radius']), (0, 0)) > self.gui_config['x_inner_radius']
            isRActivate = eucli_dist((self.rx * self.gui_config['y_outer_radius'], self.ry * self.gui_config['y_outer_radius']), (0, 0)) > self.gui_config['y_inner_radius']
            l_arc = self.whichArc(self.lx, self.ly)
            r_arc = self.whichArc(self.rx, self.ry)



            for i in range(8):
                angle1 = i * math.pi / 4 + math.pi / 8
                angle2 = angle1 + math.pi / 4

                if isLActivate:
                    color = (50, 50, 50)
                else:
                    color = (255, 255, 255)
                self.draw_arc(i, circle_center, circle_center, self.gui_config['x_outer_radius'], self.gui_config['x_inner_radius'], color)
                crx, cry = self.draw_arc_y(i, circle_center, circle_center, self.gui_config['x_outer_radius'], self.gui_config['x_inner_radius'], color)
                if not isLActivate:
                    pygame.draw.circle(self.screen, (0,0,255), (crx + self.rx * self.gui_config['y_outer_radius'], cry + self.ry * self.gui_config['y_outer_radius']), 5)

            if isRActivate and not isLActivate:
                for i in range(8):
                    angle1 = i * math.pi / 4 + math.pi / 8
                    angle2 = angle1 + math.pi / 4

                    self.draw_arc_y(i, circle_center, circle_center, self.gui_config['x_outer_radius'], self.gui_config['x_inner_radius'], (0, 0, 255), lambda: False, lambda x: x != r_arc)

            if isLActivate:
                for i in range(8):
                    angle1 = i * math.pi / 4 + math.pi / 8
                    angle2 = angle1 + math.pi / 4

                    if i == l_arc:
                        color = (255, 0, 0)
                        crx, cry = self.draw_arc_y(i, circle_center, circle_center, self.gui_config['x_outer_radius'], self.gui_config['x_inner_radius'], color, lambda: True)
                        pygame.draw.circle(self.screen, (0,0,255), (crx + self.rx * self.gui_config['yh_outer_radius'], cry + self.ry * self.gui_config['yh_outer_radius']), 8)
                        if isRActivate:
                            self.draw_arc_y(i, circle_center, circle_center, self.gui_config['x_outer_radius'], self.gui_config['x_inner_radius'], (0, 0, 255), lambda: True, lambda x: x != r_arc)


            if isLActivate and isRActivate and (isRTPress and not self.lastRTPress):
                print("isPress", l_arc, r_arc)
                print(self.code_table.return_code(l_arc, r_arc))
                self.keyboard.press(self.code_table.return_code(l_arc, r_arc))
                self.keyboard.release('a')


            self.lastRTPress = isRTPress
            self.lastLTPress = isLTPress
            pygame.display.update()
            self.joystick.dispatch_events()
            self.screen.fill((0,0,0))


if __name__ == '__main__':
    pygame.init()
    c = JoystickInput()
    c.draw_gui()
