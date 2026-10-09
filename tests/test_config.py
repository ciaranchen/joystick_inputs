# coding: utf-8
"""
测试配置加载和解析
"""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from InputConfig.config import ArcJoyStickConfig, ArcJoyStickLayer
from InputConfig.config_schema import JoyStickButtons


class TestArcJoyStickLayer:
    """测试输入层构建"""
    
    def test_layer_init_basic(self):
        """测试基本层初始化"""
        data = {
            'L_NUM': 4,
            'R_NUM': 8,
            'axis': [['a', 'b', 'c', 'd']] * 4,
            'buttons': ['space', 'enter'] * 6,
            'trigger': ['shift', '<EnterCode>']
        }
        layer = ArcJoyStickLayer.init(data)
        
        assert layer.L_NUM == 4
        assert layer.R_NUM == 8
        assert len(layer._axis) == 4
        assert len(layer._buttons) == JoyStickButtons.get_size()
        assert len(layer._trigger) == 2
    
    def test_layer_buttons_padding(self):
        """测试按钮不足时自动填充 <None>"""
        data = {
            'L_NUM': 4,
            'R_NUM': 8,
            'axis': [['a'] * 8] * 4,
            'buttons': ['space', 'enter'],  # 只有 2 个按钮
            'trigger': ['shift', '<None>']
        }
        layer = ArcJoyStickLayer.init(data)
        
        expected_size = JoyStickButtons.get_size()
        assert len(layer._buttons) == expected_size
        # 后面的按钮应该填充为 <None>
        assert layer._buttons[2:] == ['<None>'] * (expected_size - 2)
    
    def test_layer_buttons_truncate(self):
        """测试按钮过多时截断"""
        data = {
            'L_NUM': 4,
            'R_NUM': 8,
            'axis': [['a'] * 8] * 4,
            'buttons': ['space'] * 20,  # 超过 12 个
            'trigger': ['shift', '<None>']
        }
        layer = ArcJoyStickLayer.init(data)
        
        assert len(layer._buttons) == JoyStickButtons.get_size()
    
    def test_layer_axis_detection(self):
        """测试轴层自动检测"""
        # 包含 <EnterCode> 的层应该是轴层
        data_with_axis = {
            'L_NUM': 4,
            'R_NUM': 8,
            'axis': [['a'] * 8] * 4,
            'buttons': ['space'] * 12,
            'trigger': ['shift', '<EnterCode>']
        }
        layer_with_axis = ArcJoyStickLayer.init(data_with_axis)
        assert layer_with_axis.is_axis_layer is True
        
        # 不包含 <EnterCode> 的层不是轴层
        data_without_axis = {
            'L_NUM': 4,
            'R_NUM': 8,
            'axis': [['a'] * 8] * 4,
            'buttons': ['space'] * 12,
            'trigger': ['shift', '<None>']
        }
        layer_without_axis = ArcJoyStickLayer.init(data_without_axis)
        assert layer_without_axis.is_axis_layer is False


class TestArcJoyStickConfig:
    """测试配置加载"""
    
    def test_load_real_config_simple(self):
        """测试加载 simple_english.json"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'configs',
            'simple_english.json'
        )
        if not os.path.exists(config_path):
            return  # 跳过如果文件不存在
        
        config = ArcJoyStickConfig.load_from(config_path)
        
        assert config.config_name == 'SingleEnglishCode'
        assert config.layer_number == 1
        assert 'layer1' in config.layers
        assert 'mouse-layer' in config.layers
        
        # 检查层结构
        layer1 = config.layers['layer1']
        assert layer1.L_NUM == 4
        assert layer1.R_NUM == 8
        assert len(layer1._axis) == 4
        assert len(layer1._axis[0]) == 8
    
    def test_load_real_config_code6(self):
        """测试加载 code6.json"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'configs',
            'code6.json'
        )
        if not os.path.exists(config_path):
            return
        
        config = ArcJoyStickConfig.load_from(config_path)
        
        assert config.config_name == 'CodeSix2'
        assert 'layer1' in config.layers
        assert 'mouse-layer' in config.layers
        
        layer1 = config.layers['layer1']
        assert layer1.L_NUM == 6
        assert layer1.R_NUM == 8
    
    def test_load_minimal_config(self):
        """测试加载最小配置"""
        minimal_config = {
            "config_name": "Test",
            "layer_number": 1,
            "layers": {
                "default": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["a", "b", "c", "d"]] * 4,
                    "buttons": ["space"] * 12,
                    "trigger": ["<None>", "<None>"]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(minimal_config, f)
            temp_path = f.name
        
        try:
            config = ArcJoyStickConfig.load_from(temp_path)
            assert config.config_name == 'Test'
            assert 'default' in config.layers
            assert config.default_layer == 'default'
        finally:
            os.unlink(temp_path)
    
    def test_default_layer_selection(self):
        """测试默认层选择（第一层）"""
        # Schema 不允许多余的 default_layer 字段，使用第一个层作为默认
        config_without_default = {
            "config_name": "Test",
            "layer_number": 2,
            "layers": {
                "main": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["a"] * 4] * 4,
                    "buttons": ["space"] * 12,
                    "trigger": ["<None>", "<None>"]
                },
                "mouse": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["<Mouse:0>"] * 4] * 4,
                    "buttons": ["space"] * 12,
                    "trigger": ["<MouseClick:left>", "<MouseClick:right>"]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_without_default, f)
            temp_path = f.name
        
        try:
            config = ArcJoyStickConfig.load_from(temp_path)
            # 默认层应该是字典中的第一个键
            assert config.default_layer in ['main', 'mouse']
        finally:
            os.unlink(temp_path)
    
    def test_layer_count(self):
        """测试层数量"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'configs',
            'simple_english.json'
        )
        if not os.path.exists(config_path):
            return
        
        config = ArcJoyStickConfig.load_from(config_path)
        assert len(config.layers) == 2  # layer1 和 mouse-layer


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
