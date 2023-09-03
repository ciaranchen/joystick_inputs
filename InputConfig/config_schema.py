import json
import re
import string
from enum import Enum
from typing import Callable, Optional

from pynput.keyboard import Key
from schema import Schema, And, Or

from InputConfig.input_functions import JoyStickInputFunctions


class JoyStickButtons(Enum):
    RDownButton = 0  # A in XBox
    RRightButton = 1  # B in XBox
    RLeftButton = 2  # X in XBox
    RUpButton = 3  # Y in XBox
    LBumper = 4
    RBumper = 5
    LDownButton = 6
    LRightButton = 7
    LLeftButton = 8
    LUpButton = 9
    LStickIn = 10
    RStickIn = 11


class ConfigParser:
    def __init__(self):
        printable_characters = [char for char in string.printable if len(char) == 1]
        valid_keys = printable_characters + list(Key.__members__.keys())

        valid_input = Or(And(str, lambda x: x.lower() in valid_keys), And(str, JoyStickInputFunctions.is_function))
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
    def get_function(key: str, controller, default_func='press') -> Callable:
        if hasattr(Key, key):
            return getattr(controller, default_func)(Key[key])
        res: Optional[str, re.Match] = JoyStickInputFunctions.get_function(key)
        if not res:
            return getattr(controller, default_func)(key)
        func_name, args = res[0], res[1].groups()
        return getattr(controller, func_name)(*args)

    def validate(self, _data):
        return self.input_config_schema.validate(_data)


if __name__ == '__main__':
    with open(r'/configs/simple_english.json') as fp:
        data = json.load(fp)
    config_res = ConfigParser().validate(data)
    print(config_res)
