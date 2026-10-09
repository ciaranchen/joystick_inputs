# 测试说明

本项目使用 pytest 进行测试。

## 安装测试依赖

```bash
pip install pytest
```

## 运行所有测试

```bash
pytest tests/
```

## 运行特定测试文件

```bash
pytest tests/test_arc.py
pytest tests/test_config.py
pytest tests/test_buttons.py
```

## 运行特定测试类或方法

```bash
pytest tests/test_arc.py::TestArc::test_arc_distance_center
pytest tests/test_config.py::TestArcJoyStickConfig
```

## 详细输出

```bash
pytest tests/ -v
```

## 测试覆盖率

安装 pytest-cov 后可以生成覆盖率报告：

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

## 测试文件说明

- `test_arc.py` - 测试扇区划分算法
- `test_buttons.py` - 测试手柄按钮枚举
- `test_functions.py` - 测试特殊函数识别
- `test_config.py` - 测试配置加载和解析
- `test_config_schema.py` - 测试配置验证
- `test_joystick_utils.py` - 测试手柄工具函数
- `test_event_handler.py` - 测试事件处理器
- `test_config_to_function.py` - 测试配置到函数的转换
