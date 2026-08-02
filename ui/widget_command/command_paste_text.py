from PySide6.QtCore import *
from PySide6.QtWidgets import *

from module.constant_default import *


class CommandPasteText(QWidget):
    signal_args = Signal(dict)

    def __init__(self):
        super().__init__()
        self.horizontalLayout = QHBoxLayout(self)

        self.label_2 = QLabel('粘贴')
        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit_message = QLineEdit()
        self.lineEdit_message.setPlaceholderText('输入文本')
        if default_message:
            self.lineEdit_message.setText(default_message)
        self.horizontalLayout.addWidget(self.lineEdit_message)

        self.label_3 = QLabel('文本')
        self.horizontalLayout.addWidget(self.label_3)

        self.checkBox_clipboard = QCheckBox('使用剪贴板内容')
        self.checkBox_clipboard.setToolTip('勾选=直接粘贴剪贴板现有内容，不勾选=将上方文本复制到剪贴板后粘贴')
        self.checkBox_clipboard.setChecked(default_use_clipboard)
        self.horizontalLayout.addWidget(self.checkBox_clipboard)

        self.label_4 = QLabel('执行')
        self.horizontalLayout.addWidget(self.label_4)

        self.spinBox_presses = QSpinBox()
        self.spinBox_presses.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinBox_presses.setValue(default_presses)
        self.horizontalLayout.addWidget(self.spinBox_presses)

        self.label_5 = QLabel('次，间隔')
        self.horizontalLayout.addWidget(self.label_5)

        self.doubleSpinBox_interval = QDoubleSpinBox()
        self.doubleSpinBox_interval.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.doubleSpinBox_interval.setMaximum(max_interval)
        self.doubleSpinBox_interval.setValue(default_interval)
        self.horizontalLayout.addWidget(self.doubleSpinBox_interval)

        self.label_6 = QLabel('秒')
        self.horizontalLayout.addWidget(self.label_6)

        self.args_dict = default_args_dict.copy()
        self._toggle_input()
        self.check_args()
        self.send_args()

        self.lineEdit_message.textChanged.connect(self.send_args)
        self.spinBox_presses.valueChanged.connect(self.send_args)
        self.doubleSpinBox_interval.valueChanged.connect(self.send_args)
        self.checkBox_clipboard.stateChanged.connect(self._toggle_input)
        self.checkBox_clipboard.stateChanged.connect(self.send_args)

    def _toggle_input(self):
        checked = self.checkBox_clipboard.isChecked()
        self.lineEdit_message.setEnabled(not checked)
        if checked:
            self.lineEdit_message.setPlaceholderText('将粘贴剪贴板现有内容')
        else:
            self.lineEdit_message.setPlaceholderText('输入文本')

    def load_args(self, args_dict):
        self.args_dict = args_dict
        self.doubleSpinBox_interval.setValue(args_dict['interval'])
        self.lineEdit_message.setText(args_dict['message'])
        self.spinBox_presses.setValue(args_dict['presses'])
        self.checkBox_clipboard.setChecked(args_dict.get('use_clipboard', default_use_clipboard))
        self._toggle_input()

    def check_args(self):
        pass

    def send_args(self):
        self.args_dict['message'] = self.lineEdit_message.text()
        self.args_dict['presses'] = self.spinBox_presses.value()
        self.args_dict['interval'] = self.doubleSpinBox_interval.value()
        self.args_dict['use_clipboard'] = self.checkBox_clipboard.isChecked()
        self.signal_args.emit(self.args_dict)
