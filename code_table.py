from typing import Dict

scan_code_dict = {
    "00 00": "None",
    "01 00": "Esc",  # 即Esc键的扫描码是"0001"
    "02 00": "1",
    "03 00": "2",
    "04 00": "3",
    "05 00": "4",
    "06 00": "5",
    "07 00": "6",
    "08 00": "7",
    "09 00": "8",
    "0a 00": "9",
    "0b 00": "0",
    "0c 00": "-",
    "0d 00": "=",
    "0e 00": "Backspace",
    "0f 00": "Tab",
    "10 00": "Q",
    "11 00": "W",
    "12 00": "E",
    "13 00": "R",
    "14 00": "T",
    "15 00": "Y",
    "16 00": "U",
    "17 00": "I",
    "18 00": "O",
    "19 00": "P",
    "1a 00": "[",
    "1b 00": "]",
    "1c 00": "Enter",
    "1d 00": "Left Ctrl",
    "1e 00": "A",
    "1f 00": "S",
    "20 00": "D",
    "21 00": "F",
    "22 00": "G",
    "23 00": "H",
    "24 00": "J",
    "25 00": "K",
    "26 00": "L",
    "27 00": "Semicolon",  # 由评论区指出，键盘上的“;”应该用其他值代替，否则会与配置文本文件中的“;”混淆
    "28 00": "'",
    "29 00": "`",
    "2a 00": "Left Shift",
    "2b 00": "\\",
    "2c 00": "Z",
    "2d 00": "X",
    "2e 00": "C",
    "2f 00": "V",
    "30 00": "B",
    "31 00": "N",
    "32 00": "M",
    "33 00": ",",
    "34 00": ".",
    "35 00": "/",
    "36 00": "Right Shift",
    "37 00": "n*",
    "38 00": "Left Alt",
    "39 00": "Space",
    "3a 00": "Caps Lock",
    "3b 00": "F1",
    "3c 00": "F2",
    "3d 00": "F3",
    "3e 00": "F4",
    "3f 00": "F5",
    "40 00": "F6",
    "41 00": "F7",
    "42 00": "F8",
    "43 00": "F9",
    "44 00": "F10",
    "45 00": "Num Lock",
    "46 00": "Scroll Lock",
    "47 00": "n7",
    "48 00": "n8",
    "49 00": "n9",
    "4a 00": "n-",
    "4b 00": "n4",
    "4c 00": "n5",
    "4d 00": "n6",
    "4e 00": "n+",
    "4f 00": "n1",
    "50 00": "n2",
    "51 00": "n3",
    "52 00": "n0",
    "53 00": "n.",
    "57 00": "F11",
    "58 00": "F12",

    "1c e0": "nEnter",
    "1d e0": "Right Ctrl",
    "37 e0": "PrtSc",
    "38 e0": "Right Alt",
    "47 e0": "Home",
    "48 e0": "Up",
    "49 e0": "Page Up",
    "4b e0": "Left",
    "4d e0": "Right",
    "4f e0": "End",
    "50 e0": "Down",
    "51 e0": "Page Down",
    "52 e0": "Insert",
    "53 e0": "Delete",
    "5b e0": "Left Windows",
    "5c e0": "Right Windows",
}

code_table = [v for v in scan_code_dict.values() if len(v) <= 2 and v != 'Up' and not v.startswith('n')]


# print(code_table)

class SingleEnglishCode:
    """
    Single English Codes has (4+1) * (8+1) = 45 keys.
    It can include 26 English characters, 10 numbers, and 9 special keys as Follow:
    [Space, ",", ., ?, ;, ', Enter, Backspace, Tab]
    """
    # TODO: consider Bi-gram probability
    LNum = 4
    RNum = 8

    def get_code(self, x: int, y: int) -> str:
        """
        return key in (x, y)
        """
        assert x <= self.LNum and y <= self.RNum
        return "a"

    def get_code_recommand(self, x: int, y: int) -> (Dict[int, str], Dict[int, str]):
        """
        return the code table for (x, y)
        """
        pass


class CodeTable(object):
    @staticmethod
    def return_code(x, y):
        index = x * 8 + y
        index = index % len(code_table)
        return code_table[index]
