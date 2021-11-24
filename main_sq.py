import pygame
import sys, itertools
import time
import math
from code_table import CodeTable
from xinput import XInputJoystick
from pynput.keyboard import Key, Controller
from operator import itemgetter, attrgetter
import win32api
import win32con
import win32gui

eucli_dist = lambda x, y: math.sqrt((x[0]-y[0]) ** 2 + (x[1]-y[1]) ** 2)


fuchsia = (100, 100, 100)  # Transparency color
done = False
dark = (0,0,0)

class ColorConfig(object):
    def __init__(self):
        self.basic_color = (0,0,0) # Black
        self.hidden_color = (200,200,200) # Gray
        self.L_selected_color = (0,0,255) # Blue
        self.R_selected_color = (255,0,0) # Red

class GUIConfig(object):
    def __init__(self, window_w, window_h):
        self.window_w = window_w
        self.window_h = window_h
        white_space = lambda x, y: 2 * ( x + y )
        calc_size = lambda x, y, ws: ((x - ws) / 3, (y - ws) / 3)

        self.outer_s_margin = 5
        self.outer_margin = 10
        self.outer_w, self.outer_h = calc_size(window_w, window_h, white_space(self.outer_margin, self.outer_s_margin))

        self.inner_margin = 10
        self.inner_s_margin = 5
        self.inner_w, self.inner_h = calc_size(self.outer_w, self.outer_h, white_space(self.inner_margin, self.inner_s_margin))

        self.hidden_margin = 20
        self.hidden_s_margin = 20
        self.hidden_w, self.hidden_h = 300, 400

        self.outer_line_width, self.inner_line_width, self.hidden_line_width = 3, 3, 3

        self.thumb_threshold = 0.4
        self.trigger_threshold = 0.3
        self.side_angle = math.pi / 30

    def to_json(self):
        pass

class JoystickWrapper():
    @staticmethod
    def whichArc(x, y):
        angle = math.atan2(-y, x)
        if angle < 0:
            angle += 2 * math.pi
        for i in range(8):
            angle1 = i * math.pi / 4 + math.pi / 8
            angle2 = angle1 + math.pi / 4
            if angle1 < angle < angle2 or (angle1 - math.pi * 2) < angle < (angle2 - math.pi * 2):
                return (i+3) % 8
        return -1

    def __init__(self, config, code_map):
        self.config = config
        self.code_map = code_map
        self.keyboard = Controller()
        self.joystick = self.get_joystick()
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0
        self.lt, self.rt = 0, 0
        self.isLTPress, self.isRTPress = False, False
        self.lastLTPress, self.lastRTPress = False, False
        self.isLActivate, self.isRActivate = False, False
        self.axis_update()
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
            self.axis_update()

    def get_joystick(self):
        joysticks = XInputJoystick.enumerate_devices()
        device_numbers = list(map(attrgetter('device_number'), joysticks))

        print('found %d devices: %s' % (len(joysticks), device_numbers))

        if not joysticks:
            return None
        return joysticks[0]


    def axis_update(self):
        self.lastRTPress = self.isRTPress
        self.lastLTPress = self.isLTPress
        self.isLTPress = self.lt > self.config.trigger_threshold
        self.isRTPress = self.rt > self.config.trigger_threshold
        self.isLActivate = eucli_dist((self.lx, self.ly), (0, 0)) > self.config.thumb_threshold
        self.isRActivate = eucli_dist((self.rx, self.ry), (0, 0)) > self.config.thumb_threshold
        self.l_arc = JoystickWrapper.whichArc(self.lx, -self.ly)
        self.r_arc = JoystickWrapper.whichArc(self.rx, -self.ry)
        # print(self.l_arc, self.r_arc)


    def step(self):
        self.joystick.dispatch_events()


    def debug_circle(self, screen, gui_config, color_config):
        center_x, center_y = gui_config.window_w / 2, gui_config.window_h / 2
        pygame.draw.circle(screen, color_config.basic_color, (center_x, center_y), gui_config.outer_h / 2, 3)
        pygame.draw.circle(screen, color_config.L_selected_color, (center_x + self.lx * (gui_config.outer_h / 2 - 5), center_y + self.ly * (gui_config.outer_h / 2 - 5)), 10)
        pygame.draw.circle(screen, color_config.R_selected_color, (center_x + self.rx * (gui_config.outer_h / 2 - 5), center_y + self.ry * (gui_config.outer_h / 2 - 5)), 10)


    def return_code(self, ix, iy):
        return self.code_map.return_code(ix, iy)

    def press_key(self, debug=False):

        key = self.code_map.return_code(self.l_arc, self.r_arc)
        if debug:
            print("isPress: ", self.l_arc, self.r_arc, "Key: ", key)
        self.joystick.set_vibration(self.lt, self.rt)
        return self.keyboard.press(key)

class InputMethodGUI(object):
    def __init__(self, debug=False):
        self.color = ColorConfig()
        self.window_x, self.window_y = 800, 600
        self.config = GUIConfig(self.window_x, self.window_y)
        self.joystick = JoystickWrapper(self.config, CodeTable)
        # self.screen = pygame.display.set_mode((self.window_size, self.window_size), pygame.NOFRAME)
        self.screen = pygame.display.set_mode((self.window_x, self.window_y))
        pygame.display.set_caption("Hello World!")
        self.debug = debug
        self.font = pygame.font.Font(None, 30)
        # Create layered window
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

    def write_text(self, ix, iy, x, y, color=(0,0,0)):
        text = self.joystick.return_code(ix, iy)
        text_w, text_h = self.font.size("txt")
        textImage = self.font.render(text, True, color)
        tx = (self.config.inner_w - text_w) / 2
        ty = (self.config.inner_h - text_h) / 2
        self.screen.blit(textImage, (x+tx, y + ty))

    @staticmethod
    def return_left_top(margin, width, height, sq_margin=0):
        non_center = [(sq_margin + (margin + width) * j, sq_margin + (margin + height) * i) for i, j in itertools.product(range(3), range(3))]
        # print(non_center)
        square_order = [(0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]
        # return [non_center[i * 3 + j] for i, j in square_order]
        return [non_center[i * 3 + j] for i, j in square_order]

    # def get_inputkey(self):
    #     return [self.joystick.get_axis(i) for i in range(6)]

    def draw_gui(self):
        while True:
            self.screen.fill(fuchsia)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # thumb location for debug
            if self.debug:
                self.joystick.debug_circle(self.screen, self.config, self.color)

            outer_left_tops = InputMethodGUI.return_left_top(self.config.outer_margin, self.config.outer_w, self.config.outer_h, self.config.outer_s_margin)
            inner_left_tops = InputMethodGUI.return_left_top(self.config.inner_margin, self.config.inner_w, self.config.inner_h, self.config.inner_s_margin)
            any_lr = self.joystick.isLActivate or self.joystick.isRActivate
            only_l = self.joystick.isLActivate and (not self.joystick.isRActivate)
            only_r = self.joystick.isRActivate and (not self.joystick.isLActivate)
            both_lr = self.joystick.isLActivate and self.joystick.isRActivate

            # TODO: show text on button.
            for i in range(8):
                l, t = outer_left_tops[i]
                # draw 8 square.
                if self.joystick.isLActivate and i == self.joystick.l_arc:
                    pygame.draw.rect(self.screen, self.color.L_selected_color, (l, t, self.config.outer_w, self.config.outer_h), self.config.outer_line_width)
                    for j in range(8):
                        il, it = inner_left_tops[j]
                        il, it = il + l, it + t
                        if self.joystick.isRActivate and self.joystick.r_arc == j:
                            pygame.draw.rect(self.screen, self.color.R_selected_color, (il, it, self.config.inner_w, self.config.inner_h), self.config.inner_line_width)
                            self.write_text(i, j, il, it, self.color.R_selected_color)
                            continue
                        color = self.color.hidden_color if self.joystick.isRActivate else self.color.basic_color
                        pygame.draw.rect(self.screen, color, (il, it, self.config.inner_w, self.config.inner_h), self.config.inner_line_width)
                        self.write_text(i, j, il, it, color)
                    continue

                color = self.color.hidden_color if any_lr else self.color.basic_color
                pygame.draw.rect(self.screen, color, (l, t, self.config.outer_w, self.config.outer_h), 3)
                
                
                for j in range(8):
                    il, it = inner_left_tops[j]
                    il += l
                    it += t
                    if only_r and j == self.joystick.r_arc:
                        pygame.draw.rect(self.screen, self.color.R_selected_color, (il, it, self.config.inner_w, self.config.inner_h), self.config.inner_line_width)
                        self.write_text(i, j, il, it, color)
                        continue
                    color = self.color.hidden_color if any_lr else self.color.basic_color
                    pygame.draw.rect(self.screen, color, (il, it, self.config.inner_w, self.config.inner_h), self.config.inner_line_width)
                    self.write_text(i, j, il, it, color)

            r_now_pressed = self.joystick.isRTPress and not self.joystick.lastRTPress
            if both_lr and r_now_pressed:
                self.joystick.press_key(debug=True)

            pygame.display.update()
            self.joystick.step()
            


if __name__ == '__main__':
    pygame.init()
    c = InputMethodGUI(True)
    c.draw_gui()
