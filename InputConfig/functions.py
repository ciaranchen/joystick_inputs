# coding: utf-8
"""
手柄功能控制器 - 将配置中的字符串动作映射为可调用对象。

支持的动作类型：
- 键盘按键：press / tap / release
- 鼠标点击：mouse_click
- 鼠标移动：mouse_move (TODO)
- 层切换：press_to_layer / hold_to_layer
- 轴输入：enter_axis（读取当前摇杆位置并输入对应键）
"""
import re
from enum import Enum
from typing import Optional, Tuple

import pygame
from pygame import JOYBUTTONUP, JOYBUTTONDOWN
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyController


class JoyStickInputFunctions(Enum):
    """可在配置 JSON 中使用的特殊函数标记。"""

    none = r'<None>'
    press_to_layer = r'<PressToLayer:(.*)>'
    hold_to_layer = r'<HoldToLayer:(.*)>'
    enter_axis = r'<EnterCode>'
    mouse_move = r'<Mouse:(\d+)>'
    mouse_click = r'<MouseClick:(.*)>'
    mouse_axis = r'<MouseAxis>'

    @classmethod
    def get_function(cls, key: str) -> Optional[Tuple[str, re.Match]]:
        """匹配 key 是否对应某个特殊函数，返回 (函数名, 匹配对象)。"""
        for func in cls.__members__.values():
            match_res = re.fullmatch(func.value, key)
            if match_res:
                return func.name, match_res
        return None

    @classmethod
    def is_function(cls, key: str, function: "JoyStickInputFunctions") -> bool:
        """检查 key 是否匹配指定的特殊函数。"""
        return re.fullmatch(function.value, key) is not None


class JoyStickFunctionController:
    """
    将配置字符串转换为实际的键盘/鼠标操作闭包。

    每个方法返回一个 (core, joy, event) -> None 的闭包。
    """

    def __init__(self):
        self.key_controller = KeyController()
        self.mouse_controller = MouseController()

    # ── 特殊函数 ────────────────────────────────────────────

    @staticmethod
    def none():
        """空操作。"""
        return lambda _core, _joy, _event: None

    @staticmethod
    def press_to_layer(layer: str):
        """按键切换层（永久切换）。"""
        def _inner(core, joy, event):
            if event == JOYBUTTONDOWN:
                core.layer = layer
        return _inner

    @staticmethod
    def hold_to_layer(layer: str):
        """按住切换层（松开恢复）。"""
        def _inner(core, joy, event):
            if event == JOYBUTTONUP:
                core.layer = core.last_layer
            elif event == JOYBUTTONDOWN:
                core.last_layer = core.layer
                core.layer = layer
        return _inner

    # ── 键盘操作 ────────────────────────────────────────────

    @staticmethod
    def _press_release(controller, key, event, press_event=JOYBUTTONDOWN, release_event=JOYBUTTONUP):
        """通用的按下/释放处理。"""
        if event == press_event:
            controller.press(key)
        elif event == release_event:
            controller.release(key)

    def press(self, key):
        """按住型：按下时 press，释放时 release。"""
        return lambda _core, _joy, e: self._press_release(self.key_controller, key, e)

    def tap(self, key, trigger_event=JOYBUTTONDOWN):
        """点按型：在指定事件时 tap 一次。"""
        def _tap(_core, _joy, event):
            if event == trigger_event:
                self.key_controller.tap(key)
        return _tap

    # ── 轴输入 ──────────────────────────────────────────────

    @staticmethod
    def enter_axis():
        """读取当前摇杆位置，查表并输入对应的键。"""
        def _inner(core, joy, event):
            now_layer = core.config.layers[core.layer]
            l_index = core.which_arc(joy.lx, joy.ly, now_layer.L_NUM)
            r_index = core.which_arc(joy.rx, joy.ry, now_layer.R_NUM)
            func = now_layer.axis[l_index][r_index]
            return func(core, joy, event)
        return _inner

    # ── 鼠标操作 ────────────────────────────────────────────

    def mouse_click(self, button_name: str):
        """鼠标按键（left / right / middle）。"""
        if not hasattr(Button, button_name):
            return self.none()
        button = Button[button_name]
        return lambda _core, _joy, e: self._press_release(self.mouse_controller, button, e)

    @staticmethod
    def mouse_move(direction_index: str):
        """鼠标移动（TODO: 待实现完整方向映射）。"""
        return lambda _core, _joy, _event: None

    @staticmethod
    def mouse_axis():
        """鼠标轴模式（TODO: 待实现）。"""
        return lambda _core, _joy, _event: None
