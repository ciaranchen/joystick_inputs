# coding: utf-8
"""
配置 Schema 验证 - 确保 JSON 配置文件格式正确。

定义了：
- JoyStickButtons: 手柄按钮枚举
- ConfigParser: JSON 配置验证器
"""
import os
import json
import string
from enum import Enum
from typing import Callable, Optional

from pynput.keyboard import Key
from schema import Schema, And, Or

from .functions import JoyStickInputFunctions, JoyStickFunctionController


class JoyStickButtons(Enum):
    """
    手柄按钮枚举。

    前 6 个对应 XBox 手柄的标准按钮：
    - 0~3: 右侧四键 (A/B/X/Y)
    - 4~5: 左右 Bumper
    - 6~9: D-Pad 四方向
    - 10~11: 摇杆按下
    """
    RDownButton = 0    # A
    RRightButton = 1   # B
    RLeftButton = 2    # X
    RUpButton = 3      # Y
    LBumper = 4
    RBumper = 5
    LDownButton = 6
    LRightButton = 7
    LLeftButton = 8
    LUpButton = 9
    LStickIn = 10
    RStickIn = 11

    @classmethod
    def get_size(cls) -> int:
        return len(cls.__members__)


class ConfigParser:
    """JSON 配置验证器。"""

    def __init__(self):
        printable_chars = [c for c in string.printable if len(c) == 1]
        valid_keys = printable_chars + list(Key.__members__.keys())

        # 有效的输入值：单个字符（键盘按键）或特殊函数标记
        valid_input = Or(
            And(str, lambda x: x.lower() in valid_keys),
            And(str, JoyStickInputFunctions.get_function)
        )

        self.input_config_schema = Schema({
            'config_name': str,
            'layer_number': And(int, lambda x: 0 < x < 10),
            'layers': {
                str: {
                    'L_NUM': int,
                    'R_NUM': int,
                    'axis': [[valid_input]],
                    'buttons': [valid_input],
                    'trigger': And([valid_input], lambda x: len(x) == 2)
                }
            }
        })

    @staticmethod
    def get_function(key: str, controller: JoyStickFunctionController,
                     default_func: str = 'press') -> Callable:
        """
        将配置字符串转换为可调用对象。

        解析顺序：
        1. 如果是 Key 枚举名 → 键盘操作
        2. 如果是特殊函数标记（<...>）→ 对应函数
        3. 否则视为普通字符 → 键盘操作
        """
        # 检查是否为 pynput Key 枚举
        if hasattr(Key, key):
            return getattr(controller, default_func)(Key[key])

        # 检查是否为特殊函数
        res = JoyStickInputFunctions.get_function(key)
        if not res:
            # 普通字符
            return getattr(controller, default_func)(key)

        # 特殊函数
        func_name, match = res
        args = match.groups()
        return getattr(controller, func_name)(*args)

    def validate(self, data: dict) -> dict:
        """验证并返回规范化后的配置。"""
        return self.input_config_schema.validate(data)


if __name__ == '__main__':
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "configs", "simple_english.json"
    )
    with open(config_path, encoding='utf-8') as fp:
        data = json.load(fp)
    result = ConfigParser().validate(data)
    print(f"验证通过: {result['config_name']}")
