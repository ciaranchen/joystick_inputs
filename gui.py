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


class GuiStyle:
    # base color
    base_color = 0x808080  # white
    font_color = (0, 0, 0)

    # axis color
    l_handle_color = 0x01ffe9  # Nintendo Blue
    r_handle_color = 0xfe0016  # Nintendo Red


class JoystickGui(object):
    def __init__(self):
        self.window_size = 600
        self.screen = pygame.display.set_mode((self.window_size * 2, self.window_size))

        self.code_table = CodeTable()
        self.imc = IMC(self.code_table)
        self.handler = Handler(self.imc)
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0

        self.font = pygame.font.Font(None, 30)
        self.gui_config = {
            'radius_gap': self.window_size / 20,

            'x_inner_radius': self.window_size / 6,
            'x_outer_radius': self.window_size / 2,
            'y_inner_radius': self.window_size / 20,
            'y_outer_radius': self.window_size / 8,
            'yh_inner_radius': self.window_size / 10,
            'yh_outer_radius': self.window_size / 4
        }

        # Create layered window
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

    def handle_axis(self, events):
        for e in events:
            if e.type == pygame.JOYAXISMOTION:
                if e.instance_id == self.handler.joy.get_instance_id() and e.axis_id in self.handler.LR_AXIS:
                    if e.axis_id == self.handler.LR_AXIS[0]:
                        self.lx = e.value
                    elif e.axis_id == self.handler.LR_AXIS[1]:
                        self.ly = e.value
                    elif e.axis_id == self.handler.LR_AXIS[2]:
                        self.rx = e.value
                    elif e.axis_id == self.handler.LR_AXIS[3]:
                        self.ry = e.value

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
                 y + r * math.sin((n * (_a2 - _a1) / 180 + _a1)))
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
        self.screen.set_alpha(128)
        self.screen.fill(fuchsia)
        # Lcircle_center = self.window_size / 2
        l_center = (self.window_size / 2, self.window_size / 2)
        r_center = (self.window_size * 3 / 2, self.window_size / 2)

        clock = pygame.time.Clock()

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            # print(events)

            self.handle_axis(events)
            l_keys, r_keys = self.imc.get_recommend(self.lx, self.ly, self.rx, self.ry)
            # print(l_keys, r_keys)

            # draw Left Axis
            self.draw_panel(self.code_table.LNum, self.imc.start_arc(self.code_table.LNum),
                            0, GuiStyle.l_handle_color,
                            l_center[0], l_center[1], self.window_size / 2,
                            self.window_size / 2 * self.imc.arc_threshold,
                            l_keys)
            pygame.draw.circle(self.screen, GuiStyle.l_handle_color,
                               (l_center[0] + self.lx * self.gui_config['x_outer_radius'],
                                l_center[1] + self.ly * self.gui_config['x_outer_radius']),
                               10)

            # draw Right Axis
            self.draw_panel(self.code_table.RNum, self.imc.start_arc(self.code_table.RNum),
                            0, GuiStyle.r_handle_color,
                            r_center[0], r_center[1], self.window_size / 2,
                            self.window_size / 2 * self.imc.arc_threshold,
                            r_keys)
            pygame.draw.circle(self.screen, GuiStyle.r_handle_color,
                               (r_center[0] + self.rx * self.gui_config['x_outer_radius'],
                                r_center[1] + self.ry * self.gui_config['x_outer_radius']),
                               10)

            pygame.display.flip()


if __name__ == '__main__':
    jg = JoystickGui()
    jg.draw_gui()
