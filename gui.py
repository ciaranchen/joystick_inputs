from ctypes import windll

from pynput.keyboard import Controller

from pygame_joysticks import XBoxHandler as Handler
from input_method_config import BasicConfig as IMC
from code_table import SingleEnglishCode as CodeTable
import pygame
import math
import win32api
import win32con
import win32gui

fuchsia = (255, 255, 255)  # Transparency color
dark = (0, 0, 0)


def limit_to(number, lower, upper):
    if number < lower:
        return lower
    if number > upper:
        return upper
    return number


class GuiStyle:
    # base color
    base_color = 0x808080  # white
    font_color = (0, 0, 0)

    # axis color
    l_handle_color = 0x01ffe9  # Nintendo Blue
    r_handle_color = 0xfe0016  # Nintendo Red


class JoystickGui(object):
    def __init__(self):
        self.window_size = 400
        self.screen = pygame.display.set_mode((self.window_size * 2, self.window_size),
                                              pygame.NOFRAME | pygame.RESIZABLE)
        self.keyboard = Controller()
        self.start_pos = (0, 0)

        self.code_table = CodeTable()
        self.imc = IMC(self.code_table)
        self.handler = Handler()
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0

        self.font = pygame.font.Font(None, 30)
        self.gui_config = {
            'radius_gap': self.window_size / 20,
            'l_radius': self.window_size / 2,
            'r_radius': self.window_size / 2,

            'x_inner_radius': self.window_size / 6,
            'x_outer_radius': self.window_size / 2,
            'y_inner_radius': self.window_size / 20,
            'y_outer_radius': self.window_size / 8,
            'yh_inner_radius': self.window_size / 10,
            'yh_outer_radius': self.window_size / 4
        }

        self.mouse_pressed = False
        # Create layered window
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

    def handle_axis(self, events):
        for e in events:
            if e.type == pygame.JOYAXISMOTION:
                if e.instance_id == self.handler.joy.get_instance_id() and e.axis in self.handler.LR_AXIS:
                    if e.axis == self.handler.LR_AXIS[0]:
                        self.lx = limit_to(e.value, -1, 1)
                    elif e.axis == self.handler.LR_AXIS[1]:
                        self.ly = limit_to(e.value, -1, 1)
                    elif e.axis == self.handler.LR_AXIS[2]:
                        self.rx = limit_to(e.value, -1, 1)
                    elif e.axis == self.handler.LR_AXIS[3]:
                        self.ry = limit_to(e.value, -1, 1)

    def moveWin(self, coordinates):
        # the handle to the window
        hwnd = pygame.display.get_wm_info()['window']

        # user32.MoveWindow also recieves a new size for the window
        w, h = pygame.display.get_surface().get_size()
        windll.user32.MoveWindow(hwnd, -coordinates[0], -coordinates[1], w, h, False)

    def draw_panel(self, arc_number, start_arc, number, choice_color, cx, cy, r1, r2, texts, gap=40):
        pygame.draw.circle(self.screen, GuiStyle.base_color, (cx, cy), r2)
        if number == 0:
            pygame.draw.circle(self.screen, choice_color, (cx, cy), r2, width=5)
        textImage = self.font.render(texts[0], True, GuiStyle.base_color)
        self.screen.blit(textImage, (cx, cy))
        for i in range(arc_number):
            a1 = start_arc + i * math.pi * 2 / arc_number
            a2 = a1 + math.pi * 2 / arc_number
            arc_color = choice_color if i + 1 == number else GuiStyle.base_color
            self.draw_arc(
                a1 + (math.pi / gap), a2 - (math.pi / gap),
                cx, cy,
                r1 - self.gui_config['radius_gap'],
                r2 + self.gui_config['radius_gap'],
                color=arc_color, text=texts[i + 1])

    def draw_arc(self, a1, a2, cx, cy, cr1, cr2, color, text):
        def arc_line_points(x, y, r, _a1=a1, _a2=a2):
            return [
                (x + r * math.cos((n * (_a2 - _a1) / 180 + _a1)),
                 y - r * math.sin((n * (_a2 - _a1) / 180 + _a1)))
                for n in range(181)  # 0-180
            ]

        p1 = arc_line_points(cx, cy, cr1)
        # print(p1)
        p2 = arc_line_points(cx, cy, cr2)
        p2.reverse()
        # Shape Color
        pygame.draw.polygon(self.screen, GuiStyle.base_color, p1 + p2)

        # Edge
        if color != GuiStyle.base_color:
            pygame.draw.line(self.screen, color, p1[0], p2[-1], width=5)
            pygame.draw.line(self.screen, color, p1[-1], p2[0], width=5)
            pygame.draw.arc(self.screen, color, (cx - cr1, cy - cr1, 2 * cr1, 2 * cr1), a1, a2, width=5)
            pygame.draw.arc(self.screen, color, (cx - cr2, cy - cr2, 2 * cr2, 2 * cr2), a1, a2, width=5)

        # Text
        point_4 = [p1[0], p1[-1], p2[-1], p2[0]]
        point_xy = (sum([p[0] for p in point_4]) / 4, sum([p[1] for p in point_4]) / 4)
        textImage = self.font.render(text, True, GuiStyle.font_color)
        self.screen.blit(textImage, point_xy)

    def draw_gui(self):
        self.mouse_pressed = False
        start_pos = []

        self.screen.set_alpha(128)
        # Lcircle_center = self.window_size / 2
        l_center = (self.window_size / 2, self.window_size / 2)
        r_center = (self.window_size * 3 / 2, self.window_size / 2)

        clock = pygame.time.Clock()
        joysticks = {}
        window_coords = [0, 0]
        self.moveWin(window_coords)

        while True:
            self.screen.fill(fuchsia)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_pressed = True
                    start_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEMOTION:
                    if self.mouse_pressed:
                        new_pos = pygame.mouse.get_pos()
                        window_coords[0] += start_pos[0] - new_pos[0]
                        window_coords[1] += start_pos[1] - new_pos[1]
                        self.moveWin(window_coords)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_pressed = False

                # Handle hotplugging
                if event.type == pygame.JOYDEVICEADDED:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks[joy.get_instance_id()] = joy
                    print(f"Joystick {joy.get_instance_id()} connencted")

                if event.type == pygame.JOYDEVICEREMOVED:
                    del joysticks[event.instance_id]
                    print(f"Joystick {event.instance_id} disconnected")

            self.handler.refresh(joysticks)

            self.handle_axis(events)

            l_arc_id, r_arc_id = self.imc.get_arcs(self.lx, self.ly, self.rx, self.ry)
            l_keys, r_keys = self.code_table.get_recommend(l_arc_id, r_arc_id)

            def press_key(lx, ly, rx, ry):
                la, ra = self.imc.get_arcs(lx, ly, rx, ry)
                code = self.code_table.get_code(la, ra)
                self.keyboard.tap(code)

            if self.handler.binding:
                self.handler.handle_trigger(events, press_key)

            # draw Left Axis
            self.draw_panel(self.code_table.LNum, self.imc.start_arc(self.code_table.LNum),
                            l_arc_id, GuiStyle.l_handle_color,
                            l_center[0], l_center[1], self.window_size / 2,
                            self.window_size / 2 * self.imc.arc_threshold,
                            l_keys)
            pygame.draw.circle(self.screen, GuiStyle.l_handle_color,
                               (l_center[0] + self.lx * self.gui_config['l_radius'],
                                l_center[1] + self.ly * self.gui_config['l_radius']),
                               10)

            # draw Right Axis
            self.draw_panel(self.code_table.RNum, self.imc.start_arc(self.code_table.RNum),
                            r_arc_id, GuiStyle.r_handle_color,
                            r_center[0], r_center[1], self.window_size / 2,
                            self.window_size / 2 * self.imc.arc_threshold,
                            r_keys)
            pygame.draw.circle(self.screen, GuiStyle.r_handle_color,
                               (r_center[0] + self.rx * self.gui_config['r_radius'],
                                r_center[1] + self.ry * self.gui_config['r_radius']),
                               10)

            pygame.display.flip()
            clock.tick(30)


if __name__ == '__main__':
    jg = JoystickGui()
    jg.draw_gui()
