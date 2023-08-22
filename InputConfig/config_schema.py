import json
import re

from pynput.keyboard import Key
from schema import Schema, Optional, And, Or, Use
import string

key_table = {k.name: k for k in Key}
printable_characters = [char for char in string.printable if len(char) == 1]
VALID_KEYS = printable_characters + list(key_table.keys())

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

class ConfigFunction:
    @staticmethod
    def is_function(key_string):
        for reg in FUNCTIONS.values():
            if re.match(reg, key_string):
                return True
        return False

    @staticmethod
    def get_function(key_string):
        pass


VALID_INPUT = Or(And(str, lambda x: x.lower() in VALID_KEYS), And(str, ConfigFunction.is_function))
input_config_schema = Schema({
    'config_name': str,
    'layer_number': And(int, lambda x: 0 < x < 10),
    'layers': {
        str: {
            'L_NUM': int,
            'R_NUM': int,
            'axis': [[VALID_INPUT]],
            'buttons': And([VALID_INPUT], lambda x: len(x) == 12),
            'trigger': And([VALID_INPUT], lambda x: len(x) == 2)
        }
    }
})

if __name__ == '__main__':
    with open(r'C:\Users\ciaran\Desktop\Projects\joystick_inputs\configs\simple_english.json') as fp:
        data = json.load(fp)
    res = input_config_schema.validate(data)
