import json
from dataclasses import dataclass
from typing import List, Dict, Union, Callable, Tuple
from pynput.keyboard import Key
from InputConfig.config_schema import ConfigParser

ACTION = Union[str, Key, Tuple]


@dataclass
class ArcJoyStickLayer:
    L_NUM: int
    R_NUM: int
    _buttons: List[ACTION] = None
    _trigger: List[ACTION] = None
    _axis: List[List[ACTION]] = None

    buttons: List[Callable] = None
    trigger: List[Callable] = None
    axis: List[List[Callable]] = None

    @classmethod
    def init(cls, data):
        NUMS = ['L_NUM', 'R_NUM']
        res = cls(**{k: data[k] for k in data if k in NUMS})
        for k, v in data.items():
            if k in NUMS:
                continue
            if k == 'axis':
                res._axis = [[ConfigParser.get_function(i) for i in line] for line in v]
            if k == 'buttons':
                res._buttons = [ConfigParser.get_function(i) for i in v]
            if k == 'trigger':
                res._trigger = [ConfigParser.get_function(i) for i in v]
        return res

    def load_controller(self, controller):
        def func_trans(f):
            if isinstance(f, tuple):
                name, args = f
                return getattr(controller, name)(*args)
            return controller.press(f)

        self.axis = [[func_trans(i) for i in line] for line in self._axis]
        self.trigger = [func_trans(i) for i in self._trigger]
        self.buttons = [func_trans(i) for i in self._buttons]


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
