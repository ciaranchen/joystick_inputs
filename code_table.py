from typing import List
from pynput.keyboard import Key

key_table = {
    "Windows": Key.cmd,
    "Left Windows": Key.cmd_l,
    "Right Windows": Key.cmd_r,
    "Ctrl": Key.ctrl,
    "Left Ctrl": Key.ctrl_l,
    "Right Ctrl": Key.ctrl_r,
    "Shift": Key.shift,
    "Left Shift": Key.shift_l,
    "Right Shift": Key.shift_r,
    "Alt": Key.alt,
    "Left Alt": Key.alt_l,
    "Right Alt": Key.alt_r,

    "Esc": Key.esc,
    "Backspace": Key.backspace,
    "Tab": Key.tab,
    "Enter": Key.enter,
    "Space": Key.space,
    "Caps Lock": Key.caps_lock,
    "Num Lock": Key.num_lock,

    "F1": Key.f1,
    "F2": Key.f2,
    "F3": Key.f3,
    "F4": Key.f4,
    "F5": Key.f5,
    "F6": Key.f6,
    "F7": Key.f7,
    "F8": Key.f8,
    "F9": Key.f9,
    "F10": Key.f10,
    "F11": Key.f11,
    "F12": Key.f12,

    "PrtSc": Key.print_screen,
    "Scroll Lock": Key.scroll_lock,
    "Pause": Key.pause,

    "Insert": Key.insert,
    "Delete": Key.delete,
    "Home": Key.home,
    "End": Key.end,
    "Page Up": Key.page_up,
    "Page Down": Key.page_down,

    "Up": Key.up,
    "Left": Key.left,
    "Right": Key.right,
    "Down": Key.down,

    "media_next": Key.media_next,
    "media_play_pause": Key.media_play_pause,
    "media_previous": Key.media_previous,
    "media_volume_down": Key.media_volume_down,
    "media_volume_mute": Key.media_volume_mute,
    "media_volume_up": Key.media_volume_up,
    "menu": Key.menu
}


class SingleEnglishCode:
    """
    Single English Codes has (4+1) * (8+1) = 45 keys.
    It can include 26 English characters, 10 numbers, and 9 special keys as Follow:
    [Space, ",", ., ?, ;, ', Enter, Backspace, Tab]
    """
    # TODO: consider Bi-gram probability
    L_NUM = 4
    R_NUM = 8

    special_code = {
        # Left Thumb Down for number
        (3, 8): '1', (3, 1): '2', (3, 2): '3',
        (3, 7): '4', (3, 0): '5', (3, 3): '6',
        (3, 6): '7', (3, 5): '8', (3, 4): '9',

        # Right Thumb center for frequently used code.
        (0, 0): 'Space',
        (1, 0): ',',
        (2, 0): '.',
        (4, 0): ';',

        # Right Thumb Down for special keys
        (0, 5): '0',
        (1, 5): ':',
        (2, 5): "'",
        (4, 5): '/',
    }

    indexs = [
        # Left Thumb Down for number
        [[3], list(range(9))],
        # Right Thumb for special keys
        [[0, 1, 2, 4], [0, 5]],
        [[1, 2, 3, 4, 6, 7, 8], [0, 1, 2, 4]],
    ]
    configs = [
        list('123456789'),
        [
            "space", ',', '.', ';',
            "0", ':', "'", '/'
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
        self.bumper_mapping = (Key.ctrl, Key.alt)
        self.LT_mapping = Key.shift
        self.right_mapping = [Key.space, Key.enter, Key.backspace, Key.tab]

        self.code = {}
        for index, data in zip(self.indexs, self.configs):
            # print(index)
            fi1, fi2 = index
            if isinstance(data, list):
                for i1, f1 in enumerate(fi1):
                    for i2, f2 in enumerate(fi2):
                        print(f1, f2)
                        self.code[(f1, f2)] = data[i1 * len(fi2) + i2]

            elif isinstance(data, dict):
                for i1, k in zip(fi1, data):
                    codes = [k] + data[k]
                    for i2, c in zip(fi2, codes):
                        print(i2, i1)
                        self.code[(i2, i1)] = c

    def get_code(self, x: int, y: int) -> str or Key:
        """
        return key in (x, y)
        """
        assert x <= self.L_NUM and y <= self.R_NUM
        key = self.code[(x, y)]
        return key_table[key] if key in key_table else key

    def get_recommend(self, x: int, y: int) -> (List[str], List[str]):
        """
        return the code table for (x, y)
        """
        code = self.code
        return [code[(l, y)] for l in range(self.L_NUM + 1)], \
               [code[(x, r)] for r in range(self.R_NUM + 1)]


class CodeExtension(SingleEnglishCode):
    L_NUM = 6
    R_NUM = 8

    special_code = {
        # Left Thumb Down for number
        (3, 8): '1', (3, 1): '2', (3, 2): '3',
        (3, 7): '4', (3, 0): '5', (3, 3): '6',
        (3, 6): '7', (3, 5): '8', (3, 4): '9',

        # Right Thumb center for frequently used code.
        (0, 0): 'Space',
        (1, 0): ',',
        (2, 0): '.',
        (4, 0): ';',
        (5, 0): '-',
        (6, 0): '=',

        (0, 5): '0',
        (1, 5): ':',
        (2, 5): "'",
        (4, 5): '/',
        (5, 5): '\\',
        (6, 5): '`',

    }
    freq_index = [[1, 2, 3, 4, 6, 7, 8], [0, 4, 5, 1]]
    freq_mappings = {
        'e': ['z', 'j', 'q'],
        't': ['v', 'k', 'd'],
        'a': ['x', 'y', 'f'],
        'o': ['g', 'b', 'h'],
        'i': ['u', 'p', 'w'],
        'n': ['m', 'l', 'r'],
        's': ['c', '-', '=']
    }


class CodeSix2(SingleEnglishCode):
    L_NUM = 6
    R_NUM = 8

    _code = {
        0: ['Space'] + list('tainshrd'),
        # 1 and 4 is large
        1: list('elmcvpbgw'),
        4: list('ofjkquxyz'),
        2: ['F10', 'F11', 'F12', '`', 'Home', 'End', "Caps Lock", '-', '='],
        3: ['F' + str(i+1) for i in range(9)],
        5: list('523698741'),
        6: list(",./;[]\\0") + ['menu'],
    }

    def __init__(self):
        super().__init__()
        self.code = {}
        for i, j in zip(range(self.L_NUM + 1), range(self.R_NUM + 1)):
            self.code[(i, j)] = self._code[i][j]
