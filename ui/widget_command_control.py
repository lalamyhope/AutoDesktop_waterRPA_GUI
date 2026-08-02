"""命令控件组，命令行相关操作在该模块实现"""

from PySide6.QtCore import *
from PySide6.QtGui import *

from module.function_convert_command import *


class WidgetCommandControl(QWidget):
    """整行指令控件组，作为内部指令行的容器"""
    signal_send_args = Signal(dict)  # 子控件信号的中转发送

    def __init__(self):
        super().__init__()
        self.verticalLayout_main = QVBoxLayout(self)
        self.verticalLayout_main.setSpacing(1)
        self.verticalLayout_main.setContentsMargins(3, 2, 3, 2)

        # ---- 第 1 行：备注 ----
        self.row_comment = QHBoxLayout()
        self.row_comment.setSpacing(3)
        self.label_comment = QLabel('备注')
        self.label_comment.setFixedWidth(28)
        self.label_comment.setStyleSheet('color: #888;')
        self.row_comment.addWidget(self.label_comment)
        self.lineEdit_comment = QLineEdit()
        self.lineEdit_comment.setPlaceholderText('命令备注/说明（可选）')
        self.lineEdit_comment.setStyleSheet('color: #666; font-size: 11px;')
        self.row_comment.addWidget(self.lineEdit_comment)
        self.verticalLayout_main.addLayout(self.row_comment)

        # ---- 第 2 行：操作控件 ----
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(3)

        self.label_index = QLabel()
        self.label_index.setFixedWidth(24)
        self.label_index.setAlignment(Qt.AlignCenter)
        self.label_index.setStyleSheet('color: #888;')
        self.horizontalLayout.addWidget(self.label_index)

        self.toolButton_state = QToolButton()
        self.toolButton_state.setText('✏')
        self.toolButton_state.setAutoRaise(True)
        self.toolButton_state.setFixedSize(28, 28)
        self.toolButton_state.setToolTip('执行状态：✏编辑  ⏳等待  ✅成功  ❌失败')
        self.horizontalLayout.addWidget(self.toolButton_state)

        self.toolButton_add_command = QToolButton()
        self.toolButton_add_command.setText('＋')
        self.toolButton_add_command.setFixedSize(28, 28)
        self.toolButton_add_command.setToolTip('在下方插入新命令行')
        self.horizontalLayout.addWidget(self.toolButton_add_command)

        self.toolButton_copy_command = QToolButton()
        self.toolButton_copy_command.setText('📋')
        self.toolButton_copy_command.setFixedSize(28, 28)
        self.toolButton_copy_command.setToolTip('复制当前命令行')
        self.horizontalLayout.addWidget(self.toolButton_copy_command)

        self.toolButton_delete_command = QToolButton()
        self.toolButton_delete_command.setText('✕')
        self.toolButton_delete_command.setFixedSize(28, 28)
        self.toolButton_delete_command.setToolTip('删除当前命令行')
        self.horizontalLayout.addWidget(self.toolButton_delete_command)

        self.comboBox_select_command = QComboBox()
        self.comboBox_select_command.addItems(list(command_chs_to_en_dict.keys()))
        self.comboBox_select_command.setFixedWidth(130)
        self.comboBox_select_command.setToolTip('选择命令类型')
        setattr(self.comboBox_select_command, "wheelEvent", lambda a: None)
        self.horizontalLayout.addWidget(self.comboBox_select_command)

        self.widget_command_setting = QWidget()
        self.horizontalLayout_command_setting = QHBoxLayout()
        self.horizontalLayout_command_setting.setSpacing(0)
        self.horizontalLayout_command_setting.setContentsMargins(0, 0, 0, 0)
        self.widget_command_setting.setLayout(self.horizontalLayout_command_setting)
        self.horizontalLayout.addWidget(self.widget_command_setting)

        self.horizontalLayout.setStretch(5, 1)

        self.verticalLayout_main.addLayout(self.horizontalLayout)

        # 连接备注框的变更信号
        self.lineEdit_comment.textChanged.connect(self._update_comment)
        self.comboBox_select_command.currentTextChanged.connect(self.select_command)

        """
        初始化
        """
        self.args_dict = default_args_dict.copy()

    def load_command_args(self, args_dict):
        """加载命令参数"""
        if args_dict:
            self.args_dict = args_dict
        self.lineEdit_comment.setText(self.args_dict.get('other', ''))
        command_type = self.args_dict.get('command_type', '')
        if command_type and command_type in command_en_to_chs_dict:
            command_type = command_en_to_chs_dict[command_type]
        if command_type:
            # 阻止 setCurrentText 触发的信号，避免重复创建
            self.comboBox_select_command.blockSignals(True)
            self.comboBox_select_command.setCurrentText(command_type)
            self.comboBox_select_command.blockSignals(False)
            self.select_command(command_type)

    def set_sequence_number(self, number: int):
        """设置序号显示"""
        self.label_index.setText(str(number))

    def _update_comment(self):
        """备注文本变化时更新 args_dict"""
        self.args_dict['other'] = self.lineEdit_comment.text()

    def select_command(self, command_type_chs: str):
        """选择命令"""
        # 先清空
        layout = self.widget_command_setting.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 再添加
        convert = CommandConvert(command_type_chs)
        command_widget_object = convert.get_widget_object()
        command_type_en = convert.get_command_type()
        self.args_dict['command_type'] = command_type_en  # 写入指令名
        if command_widget_object:
            command_widget = command_widget_object()
            # 使用 copy 避免 __init__ 中 send_args 修改共享字典
            command_widget.load_args(dict(self.args_dict))
            layout.addWidget(command_widget)
            command_widget.signal_args.connect(self.get_command_signal)
            command_widget.send_args()  # 执行一次子控件的发送信号函数，用于发送初始数据

    def get_command_signal(self, args_dict):
        """获取子控件的信号，并发送"""
        self.signal_send_args.emit(args_dict)


def _test_widget():
    # 测试显示效果
    app = QApplication([])
    window = QWidget()
    # --------------
    test = WidgetCommandControl()
    # -------------
    layout = QVBoxLayout()
    layout.addWidget(test)
    window.setLayout(layout)
    window.show()
    app.exec_()


if __name__ == "__main__":
    _test_widget()
