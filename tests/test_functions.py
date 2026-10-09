# coding: utf-8
"""
测试 JoyStickInputFunctions 特殊函数匹配
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from InputConfig.functions import JoyStickInputFunctions


class TestJoyStickInputFunctions:
    """测试特殊函数识别"""
    
    def test_none_function(self):
        """测试 <None> 匹配"""
        result = JoyStickInputFunctions.get_function('<None>')
        assert result is not None
        func_name, match = result
        assert func_name == 'none'
        assert match.groups() == ()
    
    def test_press_to_layer(self):
        """测试 <PressToLayer:xxx> 匹配"""
        result = JoyStickInputFunctions.get_function('<PressToLayer:mouse-layer>')
        assert result is not None
        func_name, match = result
        assert func_name == 'press_to_layer'
        assert match.group(1) == 'mouse-layer'
    
    def test_hold_to_layer(self):
        """测试 <HoldToLayer:xxx> 匹配"""
        result = JoyStickInputFunctions.get_function('<HoldToLayer:layer1>')
        assert result is not None
        func_name, match = result
        assert func_name == 'hold_to_layer'
        assert match.group(1) == 'layer1'
    
    def test_enter_axis(self):
        """测试 <EnterCode> 匹配"""
        result = JoyStickInputFunctions.get_function('<EnterCode>')
        assert result is not None
        func_name, match = result
        assert func_name == 'enter_axis'
    
    def test_mouse_move(self):
        """测试 <Mouse:N> 匹配"""
        result = JoyStickInputFunctions.get_function('<Mouse:0>')
        assert result is not None
        func_name, match = result
        assert func_name == 'mouse_move'
        assert match.group(1) == '0'
        
        result2 = JoyStickInputFunctions.get_function('<Mouse:3>')
        assert result2 is not None
        assert result2[1].group(1) == '3'
    
    def test_mouse_click(self):
        """测试 <MouseClick:button> 匹配"""
        result = JoyStickInputFunctions.get_function('<MouseClick:left>')
        assert result is not None
        func_name, match = result
        assert func_name == 'mouse_click'
        assert match.group(1) == 'left'
        
        result2 = JoyStickInputFunctions.get_function('<MouseClick:right>')
        assert result2 is not None
        assert result2[1].group(1) == 'right'
    
    def test_mouse_axis(self):
        """测试 <MouseAxis> 匹配"""
        result = JoyStickInputFunctions.get_function('<MouseAxis>')
        assert result is not None
        func_name, match = result
        assert func_name == 'mouse_axis'
    
    def test_regular_character(self):
        """测试普通字符不匹配任何函数"""
        for char in ['a', 'b', 'z', '1', ' ', 'space', 'enter']:
            result = JoyStickInputFunctions.get_function(char)
            assert result is None, f"普通字符 '{char}' 不应匹配函数"
    
    def test_invalid_format(self):
        """测试无效格式"""
        invalid_inputs = [
            '<PressToLayer>',      # 缺少层名
            '<Mouse>',             # 缺少索引
            '<MouseClick>',        # 缺少按钮名
            'PressToLayer:xxx',    # 缺少尖括号
        ]
        for inp in invalid_inputs:
            result = JoyStickInputFunctions.get_function(inp)
            assert result is None, f"无效格式 '{inp}' 不应匹配"
    
    def test_is_function_helper(self):
        """测试 is_function 辅助方法"""
        assert JoyStickInputFunctions.is_function(
            '<None>', 
            JoyStickInputFunctions.none
        )
        assert JoyStickInputFunctions.is_function(
            '<EnterCode>', 
            JoyStickInputFunctions.enter_axis
        )
        assert not JoyStickInputFunctions.is_function(
            'space', 
            JoyStickInputFunctions.none
        )
        assert not JoyStickInputFunctions.is_function(
            '<PressToLayer:x>', 
            JoyStickInputFunctions.none
        )


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
