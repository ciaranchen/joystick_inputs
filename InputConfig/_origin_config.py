import json
from itertools import product
from typing import List, Union
from pynput.keyboard import Key


class SingleEnglishCode:
    """
    Single English Codes has (4+1) * (8+1) = 45 keys.
    It can include 26 English characters, 10 numbers, and 9 special keys as Follow:
    [Space, ",", ., ?, ;, ', Enter, Backspace, Tab]
    """
    L_NUM = 4
    R_NUM = 8

    special_code = {
        # Left Thumb Down for number
        (3, 8): '1', (3, 1): '2', (3, 2): '3',
        (3, 7): '4', (3, 0): '5', (3, 3): '6',
        (3, 6): '7', (3, 5): '8', (3, 4): '9',
    }

    indexs = [
        # Right Thumb for special keys
        [[0, 5], [0, 1, 2, 4], True],
        # Right Thumb for English keys
        [[1, 2, 3, 4, 6, 7, 8], [0, 1, 2, 4], True],
    ]
    configs = [
        [
            [Key.space, ',', '.', ';'],
            ["0", ':', "'", '/']
        ],
        {
            'e': ['z', 'j', 'q'],
            't': ['v', 'k', 'd'],
            'a': ['x', 'y', 'f'],
            'o': ['g', 'b', 'h'],
            'i': ['u', 'p', 'w'],
            'n': ['m', 'l', 'r'],
            's': ['c', '-', '=']
        }
    ]
    MOTION = [Key.up, Key.right, Key.down, Key.left]

    def __init__(self):
        self.bumper_mapping = [Key.ctrl, Key.alt]
        self.LT_mapping = Key.shift
        self.right_mapping = [Key.space, Key.enter, Key.backspace, Key.tab]

        self.code = self.special_code.copy()
        for index, data in zip(self.indexs, self.configs):
            # print(index)
            fi1, fi2, vertical = index
            if isinstance(data, list):
                for i1, f1 in enumerate(fi1):
                    for i2, f2 in enumerate(fi2):
                        index = (f1, f2) if not vertical else (f2, f1)
                        self.code[index] = data[i1][i2]
            elif isinstance(data, dict):
                for f1, k in zip(fi1, data):
                    codes = [k] + data[k]
                    for f2, c in zip(fi2, codes):
                        index = (f1, f2) if not vertical else (f2, f1)
                        self.code[index] = c

    def get_code(self, x: int, y: int) -> str or Key:
        """
        return key in (x, y)
        """
        assert x <= self.L_NUM and y <= self.R_NUM
        key = self.code[(x, y)]
        return key

    def get_recommend(self, x: int, y: int) -> (List[str], List[str]):
        """
        return the code table for (x, y)
        """
        code = self.code
        return [code[(l, y)] for l in range(self.L_NUM + 1)], \
            [code[(x, r)] for r in range(self.R_NUM + 1)]

    def to_json(self, filename):
        def walk_mapping(arr: List[Union[Key, str]]) -> List[str]:
            return [c if isinstance(c, str) else c.name for c in arr]

        table = [[self.code[(i, j)] for j in range(self.R_NUM)] for i in range(self.L_NUM)]
        table = [walk_mapping(line) for line in table]
        obj = {
            'config_name': self.__class__.__name__,
            'layer_number': 1,
            'layers': {
                'mouse-layer': {
                    'L_NUM': 4,
                    'R_NUM': 1,
                    'axis': [['<Mouse:%d>' % i for i in range(4)]],
                    'buttons': walk_mapping(
                        self.right_mapping + self.bumper_mapping + [Key.up, Key.down, Key.left, Key.right]
                    ) + [r'<None>', r'<PressToLayer:layer1>'],
                    'trigger': [r'<MouseClick:left>', r'<MouseClick:right>']
                },
                'layer1': {
                    'L_NUM': self.L_NUM,
                    'R_NUM': self.R_NUM,
                    'axis': table,
                    'buttons': walk_mapping(
                        self.right_mapping + self.bumper_mapping + [Key.up, Key.down, Key.left, Key.right]
                    ) + [r'<None>', r'<PressToLayer:mouse-layer>'],
                    'trigger': walk_mapping([self.LT_mapping, r'<EnterCode>']),
                }
            }
        }
        with open(filename, 'w') as fp:
            json.dump(obj, fp)


class CodeExtension(SingleEnglishCode):
    L_NUM = 6
    R_NUM = 8

    special_code = {
        # numbers
        (6, 8): '1', (6, 1): '2', (6, 2): '3',
        (6, 7): '4', (6, 0): '5', (6, 3): '6',
        (6, 6): '7', (6, 5): '8', (6, 4): '9',
    }

    indexs = [
        # Right Thumb for special keys
        [[0, 5], [0, 1, 2, 3, 4, 5], True],
        # Right Thumb for English keys
        [[1, 2, 3, 4, 6, 7, 8], [0, 4, 5, 1], True],
        [[1, 2, 3, 4, 6, 7, 8], [2, 3], True],
    ]
    configs = [
        [
            [Key.space, ',', '.', ';', ':', "'"],
            ["0", '/', '\\', '`', Key.menu, Key.delete]
        ],
        {
            'e': ['z', 'j', 'q'],
            't': ['v', 'k', 'd'],
            'a': ['x', 'y', 'f'],
            'o': ['g', 'b', 'h'],
            'i': ['u', 'p', 'w'],
            'n': ['m', 'l', 'r'],
            's': ['c', '-', '=']
        },
        [
            [Key.insert, Key.pause],
            [Key.home, Key.end],
            [Key.page_up, Key.page_down],
            [Key.print_screen, Key.scroll_lock],
            [Key.f1, Key.f2],
            [Key.f3, Key.f4],
            [Key.f5, Key.f6]
        ]
    ]


class CodeSix2(SingleEnglishCode):
    L_NUM = 6
    R_NUM = 8

    _code = {
        0: ['Space'] + list('tainshrd'),
        # 1 and 4 is large
        1: list('elmcvpbgw'),
        4: list('ofjkquxyz'),
        2: [Key.f10, Key.f11, Key.f12, '`', Key.delete, Key.home, Key.end, '-', '='],
        3: [Key.f1, Key.f2, Key.f3, Key.f4, Key.f5, Key.f6, Key.f7, Key.f8, Key.f9],
        5: list('523698741'),
        6: list(",./;[]\\0") + [Key.menu],
    }

    def __init__(self):
        super().__init__()
        self.code = {}
        for i, j in product(range(self.L_NUM + 1), range(self.R_NUM + 1)):
            # print(i, j)
            self.code[(i, j)] = self._code[i][j]


if __name__ == '__main__':
    sec = SingleEnglishCode()
    sec.to_json('simple_english.json')
    ce = CodeExtension()
    ce.to_json('english_code_ex.json')
    cs6 = CodeSix2()
    cs6.to_json('code6.json')
