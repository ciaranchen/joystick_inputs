import json
import re
from dataclasses import dataclass
from typing import Union

from pynput.keyboard import Key
from schema import Schema, Optional, And, Or, Use
import string

FUNCTIONS = {
    'PressToLayer': r'<PressToLayer:(.*)>',
    'HoldToLayer': r'<HoldToLayer:(.*)>',
    'PressToMouseLayer': r'<PressToMouse>',
    'HoldToMouseLayer': r'<HoldToMouse>',
    'EnterCode': r'<EnterCode>',
    'None': r'<None>',
    'Mouse': r'<Mouse:(\d+)>',
    'MouseClick': r'<MouseClick:(.*)>'
}


# BUTTONS
# A Button        - Button 0
# B Button        - Button 1
# X Button        - Button 2
# Y Button        - Button 3
# Left Bumper     - Button 4
# Right Bumper    - Button 5
# D-pad UP        - Button 6
# D-pad DOWN      - Button 7
# D-pad LEFT      - Button 8
# D-pad RIGHT     - Button 9
# L. Stick In     - Button 10
# R. Stick In     - Button 11

class ConfigParser:
    def __init__(self):
        key_table = {k.name: k for k in Key}
        printable_characters = [char for char in string.printable if len(char) == 1]
        valid_keys = printable_characters + list(key_table.keys())

        valid_input = Or(And(str, lambda x: x.lower() in valid_keys), And(str, ConfigParser.is_function))
        self.input_config_schema = Schema({
            'config_name': str,
            'layer_number': And(int, lambda x: 0 < x < 10),
            'layers': {
                str: {
                    'L_NUM': int,
                    'R_NUM': int,
                    'axis': [[valid_input]],
                    'buttons': And([valid_input], lambda x: len(x) == 12),
                    'trigger': And([valid_input], lambda x: len(x) == 2)
                }
            }
        })

    @staticmethod
    def is_function(key_string):
        for reg in FUNCTIONS.values():
            match_res = re.fullmatch(reg, key_string)
            if match_res:
                return match_res
        return False

    @staticmethod
    def get_function(key: Union[str, Key]):
        if isinstance(key, Key):
            return key
        res = ConfigParser.is_function(key_string=key)
        if not res:
            return key
        func_name, args = res.group(0), res.groups()
        return lambda: func_name, args

    def validate(self, _data):
        return self.input_config_schema.validate(_data)


if __name__ == '__main__':
    with open(r'/configs/simple_english.json') as fp:
        data = json.load(fp)
    res = ConfigParser().validate(data)
