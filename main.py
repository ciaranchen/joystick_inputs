# This Python file uses the following encoding: utf-8
import sys
import os
from typing import Optional

import pygame
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QUrl, QTimer

from InputConfig.input_config import ArcJoyStickConfig
from JoyStick.joystick_state import JoyStickState
from JoyStick.pygame_joysticks import JoystickEventHandler, XBoxEventHandler, JoyConEventHandler
from src.core import InputManagerCore


class Main:
    def __init__(self):
        pygame.init()
        self.joy_classes = [XBoxEventHandler]
        self.joy: Optional[JoystickEventHandler] = None
        self.core = InputManagerCore(r"C:\Users\ciaran\Desktop\Projects\joystick_inputs\configs\code6.json")

    def init(self, state: JoyStickState):
        print('Waiting for Joy Stick connection...')
        while self.joy is None:
            events = pygame.event.get()
            for event in events:
                if not hasattr(event, 'device_index'):
                    continue
                joy = pygame.joystick.Joystick(event.device_index)
                for x in self.joy_classes:
                    j = x.joy_add(joy, state)
                    if j:
                        print(j.type_name)
                        self.joy = j

    def loop(self):
        events = pygame.event.get()
        for event in events:
            if self.joy and event.type == pygame.JOYDEVICEREMOVED:
                # TODO: deal with delete device.
                self.joy = None
            self.joy.handle_events(event, self.core.action)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    state = JoyStickState()
    engine.rootContext().setContextProperty("Joy", state)

    qml_file = os.path.join(os.path.dirname(__file__), "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    # 初始化MainLoop
    m = Main()
    m.init(state)

    # 添加定时器以执行循环中的操作
    timer = QTimer()
    timer.timeout.connect(m.loop)
    timer.start(100)  # 每隔0.1秒执行一次循环中的操作

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
