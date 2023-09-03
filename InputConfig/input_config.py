import json
from dataclasses import dataclass
from typing import List, Dict, Callable
from InputConfig.config_schema import ConfigParser, JoyStickButtons
from InputConfig.input_functions import JoyStickInputFunctions


@dataclass
class ArcJoyStickLayer:
    L_NUM: int
    R_NUM: int
    _buttons: List[str] = None
    _trigger: List[str] = None
    _axis: List[List[str]] = None

    buttons: List[Callable] = None
    trigger: List[Callable] = None
    axis: List[List[Callable]] = None

    is_axis_layer = False

    @classmethod
    def init(cls, data):
        NUMS = ['L_NUM', 'R_NUM']
        res = cls(**{k: data[k] for k in data if k in NUMS})
        for k, v in data.items():
            if k in NUMS:
                continue
            if k == 'axis':
                res._axis = v
            if k == 'buttons':
                # 填充空值
                support_buttons = len(JoyStickButtons.__members__)
                res._buttons = v[:support_buttons] if len(v) >= support_buttons else \
                    (v + [JoyStickInputFunctions.none.value])
            if k == 'trigger':
                res._trigger = v
        res.is_axis_layer = any([JoyStickInputFunctions.is_function(k, JoyStickInputFunctions.enter_axis)
                                 for k in (res._trigger + res._buttons)])
        return res

    def load_controller(self, controller):
        default_axis_func = 'tap' if self.is_axis_layer else 'press'
        self.axis = [
            [ConfigParser.get_function(i, controller, default_func=default_axis_func) for i in line]
            for line in self._axis
        ]
        self.trigger = [ConfigParser.get_function(i, controller) for i in self._trigger]
        self.buttons = [ConfigParser.get_function(i, controller) for i in self._buttons]


@dataclass
class ArcJoyStickConfig:
    config_name: str
    layer_number: int
    default_layer: str
    layers: Dict[str, ArcJoyStickLayer] = None

    @classmethod
    def load_from(cls, filename):
        with open(filename) as fp:
            data = json.load(fp)
        config = ConfigParser().validate(data)
        layers = {k: ArcJoyStickLayer.init(config['layers'][k]) for k in config['layers']}
        if 'default_layer' not in config:
            config['default_layer'] = list(layers.keys())[0]
        res = cls(**{k: config[k] for k in config if k != 'layers'})
        res.layers = layers
        return res

    def load_controller(self, controller):
        for layer in self.layers.values():
            layer.load_controller(controller)


if __name__ == '__main__':
    c = ArcJoyStickConfig.load_from(r"/configs/code6.json")
