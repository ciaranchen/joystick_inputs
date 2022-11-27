# 手柄输入法

使用手柄来代替键盘输入。（可以躺着在电脑上输入

主要使用手柄的两个摇杆来进行输入，八项的两个摇杆可以映射到键盘上的64个键。

手柄的两个扳机可以用来表示确认输入或者其他组合键（如Shift）。

结合手柄的其他按键可以做出键盘的效果。（主要用于组合键）

> 这当然是个半成品…主要是，谁会真的完全使用手柄来输入呢？

## 使用方法

```bash
pip install -r requirements.txt
python main.py
```

![截图](readme.assets/屏幕截图%202022-11-27%20101951.png)

推动左右摇杆，选择合适的键盘输入。

按动右Trigger，输入内容。

## todo

1. 一些配置界面。
2. 代码重构
3. 其它键盘配置
4. 以特定格式文件表示的配置

## Reference

> bigram-pairs.json is from: https://gist.github.com/lydell/c439049abac2c9226e53#file-pairs-json