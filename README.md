# waterRPA_GUI

> 基于 Python 的桌面自动化 RPA 工具，提供图形化界面编排和执行键鼠自动化脚本。

项目来源：https://github.com/PPJUST/waterRPA_GUI.git

---

## 功能特性

- **可视化命令编排**：拖拽排序，16 种命令类型自由组合
- **键鼠录制**：实时录制操作，自动转为命令序列
- **图像识别**：截图匹配、移动到/点击图片位置，支持可调置信度
- **循环执行**：可配置循环次数（0=无限），支持**坐标每轮自动步进**
- **多配置文件**：保存/加载多套方案，JSON 格式便于迁移
- **紧急停止**：ESC 全局热键即时中止
- **快捷键保存**：Ctrl+S 保存当前配置
- **备注注释**：每条命令支持备注说明
- **示教坐标**：点击屏幕直接获取鼠标坐标

---

## 技术栈

| 类别 | 技术 |
|------|------|
| GUI 框架 | PySide6 (Qt for Python) |
| 键盘操作 | Pynput（全局热键、可靠修饰键） |
| 鼠标模拟 | PyAutoGUI |
| 图像处理 | Pillow、NumPy、OpenCV |
| 配置格式 | JSON |
| 打包 | PyInstaller + UPX |

---

## 快速开始

### 环境要求

- Python 3.8+
- Windows

### 安装

```bash
pip install -r requirements.txt
python main.py
```

### 打包

```bash
pip install pyinstaller
pyinstaller main.spec
# 产物: dist\waterRPA\waterRPA.exe
```

---

## 命令类型（16 种）

| 类别 | 命令 | 说明 |
|------|------|------|
| 🖱️ 鼠标 | 点击 | 坐标 + 按键 + 次数 + 间隔 |
| | 移动(绝对) | 时间 + 目标坐标 |
| | 移动(相对) | 方向 + 距离 |
| | 按下 / 释放 | 坐标 + 按键 |
| | 滚轮 | 方向 + 距离 |
| ⌨️ 键盘 | 快捷键 | 支持录制，可靠修饰键 |
| | 按键序列 | 多键依次敲击 |
| | 按下 / 释放 | 单键控制 |
| | 粘贴文本 | 剪贴板粘贴或输入文本 |
| ⏱️ 等待 | 固定等待 | 秒数 |
| | 随机等待 | 区间随机 |
| 📷 截图 | 全屏截图 | 保存路径 |
| | 移动到图片 | 匹配图片 → 移动鼠标 |
| | 点击图片 | 匹配图片 → 点击 |

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `ESC` | 紧急停止执行 |
| `Ctrl+S` | 保存当前配置 |

---

## 目录结构

```
waterRPA_GUI/
├── main.py
├── main.spec                        # PyInstaller 打包配置
├── requirements.txt
├── .gitignore
├── README.md
├── qt.conf                          # Qt DPI 配置
├── icon/main.ico                    # 程序图标
├── module/
│   ├── constant_default.py
│   ├── function_config.py           # JSON 配置读写
│   ├── function_general.py
│   ├── function_pyautogui.py        # 鼠标/键盘/截图/寻图（pynput 后端）
│   ├── function_pynput.py           # 键鼠录制
│   ├── function_convert_command.py
│   ├── function_convert_listener.py
│   └── thread_run_commands.py       # 执行线程（支持中止）
└── ui/
    ├── ui_main.py
    ├── widget_command_control.py    # 命令行容器（含备注）
    ├── widget_listener.py
    ├── widget_moved_list_widget.py
    ├── widget_screenshot.py
    └── widget_command/              # 16 个命令控件
        └── *.py
```

---

## 配置格式

配置文件为 JSON，存储在 `configs/{配置名}/` 目录：

- `global.json` — 全局设置（循环次数、指令间隔、寻图超时）
- `configs/{配置名}/widget_command.json` — 命令序列
- `configs/{配置名}/*.png` — 截图/选图文件

首次启动自动将旧 `.ini` 文件迁移为 `.json`。

---

## 架构

```
main.py (QMainWindow)
  ├─ ui/           Qt 界面层
  └─ module/       核心逻辑层
       ├─ pyautogui   鼠标/截图/寻图（pynput 键盘）
       ├─ pynput      录制 + 全局热键
       ├─ config      JSON 读写
       └─ thread      命令执行（QThread）
```

命令执行在子线程中运行，不阻塞 UI。键盘操作统一使用 pynput（替代 pyautogui 的键盘 API，解决 Windows 修饰键丢失问题）。

