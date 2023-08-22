import json
from dataclasses import dataclass
from typing import List
from pynput.keyboard import Key

from .config_schema import input_config_schema, ConfigFunction


@dataclass
class ArcJoyStickConfig:
    config_name: str
    L_NUM: int
    R_NUM: int
    layer_number: int

    table: List[List[Key]] = None

    @classmethod
    def load_from(cls, filename):
        with open(filename) as fp:
            data = json.load(fp)
        config = input_config_schema.validate(data)
        res = cls(**{k: config[k] for k in config if k != 'table'})
        layers = config['table']

        res.table = [
            [
                [ConfigFunction.get_function(c) if ConfigFunction.is_function(c) else c for c in line]
                for line in layer
            ]
            for layer in layers
        ]
        return res

    def get_code(self, joystick_state):
        pass
