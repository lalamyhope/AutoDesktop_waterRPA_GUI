from PySide6.QtCore import *
from PySide6.QtWidgets import *
from pynput import keyboard as pynput_keyboard

from module.constant_default import *


class CommandKeyInHotkey(QWidget):
    signal_args = Signal(dict)

    def __init__(self):
        super().__init__()
        self.horizontalLayout = QHBoxLayout(self)

        self.label_2 = QLabel('使用')
        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit_hotkeys = QLineEdit()
        self.lineEdit_hotkeys.setPlaceholderText('如: ctrl+c')
        if default_hotkey:
            self.lineEdit_hotkeys.setText(default_hotkey)
        self.horizontalLayout.addWidget(self.lineEdit_hotkeys)

        self.label_3 = QLabel('快捷键')
        self.horizontalLayout.addWidget(self.label_3)

        self.toolButton_record = QToolButton()
        self.toolButton_record.setText('录制')
        self.toolButton_record.setToolTip('点击后按下键盘组合键即可录制')
        self.horizontalLayout.addWidget(self.toolButton_record)

        self.args_dict = default_args_dict.copy()
        self.check_args()
        self.send_args()

        self.lineEdit_hotkeys.textChanged.connect(self.check_args)
        self.lineEdit_hotkeys.textChanged.connect(self.send_args)
        self.toolButton_record.clicked.connect(self._start_record)

    def _start_record(self):
        self.toolButton_record.setEnabled(False)
        self.toolButton_record.setText('请按键...')
        pressed_keys = set()
        modifier_order = []
        def on_press(key):
            try:
                if hasattr(key, 'name') and key.name:
                    name = key.name
                elif hasattr(key, 'char') and key.char:
                    # Ctrl+字母会产生控制字符 \\x01~\\x1a，还原为字母
                    ch = key.char
                    if len(ch) == 1 and ord(ch) < 32:
                        name = chr(ord(ch) + 96)  # \\x01→a, \\x03→c ...
                    else:
                        name = ch
                else:
                    name = str(key)
            except Exception:
                name = str(key)
            name = name.replace('cmd','win').replace('ctrl_l','ctrl').replace('ctrl_r','ctrl').replace('shift_l','shift').replace('shift_r','shift').replace('alt_l','alt').replace('alt_r','alt')
            if name not in pressed_keys:
                pressed_keys.add(name); modifier_order.append(name)
        def on_release(key):
            listener.stop()
            modifiers = {'ctrl','shift','alt','win'}
            mods = [k for k in modifier_order if k in modifiers]
            regular = [k for k in modifier_order if k not in modifiers]
            self.lineEdit_hotkeys.setText('+'.join(mods + regular))
            self.toolButton_record.setEnabled(True)
            self.toolButton_record.setText('录制')
        listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

    def load_args(self, args_dict):
        self.args_dict = args_dict
        hotkey = args_dict['hotkey']
        self.lineEdit_hotkeys.setText(hotkey)

    def check_args(self):
        pass

    def send_args(self):
        hotkey = self.lineEdit_hotkeys.text()
        self.args_dict['hotkey'] = hotkey
        self.signal_args.emit(self.args_dict)
