# coding: utf-8
"""
配置加载与解析 - 从 JSON 文件构建可执行的动作层。

配置格式见 configs/ 下的 JSON 文件。
"""
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional

from .config_schema import ConfigParser, JoyStickButtons
from .functions import JoyStickInputFunctions


@dataclass
class ArcJoyStickLayer:
    """一个输入层：包含按钮、触发器、摇杆轴的映射。"""

    L_NUM: int
    R_NUM: int

    # 原始字符串配置（从 JSON 读取）
    _buttons: List[str] = field(default_factory=list)
    _trigger: List[str] = field(default_factory=list)
    _axis: List[List[str]] = field(default_factory=list)

    # 解析后的可调用对象
    buttons: List[Callable] = field(default_factory=list)
    trigger: List[Callable] = field(default_factory=list)
    axis: List[List[Callable]] = field(default_factory=list)

    is_axis_layer: bool = False

    @classmethod
    def init(cls, data: dict) -> "ArcJoyStickLayer":
        """从 JSON dict 构建层对象。"""
        res = cls(L_NUM=data['L_NUM'], R_NUM=data['R_NUM'])

        for k, v in data.items():
            if k in ('L_NUM', 'R_NUM'):
                continue
            elif k == 'axis':
                res._axis = v
            elif k == 'buttons':
                # 补齐到 JoyStickButtons 枚举数量
                support_buttons = JoyStickButtons.get_size()
                if len(v) >= support_buttons:
                    res._buttons = v[:support_buttons]
                else:
                    # 不足的部分用 <None> 填充
                    res._buttons = v + [JoyStickInputFunctions.none.value] * (support_buttons - len(v))
            elif k == 'trigger':
                res._trigger = v

        # 判断本层是否包含 EnterCode（轴输入）功能
        all_funcs = res._trigger + res._buttons
        res.is_axis_layer = any(
            JoyStickInputFunctions.is_function(k, JoyStickInputFunctions.enter_axis)
            for k in all_funcs
        )
        return res

    def load_controller(self, controller):
        """将字符串配置解析为可调用对象。"""
        default_axis_func = 'tap' if self.is_axis_layer else 'press'
        self.axis = [
            [ConfigParser.get_function(i, controller, default_func=default_axis_func) for i in row]
            for row in self._axis
        ]
        self.trigger = [ConfigParser.get_function(i, controller) for i in self._trigger]
        self.buttons = [ConfigParser.get_function(i, controller) for i in self._buttons]


@dataclass
class ArcJoyStickConfig:
    """手柄输入法配置：包含多个输入层。"""

    config_name: str
    layer_number: int
    default_layer: str
    layers: Dict[str, ArcJoyStickLayer] = field(default_factory=dict)

    @classmethod
    def load_from(cls, filename: str) -> "ArcJoyStickConfig":
        """从 JSON 文件加载配置。"""
        with open(filename, encoding='utf-8') as fp:
            data = json.load(fp)

        config = ConfigParser().validate(data)
        layers = {k: ArcJoyStickLayer.init(config['layers'][k]) for k in config['layers']}

        default_layer = config.get('default_layer', list(layers.keys())[0])

        return cls(
            config_name=config['config_name'],
            layer_number=config['layer_number'],
            default_layer=default_layer,
            layers=layers,
        )

    def load_controller(self, controller):
        """为所有层加载控制器。"""
        for layer in self.layers.values():
            layer.load_controller(controller)


if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "code6.json")
    c = ArcJoyStickConfig.load_from(config_path)
    print(f"配置: {c.config_name}, 层: {list(c.layers.keys())}")
