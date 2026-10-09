# coding: utf-8
"""
手柄输入法 - 主入口

使用 Qt/QML 作为 UI 框架，pygame 处理手柄输入。
"""
import sys
import os
from typing import Optional

import pygame
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QUrl, QTimer

from JoyStick.joystick_state import JoyStickState
from JoyStick.pygame_joysticks import JoystickEventHandler, XBoxEventHandler
from src.core import ArcInputCore

# 默认配置文件（相对于本文件）
DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), "configs", "code6.json")

# 轮询间隔（毫秒）：16ms ≈ 60Hz，兼顾低延迟和 CPU 占用
POLL_INTERVAL_MS = 16


class Main:
    def __init__(self, config_path: str = DEFAULT_CONFIG):
        pygame.init()
        self.joy_classes = [XBoxEventHandler]
        self.joy: Optional[JoystickEventHandler] = None
        self.state: Optional[JoyStickState] = None
        self.core = ArcInputCore(config_path)

    def try_connect(self):
        """非阻塞：尝试连接手柄，连接到后打印提示。"""
        events = pygame.event.get()
        for event in events:
            if not hasattr(event, 'device_index'):
                continue
            joy = pygame.joystick.Joystick(event.device_index)
            for cls in self.joy_classes:
                j = cls.joy_add(joy, self.state)
                if j:
                    print(f"已连接: {j.type_name}")
                    self.joy = j
                    return

    def loop(self):
        """QTimer 回调：轮询 pygame 事件。"""
        events = pygame.event.get()

        # 如果还没连上，继续尝试
        if self.joy is None:
            for event in events:
                if hasattr(event, 'device_index'):
                    joy = pygame.joystick.Joystick(event.device_index)
                    for cls in self.joy_classes:
                        j = cls.joy_add(joy, self.state)
                        if j:
                            print(f"已连接: {j.type_name}")
                            self.joy = j
            return

        for event in events:
            if event.type == pygame.JOYDEVICEREMOVED:
                print("手柄已断开")
                self.joy = None
                return
            self.joy.handle_events(event, self.core.action)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    state = JoyStickState()
    engine.rootContext().setContextProperty("Joy", state)

    qml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    # 启动主循环（非阻塞：Qt 事件循环驱动 pygame 轮询）
    m = Main()
    m.state = state

    timer = QTimer()
    timer.timeout.connect(m.loop)
    timer.start(POLL_INTERVAL_MS)

    print(f"轮询间隔: {POLL_INTERVAL_MS}ms")
    print("等待手柄连接...")

    sys.exit(app.exec_())
