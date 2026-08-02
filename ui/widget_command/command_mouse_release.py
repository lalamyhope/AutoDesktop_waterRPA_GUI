from PySide6.QtCore import *
from PySide6.QtWidgets import *
from pynput import mouse as pynput_mouse

from module.constant_default import *


def _teach_coordinates(xs, ys, btn):
    btn.setEnabled(False)
    btn.setText("click...")
    def cb(x,y,b,p):
        if p:
            xs.setValue(int(x))
            ys.setValue(int(y))
            li.stop()
            btn.setEnabled(True)
            btn.setText("示教")
        return False
    li = pynput_mouse.Listener(on_click=cb)
    li.start()


class CommandMouseRelease(QWidget):
    signal_args = Signal(dict)
    def __init__(self):
        super().__init__()
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.row1 = QHBoxLayout()
        self.row1.setSpacing(3)

        self.label_pos = QLabel("坐标 (X")
        self.row1.addWidget(self.label_pos)

        self.spinBox_x = QSpinBox()
        self.spinBox_x.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinBox_x.setMaximum(max_x)
        self.spinBox_x.setValue(default_x)
        self.spinBox_x.setToolTip("X坐标")
        self.row1.addWidget(self.spinBox_x)

        self.label_comma = QLabel(", Y")
        self.row1.addWidget(self.label_comma)

        self.spinBox_y = QSpinBox()
        self.spinBox_y.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinBox_y.setMaximum(max_y)
        self.spinBox_y.setValue(default_y)
        self.spinBox_y.setToolTip("Y坐标")
        self.row1.addWidget(self.spinBox_y)

        self.label_paren = QLabel(") ")
        self.row1.addWidget(self.label_paren)

        self.toolButton_teach = QToolButton()
        self.toolButton_teach.setText("示教")
        self.toolButton_teach.setToolTip("点击获取坐标")
        self.row1.addWidget(self.toolButton_teach)

        self.label_5 = QLabel("释放")
        self.row1.addWidget(self.label_5)

        self.comboBox_button = QComboBox()
        self.comboBox_button.addItems(["左键","右键","中键"])
        self.comboBox_button.setCurrentText(default_button)
        self.row1.addWidget(self.comboBox_button)

        self.checkBox_once = QCheckBox("仅首次")
        self.checkBox_once.setToolTip("循环中仅首次执行")
        self.row1.addWidget(self.checkBox_once)

        self.verticalLayout.addLayout(self.row1)

        self.row2 = QHBoxLayout()
        self.row2.setSpacing(3)

        self.checkBox_loop_step = QCheckBox("循环递增")
        self.checkBox_loop_step.setToolTip("每轮循环坐标自动累加")
        self.row2.addWidget(self.checkBox_loop_step)
        self.label_sx = QLabel("DX")
        self.row2.addWidget(self.label_sx)
        self.spinBox_step_x = QSpinBox()
        self.spinBox_step_x.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinBox_step_x.setMaximum(9999)
        self.spinBox_step_x.setMinimum(-9999)
        self.spinBox_step_x.setValue(default_step_x)
        self.spinBox_step_x.setFixedWidth(55)
        self.row2.addWidget(self.spinBox_step_x)
        self.label_sy = QLabel("DY")
        self.row2.addWidget(self.label_sy)
        self.spinBox_step_y = QSpinBox()
        self.spinBox_step_y.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinBox_step_y.setMaximum(9999)
        self.spinBox_step_y.setMinimum(-9999)
        self.spinBox_step_y.setValue(default_step_y)
        self.spinBox_step_y.setFixedWidth(55)
        self.row2.addWidget(self.spinBox_step_y)
        self.row2.addStretch()

        self.verticalLayout.addLayout(self.row2)

        self.args_dict = default_args_dict.copy()
        self.check_args()
        self.send_args()

        self.comboBox_button.currentTextChanged.connect(self.send_args)
        self.spinBox_x.valueChanged.connect(self.send_args)
        self.spinBox_y.valueChanged.connect(self.send_args)
        self.checkBox_once.stateChanged.connect(self.send_args)
        self.spinBox_step_x.valueChanged.connect(self.send_args)
        self.spinBox_step_y.valueChanged.connect(self.send_args)
        self.checkBox_loop_step.stateChanged.connect(self.send_args)
        self.toolButton_teach.clicked.connect(lambda: _teach_coordinates(self.spinBox_x, self.spinBox_y, self.toolButton_teach))

    def load_args(self, args_dict):
        self.args_dict = dict(args_dict)
        self.comboBox_button.setCurrentText(args_dict["button"])
        self.spinBox_x.setValue(args_dict.get("x", default_x))
        self.spinBox_y.setValue(args_dict.get("y", default_y))
        self.checkBox_once.setChecked(args_dict.get("run_mode", "every") == "once")
        self.spinBox_step_x.setValue(args_dict.get("step_x", default_step_x))
        self.spinBox_step_y.setValue(args_dict.get("step_y", default_step_y))
        self.checkBox_loop_step.setChecked(args_dict.get("step_x", 0) != 0 or args_dict.get("step_y", 0) != 0)

    def check_args(self):
        pass

    def send_args(self):
        self.args_dict["button"] = self.comboBox_button.currentText()
        self.args_dict["x"] = self.spinBox_x.value()
        self.args_dict["y"] = self.spinBox_y.value()
        self.args_dict["run_mode"] = "once" if self.checkBox_once.isChecked() else "every"
        self.args_dict["step_x"] = self.spinBox_step_x.value() if self.checkBox_loop_step.isChecked() else 0
        self.args_dict["step_y"] = self.spinBox_step_y.value() if self.checkBox_loop_step.isChecked() else 0
        self.signal_args.emit(self.args_dict)
