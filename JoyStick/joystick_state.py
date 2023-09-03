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
