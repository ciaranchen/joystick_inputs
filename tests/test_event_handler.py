# coding: utf-8
"""
测试手柄事件处理器（不依赖实际硬件）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock
from JoyStick.pygame_joysticks import XBoxEventHandler, DEAD_ZONE
from InputConfig.config_schema import JoyStickButtons


class TestXBoxEventHandler:
    """测试 XBox 手柄事件处理器"""
    
    def setup_method(self):
        """每个测试前重置单例"""
        XBoxEventHandler._instance = None
    
    def test_joy_add_correct_device(self):
        """测试识别正确的 XBox 手柄"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Xbox 360 Controller"
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        assert handler is not None
        assert handler.joy == mock_joy
        assert handler.state == mock_state
    
    def test_joy_add_wrong_device(self):
        """测试忽略非 XBox 手柄"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "PlayStation Controller"
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        assert handler is None
    
    def test_joy_add_singleton(self):
        """测试单例模式"""
        mock_joy1 = Mock()
        mock_joy1.get_name.return_value = "Xbox 360 Controller"
        mock_state1 = Mock()
        
        handler1 = XBoxEventHandler.joy_add(mock_joy1, mock_state1)
        
        mock_joy2 = Mock()
        mock_joy2.get_name.return_value = "Xbox 360 Controller"
        mock_state2 = Mock()
        
        handler2 = XBoxEventHandler.joy_add(mock_joy2, mock_state2)
        
        assert handler1 is handler2
    
    def test_axis_mapping(self):
        """测试轴映射正确"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Xbox 360 Controller"
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        assert handler.axis_mapping['lx'] == 0
        assert handler.axis_mapping['ly'] == 1
        assert handler.axis_mapping['rx'] == 2
        assert handler.axis_mapping['ry'] == 3
        assert handler.axis_mapping['lt'] == 4
        assert handler.axis_mapping['rt'] == 5
    
    def test_button_mapping(self):
        """测试按钮映射正确"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Xbox 360 Controller"
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        # 前 6 个按钮 (A/B/X/Y/LB/RB)
        assert handler.button_mapping[0] == JoyStickButtons.RDownButton
        assert handler.button_mapping[1] == JoyStickButtons.RRightButton
        assert handler.button_mapping[2] == JoyStickButtons.RLeftButton
        assert handler.button_mapping[3] == JoyStickButtons.RUpButton
        assert handler.button_mapping[4] == JoyStickButtons.LBumper
        assert handler.button_mapping[5] == JoyStickButtons.RBumper
        
        # 摇杆按下
        assert handler.button_mapping[8] == JoyStickButtons.LStickIn
        assert handler.button_mapping[9] == JoyStickButtons.RStickIn
    
    def test_hat_mapping(self):
        """测试 D-Pad 映射"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Xbox 360 Controller"
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        # X 轴
        assert handler.hat_mapping_x[-1] == JoyStickButtons.LLeftButton
        assert handler.hat_mapping_x[1] == JoyStickButtons.LRightButton
        
        # Y 轴
        assert handler.hat_mapping_y[-1] == JoyStickButtons.LDownButton
        assert handler.hat_mapping_y[1] == JoyStickButtons.LUpButton
    
    def test_is_joy_matching_id(self):
        """测试 is_joy 匹配 instance_id"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Xbox 360 Controller"
        mock_joy.get_instance_id.return_value = 42
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        assert handler.is_joy(42) is True
        assert handler.is_joy(43) is False
    
    def test_trigger_threshold(self):
        """测试 trigger 阈值"""
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Xbox 360 Controller"
        mock_state = Mock()
        
        handler = XBoxEventHandler.joy_add(mock_joy, mock_state)
        
        assert handler.TRIGGER_THRESHOLD == 0.3
        assert 0.0 < handler.TRIGGER_THRESHOLD < 1.0


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
