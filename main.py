# This Python file uses the following encoding: utf-8
import sys
import os
import time
from dataclasses import dataclass

import pygame
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, Slot, QUrl, QTimer, Signal, Property

from InputConfig.input_config import ArcJoyStickConfig
from qt_decorator import PropertyMeta, Property
from pygame_joysticks import JoystickEventHandler, XBoxEventHandler, JoyConEventHandler
from src.core import InputManagerCore


class JoyStickState(QObject, metaclass=PropertyMeta):
    lx = Property(float)
    ly = Property(float)
    rx = Property(float)
    ry = Property(float)

    buttons = Property(list)
    l_trigger = Property(bool)
    r_trigger = Property(bool)

    def __init__(self):
        super().__init__()
        self.lx = 0.0
        self.ly = 0.0
        self.rx = 0.0
        self.ry = 0.0
        self.l_trigger = False
        self.r_trigger = False
        self.buttons = []


class MainLoop:
    def __init__(self):
        pygame.init()
        self.joy_classes = [XBoxEventHandler, JoyConEventHandler]
        self.joy = None
        input_config = ArcJoyStickConfig.load_from(
            r"C:\Users\ciaran\Desktop\Projects\joystick_inputs\configs\code6.json")
        self.imc = InputManagerCore(input_config)

    def main(self):
        events = pygame.event.get()
        for event in events:
            # Handle hotplugging
            if not self.joy and event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                for x in self.joy_classes:
                    j = x.joy_add(joy)
                    if j:
                        self.joy = j
            if self.joy and event.type == pygame.JOYDEVICEREMOVED:
                j = None
            if self.joy:
                self.joy.handle_events(events, self.imc.action)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    state = JoyStickState()
    engine.rootContext().setContextProperty("Joy", state)

    qml_file = os.path.join(os.path.dirname(__file__), "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    # 初始化MainLoop
    m = MainLoop()

    # 添加定时器以执行循环中的操作
    timer = QTimer()
    timer.timeout.connect(m.main)
    timer.start(1000)  # 每隔1秒执行一次循环中的操作

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
