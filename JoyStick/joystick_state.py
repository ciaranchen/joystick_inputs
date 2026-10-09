# coding: utf-8
"""
手柄状态 - 通过 Qt Property 绑定到 QML。

属性变更时才触发 Qt 信号，避免重复刷新。
"""
from PySide2.QtCore import QObject

from InputConfig import JoyStickButtons
from utils import PropertyMeta, Property


class JoyStickState(QObject, metaclass=PropertyMeta):
    lx = Property(float)
    ly = Property(float)
    rx = Property(float)
    ry = Property(float)

    buttons = Property(list)
    lt = Property(bool)
    rt = Property(bool)

    def __init__(self):
        super().__init__()
        self.lx = 0.0
        self.ly = 0.0
        self.rx = 0.0
        self.ry = 0.0
        self.lt = False
        self.rt = False
        self.buttons = [False] * JoyStickButtons.get_size()

    def set_axis(self, attr: str, value: float, dead_zone: float = 0.15):
        """设置轴值，低于死区的归零，仅在值变化时更新。"""
        if abs(value) < dead_zone:
            value = 0.0
        old = getattr(self, attr)
        if old != value:
            setattr(self, attr, value)

    def set_trigger(self, attr: str, value: bool):
        """设置 trigger 状态，仅在值变化时更新。"""
        old = getattr(self, attr)
        if old != value:
            setattr(self, attr, value)
