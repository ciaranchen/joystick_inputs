from pygame_joysticks import XBoxHandler as Handler
from input_method_config import BasicConfig as IMC
from code_table import SingleEnglishCode as CodeTable
import pygame
import math
import win32api
import win32con
import win32gui

fuchsia = (255, 0, 128)  # Transparency color
dark = (0, 0, 0)


class GuiStyle:
    # base color
    base_color = (255, 255, 255)  # white

    # axis color
    l_handle_color = (255, 0, 0)  # red
    r_handle_color = (255, 255, 0)  # blue


class JoystickGui(object):
    def __init__(self):
        self.window_size = 600
        self.screen = pygame.display.set_mode((self.window_size * 2, self.window_size))

        self.code_table = CodeTable
        self.imc = IMC(self.code_table)
        self.handler = Handler(self.imc)
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0

        self.font = pygame.font.Font(None, 30)
        self.gui_config = {
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

    def draw_panel(self, arc_number, start_arc, cx, cy, r1, r2, texts, gap=40):
        pygame.draw.circle(self.screen, GuiStyle.base_color,
                           (cx, cy), r2, width=1)
        textImage = self.font.render(texts[0], True, GuiStyle.base_color)
        # self.screen.blit(textImage, (, ))
        # TODO：写在圆心
        for i in range(arc_number):
            a1 = start_arc + i * math.pi * 2 / arc_number
            a2 = a1 + math.pi * 2 / arc_number
            self.draw_arc(a1 + (math.pi / gap), a2 - (math.pi / gap), cx, cy, r1, r2 + 0.1 * (r1 - r2),
                          text=texts[i + 1])

    def draw_arc(self, a1, a2, cx, cy, cr1, cr2, color=GuiStyle.base_color, text=None):
        pygame.draw.line(self.screen, color,
                         (cx + cr1 * math.cos(a1), cy - cr1 * math.sin(a1)),
                         (cx + cr2 * math.cos(a1), cy - cr2 * math.sin(a1)))
        pygame.draw.line(self.screen, color,
                         (cx + cr1 * math.cos(a2), cy - cr1 * math.sin(a2)),
                         (cx + cr2 * math.cos(a2), cy - cr2 * math.sin(a2)))
        pygame.draw.arc(self.screen, color, (cx - cr1, cy - cr1, 2 * cr1, 2 * cr1), a1, a2)
        pygame.draw.arc(self.screen, color, (cx - cr2, cy - cr2, 2 * cr2, 2 * cr2), a1, a2)

        if text:
            point_xs = sum([cx + cr1 * math.cos(a1), cx + cr1 * math.cos(a2), cx + cr2 * math.cos(a1),
                            cx + cr2 * math.cos(a2)]) / 4
            point_ys = sum([cy - cr1 * math.sin(a1), cy - cr1 * math.sin(a2), cy - cr2 * math.sin(a1),
                            cy - cr2 * math.sin(a2)]) / 4
            textImage = self.font.render(text, True, color)
            self.screen.blit(textImage, (point_xs, point_ys))

    def draw_gui(self):
        self.screen.set_alpha(192)
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

            # draw Left Axis
            pygame.draw.circle(self.screen, GuiStyle.l_handle_color,
                               (l_center[0] + self.lx * self.gui_config['x_outer_radius'],
                                l_center[1] + self.ly * self.gui_config['x_outer_radius']),
                               10)
            self.draw_panel(self.code_table.LNum, self.imc.start_arc(self.code_table.LNum),
                            l_center[0], l_center[1], self.window_size / 2,
                            self.window_size / 2 * self.imc.arc_threshold,
                            ['a', 'a', 'a', 'a', 'a'])

            # draw Right Axis
            pygame.draw.circle(self.screen, GuiStyle.r_handle_color,
                               (r_center[0] + self.rx * self.gui_config['x_outer_radius'],
                                r_center[1] + self.ry * self.gui_config['x_outer_radius']),
                               10)
            self.draw_panel(self.code_table.RNum, self.imc.start_arc(self.code_table.RNum),
                            r_center[0], r_center[1], self.window_size / 2,
                            self.window_size / 2 * self.imc.arc_threshold,
                            'a' * 9)

            pygame.display.update()


if __name__ == '__main__':
    jg = JoystickGui()
    jg.draw_gui()
