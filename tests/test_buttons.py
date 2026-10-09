# coding: utf-8
"""
测试 JoyStickButtons 枚举
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from InputConfig.config_schema import JoyStickButtons


class TestJoyStickButtons:
    """测试手柄按钮枚举"""
    
    def test_button_count(self):
        """测试按钮总数"""
        assert JoyStickButtons.get_size() == 12
    
    def test_button_values(self):
        """测试按钮值从 0 开始连续"""
        values = [b.value for b in JoyStickButtons]
        assert values == list(range(12))
    
    def test_xbox_buttons(self):
        """测试 XBox 标准按钮"""
        assert JoyStickButtons.RDownButton.value == 0   # A
        assert JoyStickButtons.RRightButton.value == 1  # B
        assert JoyStickButtons.RLeftButton.value == 2   # X
        assert JoyStickButtons.RUpButton.value == 3     # Y
        assert JoyStickButtons.LBumper.value == 4
        assert JoyStickButtons.RBumper.value == 5
    
    def test_dpad_buttons(self):
        """测试 D-Pad 按钮"""
        assert JoyStickButtons.LDownButton.value == 6
        assert JoyStickButtons.LRightButton.value == 7
        assert JoyStickButtons.LLeftButton.value == 8
        assert JoyStickButtons.LUpButton.value == 9
    
    def test_stick_buttons(self):
        """测试摇杆按下按钮"""
        assert JoyStickButtons.LStickIn.value == 10
        assert JoyStickButtons.RStickIn.value == 11
    
    def test_button_names(self):
        """测试按钮名称"""
        assert JoyStickButtons.RDownButton.name == 'RDownButton'
        assert JoyStickButtons.LBumper.name == 'LBumper'
    
    def test_get_size_method(self):
        """测试 get_size 返回正确数量"""
        size = JoyStickButtons.get_size()
        assert size == len(JoyStickButtons.__members__)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
