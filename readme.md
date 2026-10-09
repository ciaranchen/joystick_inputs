# 手柄输入法

使用游戏手柄代替键盘进行文字输入——可以躺着打字。

通过左右摇杆的方向组合（扇区），映射到键盘上的字符。支持多层配置、按钮映射、鼠标模式等。

## 功能

- 🎮 **双摇杆扇区输入**：左摇杆选择行，右摇杆选择列，RT 确认输入
- 📐 **JSON 配置**：键盘布局通过 `configs/*.json` 定义，可自定义
- 🖱️ **鼠标模式**：切换到鼠标控制层，用摇杆操控光标
- 🔄 **多层切换**：支持按键/按住切换不同输入层
- 💀 **死区滤波**：消除摇杆漂移，轴值仅在有效变化时触发
- ⚡ **60Hz 轮询**：16ms 延迟，流畅响应

## 使用方法

```bash
pip install -r requirements.txt
python main.py
```

推动左右摇杆到目标方向，按 RT（右扳机）输入对应字符。

## 配置

编辑 `configs/` 下的 JSON 文件来自定义键盘布局：

- `code6.json` — 默认 6×8 英文布局（含 F 键、数字层）
- `simple_english.json` — 4×8 简易英文布局
- `english_code_ex.json` — 4×8 扩展英文布局

### 配置格式

```json
{
  "config_name": "MyLayout",
  "layer_number": 1,
  "layers": {
    "layer1": {
      "L_NUM": 6,
      "R_NUM": 8,
      "axis": [["space", "t", "a", "i", "n", "s", "h", "r"], ...],
      "buttons": ["space", "enter", "backspace", ...],
      "trigger": ["shift", "<EnterCode>"]
    }
  }
}
```

特殊函数标记：
- `<None>` — 空操作
- `<EnterCode>` — 输入当前摇杆方向对应的字符
- `<PressToLayer:name>` — 切换到指定层
- `<HoldToLayer:name>` — 按住切换到指定层
- `<MouseClick:left>` — 鼠标点击（left/right/middle）

## 项目结构

```
├── main.py                  # 入口：Qt 应用 + pygame 轮询循环
├── main.qml                 # QML 界面
├── src/
│   └── core.py              # ArcInputCore：扇区计算 + 动作分发
├── InputConfig/
│   ├── config.py            # 配置加载（JSON → 可调用对象）
│   ├── config_schema.py     # Schema 验证 + 按钮枚举
│   └── functions.py         # 动作控制器（键盘/鼠标/层切换）
├── JoyStick/
│   ├── joystick_state.py    # Qt Property 状态绑定
│   └── pygame_joysticks.py  # pygame 事件处理 + 死区滤波
├── configs/                 # JSON 键盘布局配置
├── utils/
│   └── qt_decorator.py      # Qt Property 元类工具
└── bigram_playground.py     # 字母频率分析（辅助布局设计）
```

## 支持的手柄

| 手柄 | 状态 |
|------|------|
| Xbox 360 | ✅ 完整支持 |
| JoyCon | 🔧 框架存在，待补全 |

## Reference

> `bigram-pairs.json` from: https://gist.github.com/lydell/c439049abac2c9226e53#file-pairs-json
