# coding: utf-8
"""
测试配置字符串到函数的转换
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock
from InputConfig.config_schema import ConfigParser
from InputConfig.functions import JoyStickFunctionController


class TestConfigParserGetFunction:
    """测试 ConfigParser.get_function 方法"""
    
    def setup_method(self):
        """每个测试前创建模拟控制器"""
        self.controller = Mock(spec=JoyStickFunctionController)
        
        # 设置模拟方法返回值
        self.controller.press.return_value = Mock()
        self.controller.tap.return_value = Mock()
        self.controller.none.return_value = Mock()
        self.controller.press_to_layer.return_value = Mock()
        self.controller.hold_to_layer.return_value = Mock()
        self.controller.enter_axis.return_value = Mock()
        self.controller.mouse_move.return_value = Mock()
        self.controller.mouse_click.return_value = Mock()
        self.controller.mouse_axis.return_value = Mock()
        
        self.parser = ConfigParser()
    
    def test_regular_character(self):
        """测试普通字符转为 press 函数"""
        result = self.parser.get_function('a', self.controller)
        
        self.controller.press.assert_called_once_with('a')
        assert result == self.controller.press.return_value
    
    def test_space_character(self):
        """测试空格键（会转换为 pynput Key.space）"""
        result = self.parser.get_function('space', self.controller)
        
        # space 会被识别为 pynput 的 Key.space
        from pynput.keyboard import Key
        self.controller.press.assert_called_once_with(Key.space)
    
    def test_pynput_key(self):
        """测试 pynput Key 枚举"""
        result = self.parser.get_function('shift', self.controller)
        
        from pynput.keyboard import Key
        self.controller.press.assert_called_once_with(Key.shift)
    
    def test_pynput_key_f1(self):
        """测试 F1 键"""
        result = self.parser.get_function('f1', self.controller)
        
        from pynput.keyboard import Key
        self.controller.press.assert_called_once_with(Key.f1)
    
    def test_none_function(self):
        """测试 <None> 函数"""
        result = self.parser.get_function('<None>', self.controller)
        
        self.controller.none.assert_called_once_with()
        assert result == self.controller.none.return_value
    
    def test_press_to_layer(self):
        """测试 <PressToLayer:xxx> 函数"""
        result = self.parser.get_function('<PressToLayer:mouse-layer>', self.controller)
        
        self.controller.press_to_layer.assert_called_once_with('mouse-layer')
        assert result == self.controller.press_to_layer.return_value
    
    def test_hold_to_layer(self):
        """测试 <HoldToLayer:xxx> 函数"""
        result = self.parser.get_function('<HoldToLayer:layer1>', self.controller)
        
        self.controller.hold_to_layer.assert_called_once_with('layer1')
        assert result == self.controller.hold_to_layer.return_value
    
    def test_enter_axis(self):
        """测试 <EnterCode> 函数"""
        result = self.parser.get_function('<EnterCode>', self.controller)
        
        self.controller.enter_axis.assert_called_once_with()
        assert result == self.controller.enter_axis.return_value
    
    def test_mouse_move(self):
        """测试 <Mouse:N> 函数"""
        result = self.parser.get_function('<Mouse:0>', self.controller)
        
        self.controller.mouse_move.assert_called_once_with('0')
        assert result == self.controller.mouse_move.return_value
        
        result2 = self.parser.get_function('<Mouse:3>', self.controller)
        self.controller.mouse_move.assert_called_with('3')
    
    def test_mouse_click(self):
        """测试 <MouseClick:button> 函数"""
        result = self.parser.get_function('<MouseClick:left>', self.controller)
        
        self.controller.mouse_click.assert_called_once_with('left')
        assert result == self.controller.mouse_click.return_value
        
        result2 = self.parser.get_function('<MouseClick:right>', self.controller)
        self.controller.mouse_click.assert_called_with('right')
    
    def test_mouse_axis(self):
        """测试 <MouseAxis> 函数"""
        result = self.parser.get_function('<MouseAxis>', self.controller)
        
        self.controller.mouse_axis.assert_called_once_with()
        assert result == self.controller.mouse_axis.return_value
    
    def test_default_func_parameter(self):
        """测试 default_func 参数"""
        # 默认是 press
        self.parser.get_function('a', self.controller)
        self.controller.press.assert_called_once()
        
        # 改为 tap
        self.controller.reset_mock()
        self.parser.get_function('b', self.controller, default_func='tap')
        self.controller.tap.assert_called_once()


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
