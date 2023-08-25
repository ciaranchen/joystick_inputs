from PySide2.QtCore import QObject

from InputConfig.config_schema import SUPPORT_BUTTONS
from JoyStick.qt_decorator import PropertyMeta, Property


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
        self.buttons = [False] * SUPPORT_BUTTONS
