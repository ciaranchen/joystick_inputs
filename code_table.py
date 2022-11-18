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
}


class SingleEnglishCode:
    """
    Single English Codes has (4+1) * (8+1) = 45 keys.
    It can include 26 English characters, 10 numbers, and 9 special keys as Follow:
    [Space, ",", ., ?, ;, ', Enter, Backspace, Tab]
    """
    # TODO: consider Bi-gram probability
    LNum = 4
    RNum = 8
    special_code = {
        # Left Thumb Down for number
        (3, 8): '1', (3, 1): '2', (3, 2): '3',
        (3, 7): '4', (3, 0): '5', (3, 3): '6',
        (3, 6): '7', (3, 5): '8', (3, 4): '9',

        (0, 0): 'Space',
        (1, 0): 'Enter',
        (2, 0): 'Backspace',
        (4, 0): 'Tab',

        # Right Thumb Down for special keys
        (0, 5): '0',
        (1, 5): ',',
        (2, 5): '.',
        (4, 5): ';',
    }
    Frq_single_gram = "etaoins"
    freq_mappings = {
        'e': ['z', 'j', 'q'],
        't': ['v', 'k', 'd'],
        'a': ['x', 'y', 'f'],
        'o': ['g', 'b', 'h'],
        'i': ['u', 'p', 'w'],
        'n': ['m', 'l', 'r'],
        's': ['c', '?', "'"]
    }

    def __init__(self):
        self.trigger_mapping = ("Shift", None)

        self.code = self.special_code.copy()
        no_assign = [1, 2, 3, 4, 6, 7, 8]
        for i, z in zip(no_assign, self.freq_mappings):
            self.code[(0, i)] = z
            self.code[(1, i)] = self.freq_mappings[z][0]
            self.code[(2, i)] = self.freq_mappings[z][1]
            self.code[(4, i)] = self.freq_mappings[z][2]

    def get_code(self, x: int, y: int) -> str or Key:
        """
        return key in (x, y)
        """
        assert x <= self.LNum and y <= self.RNum
        key = self.code[(x, y)]
        return key_table[key] if key in key_table else key

    def get_recommend(self, x: int, y: int) -> (List[str], List[str]):
        """
        return the code table for (x, y)
        """
        code = self.code
        return [code[(l, y)] for l in range(self.LNum + 1)], \
               [code[(x, r)] for r in range(self.RNum + 1)]
