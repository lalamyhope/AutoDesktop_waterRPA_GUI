# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
打包命令: pyinstaller main.spec
"""

import os
import sys

# ---- 项目根目录 ----
PROJECT_ROOT = SPECPATH  # PyInstaller 提供的 spec 文件所在目录
ICON_DIR = os.path.join(PROJECT_ROOT, 'icon')

# ---- UPX 路径（命令行指定优先，否则从 venv 查找）----
import subprocess
_upx_check = subprocess.run(['where', 'upx'], capture_output=True, text=True)
UPX_DIR = os.path.dirname(_upx_check.stdout.strip().splitlines()[0]) if _upx_check.returncode == 0 else None

# ---- 隐式导入模块 ----
hidden_imports = [
    # PySide6 核心模块
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    # pyautogui 平台适配
    'pyautogui._pyautogui_win',
    # pynput 平台适配
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    # PIL / Pillow 图像插件
    'PIL._imaging',
    'PIL.Image',
    # opencv
    'cv2',
    'numpy',
    # 其他
    'filetype',
    'send2trash',
    'pyperclip',
    # 项目内部导入（避免动态导入遗漏）
    'module.function_general',
    'module.function_config',
    'module.function_pyautogui',
    'module.function_pynput',
    'module.function_convert_command',
    'module.function_convert_listener',
    'module.thread_run_commands',
    'module.constant_default',
    'ui.ui_main',
    'ui.widget_command_control',
    'ui.widget_listener',
    'ui.widget_moved_list_widget',
    'ui.widget_screenshot',
    'ui.widget_command.command_click_image_position',
    'ui.widget_command.command_key_in_hotkey',
    'ui.widget_command.command_key_in_keys',
    'ui.widget_command.command_key_press',
    'ui.widget_command.command_key_release',
    'ui.widget_command.command_mouse_click',
    'ui.widget_command.command_mouse_move_absolute',
    'ui.widget_command.command_mouse_move_relative',
    'ui.widget_command.command_mouse_press',
    'ui.widget_command.command_mouse_release',
    'ui.widget_command.command_mouse_scroll',
    'ui.widget_command.command_move_to_image_position',
    'ui.widget_command.command_paste_text',
    'ui.widget_command.command_screenshot_fullscreen',
    'ui.widget_command.command_wait_time',
    'ui.widget_command.command_wait_time_random',
    'ui.widget_command.command_base_image_position',
]

# ---- 数据文件 ----
datas = [
    (f'{ICON_DIR}/*', 'icon'),  # 图标目录
]

# ---- 排除不需要的大型模块 ----
excluded_modules = [
    'matplotlib',
    'scipy',
    'pandas',
    'IPython',
    'jupyter',
    'notebook',
    'tornado',
    'tkinter',
    'PyQt5',
    # PySide6 重型子模块（本项目未使用）
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngine',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DRender',
    'PySide6.Qt3DInput',
    'PySide6.Qt3DLogic',
    'PySide6.Qt3DAnimation',
    'PySide6.Qt3DExtras',
    'PySide6.QtCharts',
    'PySide6.QtDataVisualization',
    'PySide6.QtQuick',
    'PySide6.QtQuickWidgets',
    'PySide6.QtQml',
    'PySide6.QtQmlModels',
    'PySide6.QtOpenGLWidgets',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtNetwork',
    'PySide6.QtBluetooth',
    'PySide6.QtNfc',
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtPositioning',
    'PySide6.QtSql',
    'PySide6.QtTest',
    'PySide6.QtHelp',
    'PySide6.QtSvgWidgets',
    'PySide6.QtAxContainer',
    'PySide6.QtDesigner',
    'PySide6.QtUiTools',
    'PySide6.QtPrintSupport',
    'PySide6.QtPdf',
    'PySide6.QtPdfWidgets',
    'PySide6.QtHttpServer',
    'PySide6.QtSpatialAudio',
    'PySide6.QtTextToSpeech',
    'PySide6.QtVirtualKeyboard',
]

# ============================================================
# PyInstaller Analysis
# ============================================================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    noarchive=False,
    optimize=0,
)

# ---- 过滤掉未使用的 Qt 重型 DLL ----
_qt_exclude = {
    'Qt6Quick', 'Qt6QuickWidgets', 'Qt6Qml', 'Qt6QmlModels',
    'Qt6Pdf', 'Qt6PdfWidgets',
    'Qt6WebEngine', 'Qt6WebEngineCore', 'Qt6WebEngineWidgets',
    'Qt63D', 'Qt6Charts', 'Qt6DataVisualization',
    'Qt6Sensors', 'Qt6SerialPort', 'Qt6Bluetooth', 'Qt6Nfc',
    'Qt6Multimedia', 'Qt6MultimediaWidgets',
    'Qt6Positioning', 'Qt6Sql', 'Qt6Test', 'Qt6Help',
    'Qt6SvgWidgets', 'Qt6AxContainer', 'Qt6Designer',
    'Qt6PrintSupport', 'Qt6HttpServer', 'Qt6SpatialAudio',
    'Qt6TextToSpeech', 'Qt6VirtualKeyboard',
    'opengl32sw',  # 软件 OpenGL 渲染器，桌面应用不需要
}
# 额外剔除：opencv 视频模块（本项目仅用图像匹配）
_extra_exclude = {
    'opencv_videoio',
    'opencv_videoio_ffmpeg',
}
_filtered_binaries = [(name, path, 'BINARY') for name, path, _ in a.binaries
                      if not any(ex in name for ex in _qt_exclude | _extra_exclude)]
a.binaries = _filtered_binaries

# ============================================================
# PyInstaller PYZ
# ============================================================
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# ============================================================
# EXE - 单文件打包（分发方便，但体积较大）
# ============================================================
# exe = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.datas,
#     [],
#     name='AutoDesktop_water',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=False,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
#     icon=os.path.join(PROJECT_ROOT, 'icon', 'main.ico'),
# )

# ============================================================
# COLLECT - 目录模式（启动更快，压缩后分发体积更小）
# ============================================================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoDesktop_water',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_ROOT, 'icon', 'main.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoDesktop_water',
)
