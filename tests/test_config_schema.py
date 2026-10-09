# coding: utf-8
"""
测试配置 Schema 验证
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import SchemaError
from InputConfig.config_schema import ConfigParser


class TestConfigParser:
    """测试配置验证器"""
    
    def setup_method(self):
        """每个测试前创建解析器"""
        self.parser = ConfigParser()
    
    def test_valid_minimal_config(self):
        """测试有效的最小配置"""
        valid_config = {
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
        result = self.parser.validate(valid_config)
        assert result['config_name'] == 'Test'
        assert result['layer_number'] == 1
    
    def test_valid_special_functions(self):
        """测试配置中的特殊函数"""
        config = {
            "config_name": "Test",
            "layer_number": 1,
            "layers": {
                "default": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["<None>", "<Mouse:0>", "<MouseClick:left>", "a"]],
                    "buttons": ["<PressToLayer:mouse>", "<HoldToLayer:main>", "<EnterCode>", "space"] * 3,
                    "trigger": ["shift", "<EnterCode>"]
                }
            }
        }
        result = self.parser.validate(config)
        assert result is not None
    
    def test_valid_keyboard_keys(self):
        """测试键盘按键（使用 pynput Key 枚举名）"""
        config = {
            "config_name": "Test",
            "layer_number": 1,
            "layers": {
                "default": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["a", "z", "1", "space"]],
                    "buttons": ["enter", "tab", "backspace", "space"] * 3,
                    "trigger": ["ctrl", "alt"]
                }
            }
        }
        result = self.parser.validate(config)
        assert result is not None
    
    def test_valid_pynput_keys(self):
        """测试 pynput Key 枚举"""
        config = {
            "config_name": "Test",
            "layer_number": 1,
            "layers": {
                "default": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["f1", "f12", "page_up", "insert"]],
                    "buttons": ["shift", "ctrl", "alt", "space"] * 3,
                    "trigger": ["<None>", "<None>"]
                }
            }
        }
        result = self.parser.validate(config)
        assert result is not None
    
    def test_invalid_missing_config_name(self):
        """测试缺少 config_name"""
        invalid_config = {
            "layer_number": 1,
            "layers": {}
        }
        try:
            self.parser.validate(invalid_config)
            assert False, "应该抛出 SchemaError"
        except SchemaError:
            pass
    
    def test_invalid_layer_number_zero(self):
        """测试 layer_number = 0"""
        invalid_config = {
            "config_name": "Test",
            "layer_number": 0,
            "layers": {}
        }
        try:
            self.parser.validate(invalid_config)
            assert False, "应该抛出 SchemaError"
        except SchemaError:
            pass
    
    def test_invalid_layer_number_too_large(self):
        """测试 layer_number 过大"""
        invalid_config = {
            "config_name": "Test",
            "layer_number": 10,
            "layers": {}
        }
        try:
            self.parser.validate(invalid_config)
            assert False, "应该抛出 SchemaError"
        except SchemaError:
            pass
    
    def test_invalid_trigger_count(self):
        """测试 trigger 数量不为 2"""
        invalid_config = {
            "config_name": "Test",
            "layer_number": 1,
            "layers": {
                "default": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": [["a"]],
                    "buttons": ["space"] * 12,
                    "trigger": ["<None>"]  # 只有 1 个
                }
            }
        }
        try:
            self.parser.validate(invalid_config)
            assert False, "应该抛出 SchemaError"
        except SchemaError:
            pass
    
    def test_invalid_axis_structure(self):
        """测试 axis 不是二维数组"""
        invalid_config = {
            "config_name": "Test",
            "layer_number": 1,
            "layers": {
                "default": {
                    "L_NUM": 4,
                    "R_NUM": 4,
                    "axis": ["a", "b", "c"],  # 一维数组
                    "buttons": ["space"] * 12,
                    "trigger": ["<None>", "<None>"]
                }
            }
        }
        try:
            self.parser.validate(invalid_config)
            assert False, "应该抛出 SchemaError"
        except SchemaError:
            pass
    
    def test_real_config_files(self):
        """测试实际配置文件都能通过验证"""
        configs_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'configs'
        )
        if not os.path.exists(configs_dir):
            return
        
        for filename in os.listdir(configs_dir):
            if filename.endswith('.json'):
                config_path = os.path.join(configs_dir, filename)
                with open(config_path, encoding='utf-8') as f:
                    data = json.load(f)
                
                try:
                    result = self.parser.validate(data)
                    assert result is not None, f"配置 {filename} 验证失败"
                except SchemaError as e:
                    raise AssertionError(f"配置 {filename} 验证失败: {e}")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
