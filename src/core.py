# coding: utf-8
"""
核心输入处理引擎 - 将手柄事件映射到配置的动作。

Arc 类负责将摇杆坐标 (x, y) 映射到扇区编号 (0~N)。
ArcInputCore 是上层接口，加载配置并分发动作回调。
"""
import math
import os
from typing import Optional

from InputConfig import ArcJoyStickConfig, JoyStickFunctionController, JoyStickButtons


class Arc:
    """
    扇区划分器。

    中心区域（距原点 < arc_threshold）为扇区 0（死区），
    周围区域按角度均分为 1~N 号扇区，1 号从正上方开始。
    """
    arc_threshold = 0.3

    @staticmethod
    def start_arc(num: int) -> float:
        """返回第一个扇区的起始角度（让扇区 1 居中在正上方）。"""
        return -math.pi / num - math.pi / 2

    @classmethod
    def arcs(cls, num: int) -> list:
        """返回 num+1 个角度边界（首尾相接）。"""
        return [cls.start_arc(num) + i * (2 * math.pi / num) for i in range(num + 1)]

    @staticmethod
    def arc_distance(x: float, y: float) -> float:
        return math.sqrt(x * x + y * y)

    @classmethod
    def which_arc(cls, x: float, y: float, arc_num: int) -> int:
        """
        根据坐标返回扇区编号。
        返回 0 表示在死区内，返回 -1 表示计算异常。
        """
        if cls.arc_distance(x, y) < cls.arc_threshold:
            return 0
        angle = math.atan2(y, x)
        boundaries = cls.arcs(arc_num)
        if angle < boundaries[0]:
            angle += 2 * math.pi
        for i in range(arc_num):
            a1, a2 = boundaries[i], boundaries[i + 1]
            if a1 <= angle < a2 or a1 <= (angle - 2 * math.pi) < a2:
                return i + 1
        return -1


class ArcInputCore(Arc):
    """输入引擎：加载配置，分发手柄事件到对应动作。"""

    def __init__(self, config_path: str):
        self.config = ArcJoyStickConfig.load_from(config_path)
        self.layer = self.config.default_layer
        self.last_layer = self.layer  # 用于 hold_to_layer 恢复
        self.config.load_controller(JoyStickFunctionController())
        print(f"已加载配置: {self.config.config_name}, 默认层: {self.layer}")

    def action(self, joy, event_type,
               button: Optional[JoyStickButtons] = None,
               trigger: Optional[bool] = None,
               axis: bool = False):
        """
        分发手柄事件到配置中定义的动作。

        参数:
            joy:        手柄状态对象 (JoyStickState)
            event_type: pygame 事件类型 (JOYBUTTONDOWN / JOYBUTTONUP)
            button:     按钮枚举（非 None 时按按钮查表）
            trigger:    True=右 trigger, False=左 trigger（非 None 时按 trigger 查表）
            axis:       True 表示轴移动事件（当前仅 axis_layer 响应）
        """
        now_layer = self.config.layers[self.layer]

        if trigger is not None:
            # trigger 索引：0=左, 1=右
            func = now_layer.trigger[1 if trigger else 0]
            func(self, joy, event_type)
        elif button is not None:
            func = now_layer.buttons[button.value]
            func(self, joy, event_type)
        elif axis:
            if now_layer.is_axis_layer:
                # TODO: 将轴移动也作为可配置的连续输入
                pass
        else:
            raise ValueError(f"action() 需要 button, trigger 或 axis 参数, 但全部为 None")


if __name__ == '__main__':
    import pygame

    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "code6.json")
    aic = ArcInputCore(config_path)
    aic.action(None, pygame.JOYBUTTONDOWN, trigger=False)
    aic.action(None, pygame.JOYBUTTONUP, trigger=False)
