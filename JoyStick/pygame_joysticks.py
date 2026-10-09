# coding: utf-8
"""
手柄事件管理 - 将 pygame 手柄事件转换为统一的回调调用。

支持 XBox 手柄（完整实现）和 JoyCon 手柄（框架/TODO）。

核心改进：
- 软件死区滤波：消除摇杆漂移导致的持续输入
- 仅在轴值实际变化时才触发回调，避免事件风暴
- 修复 trigger 参数 bug（原 t=='lr' 永远为 False）
"""
import enum
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional

import pygame

from InputConfig import JoyStickButtons

# 摇杆死区阈值：低于此值的输入视为零（消除漂移）
DEAD_ZONE = 0.15


def clamp(value: float, lower: float = -1.0, upper: float = 1.0) -> float:
    """将值限制在 [lower, upper] 范围内。"""
    return max(lower, min(upper, value))


class JoyMode(enum.Enum):
    NORMAL_MODE = 0
    MOTION_MODE = 1
    MOUSE_MODE = 2


class SingletonJoystickHandler(metaclass=ABCMeta):
    _instance = None

    @classmethod
    def joy_add(cls, joy, state):
        if cls._instance:
            return cls._instance
        raise NotImplementedError

    @abstractmethod
    def is_joy(self, instance_id: int) -> bool:
        raise NotImplementedError


@dataclass
class JoystickEventHandler(SingletonJoystickHandler):
    state = None

    @classmethod
    def joy_add(cls, joy, state):
        raise NotImplementedError

    @abstractmethod
    def is_joy(self, instance_id: int) -> bool:
        raise NotImplementedError

    def handle_events(self, event, callback):
        """分发事件到对应处理器。仅处理本手柄的事件。"""
        if not hasattr(event, 'instance_id'):
            return
        if not self.is_joy(event.instance_id):
            return
        self.handle_button(event, callback)
        self.handle_trigger(event, callback)
        self.handle_axis(event, callback)

    def handle_button(self, e, cb):
        raise NotImplementedError

    def handle_trigger(self, e, cb):
        raise NotImplementedError

    def handle_axis(self, e, cb):
        raise NotImplementedError

    def button_changed(self, button: JoyStickButtons, e_type, callback: Callable):
        """更新按钮状态并触发回调。"""
        self.state.buttons[button.value] = (e_type == pygame.JOYBUTTONDOWN)
        callback(self.state, e_type, button=button)


@dataclass
class XBoxEventHandler(JoystickEventHandler):
    """XBox 360 手柄事件处理器。"""

    axis_mapping: Dict[str, int] = field(default_factory=dict)
    button_mapping: Dict[int, JoyStickButtons] = field(default_factory=dict)
    hat_mapping_x: Dict[int, JoyStickButtons] = field(default_factory=dict)
    hat_mapping_y: Dict[int, JoyStickButtons] = field(default_factory=dict)
    joy: Optional[pygame.joystick.Joystick] = None
    state = None
    type_name: str = "Xbox 360 Controller"

    TRIGGER_THRESHOLD: float = 0.3
    LR_AXIS: tuple = (0, 1, 2, 3)
    last_hat_x: int = 0
    last_hat_y: int = 0

    @classmethod
    def joy_add(cls, joy, state):
        if joy.get_name() != cls.type_name:
            return None
        if cls._instance:
            return cls._instance

        res = cls()
        res.axis_mapping = {
            'lx': 0, 'ly': 1, 'rx': 2, 'ry': 3,
            'lt': 4, 'rt': 5,
        }
        res.button_mapping = {
            v.value: v for v in JoyStickButtons.__members__.values() if v.value < 6
        }
        res.button_mapping.update({
            8: JoyStickButtons.LStickIn,
            9: JoyStickButtons.RStickIn,
        })
        res.hat_mapping_x = {
            -1: JoyStickButtons.LLeftButton,
            1: JoyStickButtons.LRightButton,
        }
        res.hat_mapping_y = {
            -1: JoyStickButtons.LDownButton,
            1: JoyStickButtons.LUpButton,
        }
        res.joy = joy
        res.state = state
        cls._instance = res
        return res

    def is_joy(self, instance_id: int) -> bool:
        return self.joy is not None and instance_id == self.joy.get_instance_id()

    def handle_button(self, e, cb):
        if e.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            if e.button in self.button_mapping:
                self.button_changed(self.button_mapping[e.button], e.type, cb)

        elif e.type == pygame.JOYHATMOTION:
            vx, vy = e.value
            self._handle_hat_axis(vx, self.last_hat_x, self.hat_mapping_x, cb)
            self._handle_hat_axis(vy, self.last_hat_y, self.hat_mapping_y, cb)
            self.last_hat_x = vx
            self.last_hat_y = vy

    def _handle_hat_axis(self, now: int, last: int,
                        mapping: Dict[int, JoyStickButtons], cb: Callable):
        """处理 D-pad 单轴变化。"""
        if now == last:
            return
        if last != 0 and last in mapping:
            self.button_changed(mapping[last], pygame.JOYBUTTONUP, cb)
        if now != 0 and now in mapping:
            self.button_changed(mapping[now], pygame.JOYBUTTONDOWN, cb)

    def handle_trigger(self, e, cb):
        if e.type != pygame.JOYAXISMOTION:
            return
        for trigger_name in ('lt', 'rt'):
            if e.axis != self.axis_mapping[trigger_name]:
                continue
            is_right = (trigger_name == 'rt')
            was_pressed = getattr(self.state, trigger_name)

            if not was_pressed and e.value >= self.TRIGGER_THRESHOLD:
                self.state.set_trigger(trigger_name, True)
                cb(self.state, pygame.JOYBUTTONDOWN, trigger=is_right)
            elif was_pressed and e.value < self.TRIGGER_THRESHOLD:
                self.state.set_trigger(trigger_name, False)
                cb(self.state, pygame.JOYBUTTONUP, trigger=is_right)

    def handle_axis(self, e, cb):
        """处理摇杆轴输入，带死区滤波，仅在值变化时回调。"""
        if e.type != pygame.JOYAXISMOTION:
            return

        axis_names = {
            self.axis_mapping['lx']: 'lx',
            self.axis_mapping['ly']: 'ly',
            self.axis_mapping['rx']: 'rx',
            self.axis_mapping['ry']: 'ry',
        }
        name = axis_names.get(e.axis)
        if name is None:
            return

        # 应用死区 + 钳位
        new_value = clamp(e.value)
        self.state.set_axis(name, new_value, dead_zone=DEAD_ZONE)

        # 仅在值实际变化时触发回调（set_axis 已过滤死区）
        old_value = getattr(self.state, name)
        if old_value != new_value or abs(new_value) >= DEAD_ZONE:
            cb(self.state, e.type, axis=True)


class JoyConEventHandler(JoystickEventHandler):
    """
    JoyCon 手柄事件处理器（框架，需要补全）。

    TODO: 完成 JoyCon 的完整按键/轴映射。
    当前仅保留类结构以保持代码完整性。
    """

    @classmethod
    def joy_add(cls, joy, state):
        if joy.get_name() != "Wireless Gamepad":
            return None
        if cls._instance:
            return cls._instance

        # TODO: 实现 JoyCon 双柄检测逻辑
        raise NotImplementedError("JoyCon handler is not yet implemented for the new event model.")

    def is_joy(self, instance_id: int) -> bool:
        # TODO: 实现
        return False

    def handle_button(self, e, cb):
        pass

    def handle_trigger(self, e, cb):
        pass

    def handle_axis(self, e, cb):
        pass
