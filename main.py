# coding: utf-8
from pygame_joysticks import XBoxEventHandler, JoyConEventHandler, JoyMode, XBoxExtendMode, JoyConExtendMode, \
    JoyConClickMode, XBoxClickMode
from pynput.keyboard import Controller as Keyboard
from pynput.mouse import Controller as Mouse
from input_method_config import IMCoreForAlternativeSix as InputMethodCore
from code_table import CodeExtension as CodeTable

import pygame
import os
import math
import win32api
import win32con
import win32gui
from ctypes import windll

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

fuchsia = (255, 255, 255)  # Transparency color
dark = (0, 0, 0)


class GuiStyle:
    # base color
    base_color = 0x808080  # Grey
    font_color = (0, 0, 0)

    # axis color
    l_handle_color = 0x01ffe9  # Nintendo Blue
    r_handle_color = 0xfe0016  # Nintendo Red


class BasicJoystickIM:
    """
    Base class for handler
    """

    def __init__(self):
        pygame.init()
        self.code_table = CodeTable()
        self.imc = InputMethodCore()
        self.keyboard = Keyboard()
        self.joy_classes = [XBoxEventHandler, JoyConEventHandler]
        self.bind_joys = []
        self.axis = {'lx': 0, 'ly': 0, 'rx': 0, 'ry': 0}

    def press_key(self, lx, ly, rx, ry):
        la, ra = self.imc.get_arcs(lx, ly, rx, ry, self.code_table.L_NUM, self.code_table.R_NUM)
        print(la, ra, self.code_table.code[la, ra])
        code = self.code_table.get_code(la, ra)
        self.keyboard.tap(code)

    def main(self):
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    exit()
                # Handle hotplugging
                if event.type == pygame.JOYDEVICEADDED:
                    print(event)
                    joy = pygame.joystick.Joystick(event.device_index)
                    for x in self.joy_classes:
                        j = x.joy_add(joy)
                        if j:
                            self.bind_joys.append(j)
                if event.type == pygame.JOYDEVICEREMOVED:
                    for j in self.bind_joys:
                        if j.joy_del(event):
                            self.bind_joys.remove(j)
            self.main_loop(events)
            clock.tick(30)

    def main_loop(self, events):
        for j in self.bind_joys:
            j.handle_button(events, self.keyboard, self.code_table)
            j.handle_axis(events, self.keyboard, self.code_table, self.axis)
            j.handle_trigger(events, self.keyboard, self.code_table, self.press_key)


class JoystickExtendIM(BasicJoystickIM):
    def __init__(self):
        super().__init__()
        self.mouse = Mouse()
        self.joy_classes = [XBoxExtendMode, JoyConExtendMode]

    def main_loop(self, events):
        for j in self.bind_joys:
            j.handle_button(events, self.keyboard, self.code_table)
            j.ex_handle_axis(events, self.keyboard, self.code_table, self.axis, self.mouse)
            j.ex_handle_trigger(events, self.keyboard, self.code_table, self.press_key, self.mouse)


class JoystickGui(JoystickExtendIM):
    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.mouse_pressed = False
        self.window_coords = [0, 0]
        self.window_size = 400

        self.font = pygame.font.Font(None, 30)
        self.gui_config = {
            'panel_gap': self.window_size / 10,
            'radius_gap': self.window_size / 20,
            'angle_gap': math.pi / 60,
            'l_radius': self.window_size / 2,
            'r_radius': self.window_size / 2,
        }

        self.gui_config['l_inner_radius'] = self.gui_config['l_radius'] * self.imc.arc_threshold
        self.gui_config['r_inner_radius'] = self.gui_config['r_radius'] * self.imc.arc_threshold

        self.l_center = (self.window_size / 2, self.window_size / 2)
        self.r_center = (self.window_size * 3 / 2 + self.gui_config['panel_gap'], self.window_size / 2)

        self.screen = pygame.display.set_mode(
            (self.window_size * 2 + self.gui_config['panel_gap'], self.window_size),
            pygame.NOFRAME | pygame.RESIZABLE)
        # Create layered window
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # set window top mose
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOOWNERZORDER | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

    @staticmethod
    def cube2circle(x, y):
        nx = x * math.sqrt(1 - y * y / 2)
        ny = y * math.sqrt(1 - x * x / 2)
        return nx, ny

    def draw_panel(self, arc_number, number, choice_color, cx, cy, r1, r2, texts, angle_gap):
        pygame.draw.circle(self.screen, GuiStyle.base_color, (cx, cy), r2)
        if number == 0:
            pygame.draw.circle(self.screen, choice_color, (cx, cy), r2, width=5)
        text_image = self.font.render(texts[0], True, GuiStyle.base_color)
        self.screen.blit(text_image, (cx, cy))
        for i, a1, a2 in zip(range(arc_number), self.imc.arcs(arc_number), self.imc.arcs(arc_number)[1:]):
            arc_color = choice_color if i + 1 == number else GuiStyle.base_color
            self.draw_arc(
                a1 + angle_gap, a2 - angle_gap,
                cx, cy,
                r1,
                r2 + self.gui_config['radius_gap'],
                color=arc_color, text=texts[i + 1])

    def draw_arc(self, a1, a2, cx, cy, cr1, cr2, color, text):
        def arc_line_points(x, y, r, _a1=a1, _a2=a2):
            return [
                (x + r * math.cos((n * (_a2 - _a1) / 180 + _a1)),
                 y + r * math.sin((n * (_a2 - _a1) / 180 + _a1)))
                for n in range(181)  # 0-180
            ]

        p1 = arc_line_points(cx, cy, cr1)
        p2 = arc_line_points(cx, cy, cr2)
        p2.reverse()
        # Shape Color
        pygame.draw.polygon(self.screen, GuiStyle.base_color, p1 + p2)

        # Edge
        if color != GuiStyle.base_color:
            pygame.draw.line(self.screen, color, p1[0], p2[-1], width=5)
            pygame.draw.line(self.screen, color, p1[-1], p2[0], width=5)
            pygame.draw.lines(self.screen, color, False, p1, width=5)
            pygame.draw.lines(self.screen, color, False, p2, width=5)

        # Text
        point_4 = [p1[0], p1[-1], p2[-1], p2[0]]
        point_xy = (sum([p[0] for p in point_4]) / 4, sum([p[1] for p in point_4]) / 4)
        text_image = self.font.render(text, True, GuiStyle.font_color)
        self.screen.blit(text_image, point_xy)

    def main(self):
        self.window_coords = [0, 0]
        self.refresh_win_location(self.window_coords)
        super().main()

    @staticmethod
    def refresh_win_location(coordinates):
        # the handle to the window
        hwnd = pygame.display.get_wm_info()['window']

        # user32.MoveWindow also recieves a new size for the window
        w, h = pygame.display.get_surface().get_size()
        windll.user32.MoveWindow(hwnd, -coordinates[0], -coordinates[1], w, h, False)

    def handle_mouse(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed = True
                self.start_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    new_pos = pygame.mouse.get_pos()
                    self.window_coords[0] += self.start_pos[0] - new_pos[0]
                    self.window_coords[1] += self.start_pos[1] - new_pos[1]
                    self.refresh_win_location(self.window_coords)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False

    def main_loop(self, events):
        self.handle_mouse(events)
        super().main_loop(events)
        l_arc_id, r_arc_id = self.imc.get_arcs(self.axis['lx'], self.axis['ly'], self.axis['rx'], self.axis['ry'],
                                               self.code_table.L_NUM, self.code_table.R_NUM)
        l_keys, r_keys = self.code_table.get_recommend(l_arc_id, r_arc_id)
        self.draw_gui(l_arc_id, r_arc_id, l_keys, r_keys)
        pygame.display.flip()

    def draw_gui(self, l_arc_id, r_arc_id, l_keys, r_keys):
        self.screen.fill(fuchsia)
        # draw Left Axis
        self.draw_panel(self.code_table.L_NUM, l_arc_id, GuiStyle.l_handle_color,
                        self.l_center[0], self.l_center[1],
                        self.gui_config['l_radius'],
                        self.gui_config['l_inner_radius'],
                        l_keys, self.gui_config['angle_gap'])
        lnx, lny = self.cube2circle(self.axis['lx'], self.axis['ly'])
        pygame.draw.circle(self.screen, GuiStyle.l_handle_color,
                           (self.l_center[0] + lnx * self.gui_config['l_radius'],
                            self.l_center[1] + lny * self.gui_config['l_radius']),
                           10)

        # draw Right Axis
        self.draw_panel(self.code_table.R_NUM, r_arc_id, GuiStyle.r_handle_color,
                        self.r_center[0], self.r_center[1],
                        self.gui_config['r_radius'],
                        self.gui_config['r_inner_radius'],
                        r_keys, self.gui_config['angle_gap'])
        rnx, rny = self.cube2circle(self.axis['rx'], self.axis['ry'])
        pygame.draw.circle(self.screen, GuiStyle.r_handle_color,
                           (self.r_center[0] + rnx * self.gui_config['r_radius'],
                            self.r_center[1] + rny * self.gui_config['r_radius']),
                           10)


class JoystickClickGui(JoystickGui):
    def __init__(self):
        super().__init__()
        self.last_axis = [0, 0]
        self.joy_classes = [JoyConClickMode, XBoxClickMode]

    def press_key(self, lx, ly, rx, ry):
        print(self.last_axis[0], self.last_axis[1], self.code_table.code[self.last_axis[0], self.last_axis[1]])
        code = self.code_table.get_code(self.last_axis[0], self.last_axis[1])
        self.keyboard.tap(code)
        for i in range(2):
            self.last_axis[i] = 0

    def main_loop(self, events):
        self.handle_mouse(events)
        for j in self.bind_joys:
            j.click_handle_button(events, self.keyboard, self.code_table, self.last_axis)
            j.ex_handle_axis(events, self.keyboard, self.code_table, self.axis, self.mouse)
            j.ex_handle_trigger(events, self.keyboard, self.code_table, self.press_key, self.mouse)
        l_arc_id, r_arc_id = self.imc.get_arcs(self.axis['lx'], self.axis['ly'], self.axis['rx'], self.axis['ry'],
                                               self.code_table.L_NUM, self.code_table.R_NUM)
        if l_arc_id != 0:
            self.last_axis[0] = l_arc_id
        if r_arc_id != 0:
            self.last_axis[1] = r_arc_id
        l_keys, r_keys = self.code_table.get_recommend(self.last_axis[0], self.last_axis[1])

        self.draw_gui(self.last_axis[0], self.last_axis[1], l_keys, r_keys)
        pygame.display.flip()


if __name__ == '__main__':
    jg = JoystickGui()
    jg.main()
