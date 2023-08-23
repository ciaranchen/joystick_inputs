import json
from dataclasses import dataclass
from typing import List, Dict, Union, Callable
from pynput.keyboard import Key
from InputConfig.config_schema import ConfigParser

ACTION = Union[str, Key, Callable]


@dataclass
class ArcJoyStickLayer:
    L_NUM: int
    R_NUM: int
    buttons: List[ACTION] = None
    trigger: List[ACTION] = None
    axis: List[ACTION] = None

    @classmethod
    def init(cls, data):
        NUMS = ['L_NUM', 'R_NUM']
        res = cls(**{k: data[k] for k in data if k in NUMS})
        for k, v in data.items():
            if k in NUMS:
                continue
            if k == 'axis':
                res.axis = [[ConfigParser.get_function(i) for i in line] for line in v]
            if k == 'buttons':
                res.buttons = [ConfigParser.get_function(i) for i in v]
            if k == 'trigger':
                res.trigger = [ConfigParser.get_function(i) for i in v]


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


if __name__ == '__main__':
    c = ArcJoyStickConfig.load_from(r"/configs/code6.json")
