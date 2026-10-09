# coding: utf-8
"""
测试手柄工具函数
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from JoyStick.pygame_joysticks import clamp, DEAD_ZONE


class TestClamp:
    """测试 clamp 函数"""
    
    def test_clamp_in_range(self):
        """测试范围内的值不变"""
        assert clamp(0.0) == 0.0
        assert clamp(0.5) == 0.5
        assert clamp(-0.5) == -0.5
        assert clamp(1.0) == 1.0
        assert clamp(-1.0) == -1.0
    
    def test_clamp_above_upper(self):
        """测试超出上限的值"""
        assert clamp(1.5) == 1.0
        assert clamp(2.0) == 1.0
        assert clamp(100.0) == 1.0
    
    def test_clamp_below_lower(self):
        """测试低于下限的值"""
        assert clamp(-1.5) == -1.0
        assert clamp(-2.0) == -1.0
        assert clamp(-100.0) == -1.0
    
    def test_clamp_custom_range(self):
        """测试自定义范围"""
        assert clamp(5.0, 0.0, 10.0) == 5.0
        assert clamp(-5.0, 0.0, 10.0) == 0.0
        assert clamp(15.0, 0.0, 10.0) == 10.0
    
    def test_clamp_boundary_values(self):
        """测试边界值"""
        assert clamp(1.0, -1.0, 1.0) == 1.0
        assert clamp(-1.0, -1.0, 1.0) == -1.0
        assert clamp(0.0, -1.0, 1.0) == 0.0


class TestDeadZone:
    """测试死区常量"""
    
    def test_dead_zone_value(self):
        """测试死区阈值合理"""
        assert 0.0 < DEAD_ZONE < 1.0
        assert DEAD_ZONE == 0.15
    
    def test_dead_zone_effectiveness(self):
        """测试死区能过滤微小噪声"""
        # 小于死区的值应该被归零
        assert abs(0.05) < DEAD_ZONE
        assert abs(-0.1) < DEAD_ZONE
        assert abs(0.14) < DEAD_ZONE
        
        # 大于死区的值应该保留
        assert abs(0.2) >= DEAD_ZONE
        assert abs(-0.3) >= DEAD_ZONE
        assert abs(1.0) >= DEAD_ZONE


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
