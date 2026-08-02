import os as _os
_os.environ['QT_LOGGING_RULES'] = 'qt.qpa.window=false'

from module.function_general import *
from module.thread_run_commands import *
from ui.ui_main import Ui_MainWindow
from ui.widget_command_control import *
from ui.widget_listener import *
from ui.widget_moved_list_widget import *

from PySide6.QtGui import QAction
from pynput import keyboard as pynput_keyboard

"""
行项目id data：1
控件组id property：'id'
"""


class Main(QMainWindow):
    # 状态图标文本（UTF-8 字符，无需 PNG 文件）
    _icon_wait_run = '⏳'
    _icon_complete = '✅'
    _icon_error = '❌'

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        """
        控件设置
        """
        # ---- 重写 UI 使用说明 ----
        self._setup_help_panel()
        self._setup_tooltips()
        self._setup_menubar()

        # 添加自定义listwidget控件
        layout = self.ui.groupBox_command.layout()
        self.listWidget_command_area = MovedListWidget()
        layout.addWidget(self.listWidget_command_area)
        self.listWidget_command_area.setDragEnabled(True)  # 启用拖动功能
        self.listWidget_command_area.setDragDropMode(QListWidget.InternalMove)  # 设置拖放模式为内部移动
        self.listWidget_command_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁止水平滚动条
        self.listWidget_command_area.setDefaultDropAction(Qt.TargetMoveAction)
        self.listWidget_command_area.itemMoved.connect(self.command_item_moved)

        # 连接信号与槽函数
        # ---- 重写按钮和标签文本 ----
        self.ui.groupBox_config.setTitle('📂 配置文件')
        self.ui.groupBox_function.setTitle('▶ 执行区')
        self.ui.groupBox_setting.setTitle('⚙️ 全局设置')
        self.ui.groupBox_command.setTitle('📋 命令列表（拖拽排序）')
        self.ui.label_3.setText('指令间隔(秒)')
        self.ui.label.setText('运行次数')
        self.ui.label_5.setText('寻图超时(秒)')
        self.ui.pushButton_start.setText('▶ 执行')
        self.ui.pushButton_stop.setText('⏹ 停止')
        self.ui.pushButton_listener.setText('🎤 录制')
        self.ui.toolButton_save_config.setText('💾')

        # ---- 固定静态控件尺寸 ----
        self.ui.comboBox_select_config.setFixedWidth(120)
        self.ui.toolButton_save_config.setFixedSize(28, 28)
        self.ui.toolButton_add_config.setFixedSize(28, 28)
        self.ui.toolButton_delete_config.setFixedSize(28, 28)
        self.ui.pushButton_start.setFixedWidth(70)
        self.ui.pushButton_stop.setFixedWidth(70)
        self.ui.pushButton_listener.setFixedWidth(70)
        self.ui.doubleSpinBox_global_wait_time.setFixedWidth(70)
        self.ui.spinBox_loop_time.setFixedWidth(60)
        self.ui.spinBox_find_image_timeout.setFixedWidth(60)

        # 连接信号与槽函数
        # 配置文件区
        self.ui.toolButton_add_config.clicked.connect(self.add_config)
        self.ui.toolButton_delete_config.clicked.connect(self.delete_config)
        self.ui.toolButton_save_config.clicked.connect(self.save_command_setting)
        self.ui.comboBox_select_config.currentTextChanged.connect(self.load_config_command)
        # 功能区
        self.ui.pushButton_start.clicked.connect(self.reset_runs_times)
        self.ui.pushButton_start.clicked.connect(self.run_commands)
        self.ui.pushButton_stop.clicked.connect(self.stop_run_commands)
        self.ui.pushButton_listener.clicked.connect(self.start_listener)
        # 全局设置区
        self.ui.doubleSpinBox_global_wait_time.valueChanged.connect(function_config.update_config_wait_time)
        self.ui.spinBox_loop_time.valueChanged.connect(function_config.update_config_loop_time)

        """
        初始设置
        """
        self.command_dict = dict()  # 各个命令行的参数设置，格式为{命令行id:{args_dict数据},...}
        self._widget_for_id = {}  # id → widget 快速查找映射
        function_config.check_default_config()
        pyautogui.FAILSAFE = True  # 启用自动防故障功能，左上角的坐标为（0，0），将鼠标移到屏幕的左上角，来抛出failSafeException异常
        pyautogui.PAUSE = 0  # pyautogui自带的延迟功能，默认延迟时间0.1秒，不使用该自带功能而使用time.sleep进行延迟时间的设置
        self.runs_times = 0  # 已运行次数，用于循环运行
        self._running = False  # 线程运行状态标记
        self.load_global_setting()  # 加载全局设置

        """
        多线程设置
        """
        self.thread_run_command = ThreadRunCommands()
        self.thread_run_command.signal_succeed.connect(self.run_commands_succeed)
        self.thread_run_command.signal_failed.connect(self.run_commands_failed)
        self.thread_run_command.signal_succeed.connect(self.scroll_to_item)
        self.thread_run_command.signal_failed.connect(self.scroll_to_item)
        self.thread_run_command.signal_finished.connect(self.run_commands_finished)
        self.thread_run_command.signal_error.connect(self.run_commands_error)
        self.thread_run_command.signal_aborted.connect(self.run_commands_aborted)

        # 全局 ESC 紧急停止热键 + Ctrl+S 保存
        self._hotkey_listener = pynput_keyboard.GlobalHotKeys({
            '<esc>': self._on_emergency_stop,
            '<ctrl>+s': self._on_save_shortcut,
        })
        self._hotkey_listener.start()

    def _find_widget_by_id(self, id_widget):
        """根据 id 快速查找 widget，利用缓存映射避免 O(n) 遍历"""
        widget = self._widget_for_id.get(id_widget)
        if widget is not None:
            return widget
        # 缓存未命中时回退遍历并更新缓存
        for i in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(i)
            w = self.listWidget_command_area.itemWidget(item)
            if w is not None:
                wid = w.property('id')
                self._widget_for_id[wid] = w
                if wid == id_widget:
                    return w
        return None

    def _rebuild_widget_map(self):
        """重建 id → widget 映射"""
        self._widget_for_id.clear()
        for i in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(i)
            w = self.listWidget_command_area.itemWidget(item)
            if w is not None:
                self._widget_for_id[w.property('id')] = w

    def _update_sequence_numbers(self):
        """更新所有命令行的序号显示"""
        for i in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(i)
            w = self.listWidget_command_area.itemWidget(item)
            if w is not None:
                w.set_sequence_number(i + 1)

    def _setup_help_panel(self):
        """设置右侧面板：隐藏原说明区，改为紧凑提示"""
        self.ui.groupBox_info.setVisible(False)
        # 释放右侧空间，命令列表区可自动扩展

    def _setup_tooltips(self):
        """设置各控件的鼠标悬停提示"""
        # 配置文件区
        self.ui.comboBox_select_config.setToolTip('选择要使用的配置方案')
        self.ui.toolButton_save_config.setToolTip('保存当前命令配置')
        self.ui.toolButton_add_config.setToolTip('新建配置方案')
        self.ui.toolButton_delete_config.setToolTip('删除当前配置方案')
        # 功能区
        self.ui.pushButton_start.setToolTip('开始执行命令序列\n快捷键：无')
        self.ui.pushButton_stop.setToolTip('停止执行（或按 ESC 键）')
        self.ui.pushButton_listener.setToolTip('录制鼠标键盘操作，按 ESC 结束录制')
        # 全局设置区
        self.ui.label_3.setToolTip('每条命令执行完后的等待时间')
        self.ui.doubleSpinBox_global_wait_time.setToolTip('数值越大执行越慢，0 表示无间隔')
        self.ui.label.setToolTip('命令序列循环执行次数')
        self.ui.spinBox_loop_time.setToolTip('0 = 无限循环，1 = 执行一次')
        self.ui.label_5.setToolTip('查找屏幕图片的超时时间')
        self.ui.spinBox_find_image_timeout.setToolTip('超时后该命令记为失败并终止执行')

    def _setup_menubar(self):
        """设置菜单栏"""
        menu_help = self.ui.menubar.addMenu('帮助(&H)')

        action_usage = QAction('使用说明(&U)', self)
        action_usage.triggered.connect(self._show_usage_dialog)
        menu_help.addAction(action_usage)

        action_about = QAction('关于(&A)', self)
        action_about.triggered.connect(self._show_about_dialog)
        menu_help.addAction(action_about)

    def _show_usage_dialog(self):
        """显示使用说明对话框（原右侧面板内容已全部迁移至此）"""
        text = (
            '═══════ AutoDesktop_water 使用指南 ═══════\n\n'
            '🚀 快速上手\n'
            '  1. 从下拉框选择命令类型，配置参数\n'
            '  2. 点击 [+] 添加命令行，拖拽调整顺序\n'
            '  3. 点击 [🎤录制] 可自动记录键鼠操作\n'
            '  4. 点击 [▶执行] 开始运行\n\n'
            '📋 可用命令类型（16 种）\n'
            '  鼠标：点击、移动(绝对/相对)、按下、释放、滚轮\n'
            '  键盘：按键序列、组合键、按下、释放\n'
            '  等待：固定等待、随机等待\n'
            '  截图：全屏截图、移动到图片位置、点击图片位置\n'
            '  其他：粘贴文本\n\n'
            '🎤 录制功能\n'
            '  点击 [录制] → 执行操作 → 按 ESC 结束\n'
            '  录制内容自动转为命令序列\n'
            '  注意：仅记录关键操作(点击/按键)，不记录移动轨迹\n\n'
            '🛑 紧急停止\n'
            '  · 运行中按键盘 ESC 键（即时生效）\n'
            '  · 或点击 [⏹停止] 按钮\n\n'
            '⚙️ 全局设置\n'
            '  · 运行次数 0 = 无限循环执行\n'
            '  · 指令间隔 = 每条命令间的等待秒数\n'
            '  · 寻图超时 = 图像搜索的最大等待秒数\n\n'
            '📂 配置文件\n'
            '  · 顶部下拉框可创建/切换多套自动化方案\n'
            '  · 💾 保存 | [+] 新建 | [-] 删除\n\n'
            '💡 操作提示\n'
            '  · 拖拽命令行可调整执行顺序\n'
            '  · 复制命令：点击 📋 图标\n'
            '  · 拖入图片到命令行的图片区域即可关联截图目标\n'
            '  · 鼠标悬停各控件可查看详细提示\n'
            '  · 录制后请注意调整指令间隔\n\n'
            '⌨️ 快捷键\n'
            '  · ESC = 紧急停止\n'
            '  · Ctrl+S = 保存当前配置\n\n'
            '⌨️ 更多帮助\n'
            '  · 鼠标悬停任意控件查看 ToolTip\n'
            '  · 状态图标：✏编辑 ⏳待执行 ✅成功 ❌失败'
        )
        box = QMessageBox(self)
        box.setWindowTitle('使用说明')
        box.setText(text)
        box.setIcon(QMessageBox.Information)
        box.resize(500, 550)
        box.exec()

    def _show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, '关于 AutoDesktop_water',
            'AutoDesktop_water GUI 版\n\n'
            '桌面自动化 RPA 工具\n'
            '基于 PySide6 + PyAutoGUI + Pynput\n\n'
            '项目来源: github.com/PPJUST/AutoDesktop_water_GUI'
        )

    """
    执行相关函数
    """

    def check_command_all_right(self):
        """检查存储的指令参数设置，判断是否启用执行按钮"""
        self.ui.pushButton_start.setEnabled(True)
        for args in self.command_dict.values():
            if args:  # 不考虑空的键值对
                args_all_right = args['args_all_right']
                if not args_all_right:
                    self.ui.pushButton_start.setEnabled(False)
                    break

    def get_args_signal(self, args_dict):
        """接收子控件传递的信号"""
        id_widget = self.sender().property('id')
        self.command_dict[id_widget] = args_dict
        self.check_command_all_right()
        # self.save_command_setting()  # 每次更新保存配置

    def run_commands(self):
        """执行指令"""
        # 执行前保存配置文件
        self.save_command_setting()
        # 重置图标
        self.reset_state_icon()
        # 禁用控件
        self.change_widget_enable(False)
        self._running = True
        # 坐标步进：首轮记录原始值，后续每轮累加
        if self.runs_times == 0:
            self._base_coords = {}  # {id_item: {'x':orig_x, 'y':orig_y}}
        # 获取每个行项目对应的指令函数
        command_function_dict = {}
        command_run_modes = {}
        for i in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(i)
            id_item = item.data(1)
            args_dict = dict(self.command_dict[id_item])  # 复制避免修改原数据
            # 应用步进
            if self.runs_times == 0:
                self._base_coords[id_item] = {'x': args_dict.get('x', 1), 'y': args_dict.get('y', 1)}
            else:
                base = self._base_coords.get(id_item, {})
                step_x = args_dict.get('step_x', 0)
                step_y = args_dict.get('step_y', 0)
                if step_x or step_y:
                    args_dict['x'] = base.get('x', 1) + step_x * self.runs_times
                    args_dict['y'] = base.get('y', 1) + step_y * self.runs_times
            command_type = args_dict['command_type']
            convert = CommandConvert(command_type)
            command_function = convert.get_function_object(args_dict)
            command_function_dict[id_item] = command_function
            command_run_modes[id_item] = args_dict.get('run_mode', 'every')
        # 子线程中执行
        self.thread_run_command.set_command_function(command_function_dict, command_run_modes)
        self.thread_run_command.start()

    def stop_run_commands(self):
        """终止指令"""
        self._running = False
        self.thread_run_command.abort()
        self.change_widget_enable(True)

    def change_widget_enable(self, enable=True):
        """执行或结束时启用或禁用相关控件"""
        if enable:
            # 配置文件
            self.ui.comboBox_select_config.setEnabled(True)
            self.ui.toolButton_save_config.setEnabled(True)
            self.ui.toolButton_add_config.setEnabled(True)
            self.ui.toolButton_delete_config.setEnabled(True)
            # 全局设置
            self.ui.doubleSpinBox_global_wait_time.setEnabled(True)
            self.ui.spinBox_loop_time.setEnabled(True)
            self.ui.spinBox_find_image_timeout.setEnabled(True)
            # 执行
            self.ui.pushButton_start.setEnabled(True)
            self.ui.pushButton_stop.setEnabled(False)
        else:
            # 配置文件
            self.ui.comboBox_select_config.setEnabled(False)
            self.ui.toolButton_save_config.setEnabled(False)
            self.ui.toolButton_add_config.setEnabled(False)
            self.ui.toolButton_delete_config.setEnabled(False)
            # 全局设置
            self.ui.doubleSpinBox_global_wait_time.setEnabled(False)
            self.ui.spinBox_loop_time.setEnabled(False)
            self.ui.spinBox_find_image_timeout.setEnabled(False)
            # 执行
            self.ui.pushButton_start.setEnabled(False)
            self.ui.pushButton_stop.setEnabled(True)

    def reset_state_icon(self):
        """重置状态图标"""
        for i in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(i)
            widget = self.listWidget_command_area.itemWidget(item)
            if widget:
                widget.toolButton_state.setText(Main._icon_wait_run)

    """
    接收多线程信号相关函数
    """

    def scroll_to_item(self, id_run):
        """滚动行项目到执行行"""
        for i in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(i)
            widget = self.listWidget_command_area.itemWidget(item)
            if widget is None:
                continue
            id_widget = widget.property('id')
            if id_widget == id_run:
                if i + 2 < self.listWidget_command_area.count():
                    scroll_to = self.listWidget_command_area.item(i + 2)
                    self.listWidget_command_area.scrollToItem(scroll_to)
                break

    def run_commands_succeed(self, id_succeed):
        """修改成功运行的行项目图标"""
        widget = self._find_widget_by_id(id_succeed)
        if widget:
            widget.toolButton_state.setText(Main._icon_complete)

    def run_commands_failed(self, id_failed):
        """修改运行失败的行项目图标"""
        widget = self._find_widget_by_id(id_failed)
        if widget:
            widget.toolButton_state.setText(Main._icon_error)

    def run_commands_error(self, error_message):
        """处理子线程的报错信息"""
        QMessageBox.warning(self, "错误", f"错误信息：【{error_message}】")

    def run_commands_aborted(self):
        """用户手动中止执行"""
        self.change_widget_enable(True)

    def _on_emergency_stop(self):
        """全局 ESC 热键回调：紧急停止"""
        if self._running:
            self.stop_run_commands()

    def _on_save_shortcut(self):
        """全局 Ctrl+S 热键回调：保存配置"""
        self.save_command_setting()
        self.statusBar().showMessage('配置已保存', 2000)

    def run_commands_finished(self, result_code):
        """全部行项目运行结束后，检查是否需要循环运行"""
        self._running = False
        if result_code:
            self.runs_times += 1
            loop_time = self.ui.spinBox_loop_time.value()
            if loop_time == 0:
                # 无限循环：直接递归调用
                self.run_commands()
            else:
                if self.runs_times < loop_time:
                    self.run_commands()
                else:
                    self.change_widget_enable(True)
        else:
            self.change_widget_enable(True)

    """
    命令控件相关函数
    """

    def load_config_command(self):
        """加载配置文件中的命令控件"""
        # 重置
        self.command_dict = dict()
        self.listWidget_command_area.clear()

        # 添加
        config = self.ui.comboBox_select_config.currentText()
        function_config.set_current_config(config)  # 同步当前配置名，供选图/截图使用
        command_list = function_config.get_command_list(config)
        for args_dict in command_list:
            self.insert_command_widget(args_dict=args_dict)

        # 如果命令行为空，则插入空行
        if self.listWidget_command_area.count() == 0:
            self.insert_command_widget()
        # 重建 widget 映射缓存
        self._rebuild_widget_map()
        # 刷新序号
        self._update_sequence_numbers()

    def insert_command_widget(self, args_dict: dict = None, index: int = None):
        """插入指令行控件
        传参：
        args_dict 指令设置的字典，用于初始传参
        sender 即self.sender()"""
        # 随机一个id，并添加入字典
        id_random = create_random_string(8)
        self.command_dict[id_random] = {}  # 创建对应的空键值对

        # 计算当前索引
        if index is None:
            if self.sender():
                index = self.get_widget_index(self.sender())
                if index is None:
                    index = self.listWidget_command_area.count()
            else:
                index = self.listWidget_command_area.count()

        # 如果传入args为空，则写入默认字典
        if not args_dict:
            args_dict = default_args_dict.copy()

        # 在当前索引后插入新的控件组
        child_widget = WidgetCommandControl()
        child_widget.load_command_args(args_dict)
        child_widget.setProperty('id', id_random)  # 设置控件组的唯一id

        list_widget_item = QListWidgetItem()
        list_widget_item.setData(1, id_random)  # 设置行项目相同的id
        resize = QSize(self.sizeHint().width(), 100)
        list_widget_item.setSizeHint(resize)
        list_widget_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)  # 启用列表项的拖放支持

        self.listWidget_command_area.insertItem(index + 1, list_widget_item)
        self.listWidget_command_area.setItemWidget(list_widget_item, child_widget)
        # 更新 widget 映射缓存
        self._widget_for_id[id_random] = child_widget

        # 设置行项目的边框
        self.listWidget_command_area.setStyleSheet("QListWidget::item { border: 1px solid grey; }")

        # 内部控件连接槽函数
        child_widget.toolButton_add_command.clicked.connect(self.insert_command_widget)
        child_widget.toolButton_copy_command.clicked.connect(self.copy_command_widget)
        child_widget.toolButton_delete_command.clicked.connect(self.delete_command_widget)
        child_widget.signal_send_args.connect(self.get_args_signal)
        child_widget.get_command_signal(args_dict)  # 手工执行一次，防止添加时不更新
        # 刷新序号
        self._update_sequence_numbers()

    def copy_command_widget(self):
        """复制指令行控件"""
        # 提取复制项的参数设置
        parent = self.sender().parentWidget()
        id_widget = parent.property('id')
        args_dict = self.command_dict[id_widget]

        # 插入复制的行
        self.insert_command_widget(args_dict=args_dict)

    def delete_command_widget(self):
        """删除指令行控件"""
        # 如果删除的是最后一个控件组，则先新增一个空白的再删除
        if self.listWidget_command_area.count() == 1:
            self.insert_command_widget()

        # 获取行项目对象
        index = self.get_widget_index(self.sender())  # 获取索引
        list_item = self.listWidget_command_area.item(index)  # 获取行项目对象
        list_widget = self.listWidget_command_area.itemWidget(list_item)  # 获取控件对象
        id_widget = list_widget.property('id')

        # 删除
        self.command_dict.pop(id_widget)
        self._widget_for_id.pop(id_widget, None)
        self.listWidget_command_area.takeItem(index)

        # 重新检查参数规范
        self.check_command_all_right()

        # 保存一遍配置
        self.save_command_setting()
        # 刷新序号
        self._update_sequence_numbers()

    def command_item_moved(self):
        """移动行项目后的处理"""
        error_index = None
        error_id = None
        for index in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(index)
            item_widget = self.listWidget_command_area.itemWidget(item)
            try:
                item_widget.property("id")
            except AttributeError:
                error_index = index
                error_id = item.data(1)
                break

        if error_index:
            # 删除错误行项目
            error_item = self.listWidget_command_area.takeItem(error_index)
            del error_item
            # 添加新的行项目
            args_dict = self.command_dict[error_id]
            if error_index == 1:  # 第1行出错时，插入行项目的index需要为0
                error_index = 0
            self.insert_command_widget(index=error_index - 1, args_dict=args_dict)
            # 删除错误id
            self.command_dict.pop(error_id)
        # 重建 widget 映射（拖拽后 widget 可能被重新创建）
        self._rebuild_widget_map()
        # 刷新序号
        self._update_sequence_numbers()

    def get_widget_index(self, sender):
        """获取当前操作的控件在控件区中的索引号
        传参：
        sender 即self.sender()"""
        parent = sender.parentWidget()
        for index in range(self.listWidget_command_area.count()):
            item = self.listWidget_command_area.item(index)
            item_widget = self.listWidget_command_area.itemWidget(item)

            if item_widget is parent:
                return index

    """
    配置文件相关函数
    """

    def load_global_setting(self):
        """加载全局设置"""
        # 加载设置项
        config_list = function_config.get_config_items()
        if not config_list:
            config_list = ['默认']
            function_config.add_config('默认')
        self.ui.comboBox_select_config.addItems(config_list)
        # 加载循环次数
        loop_time = function_config.get_config_loop_time()
        self.ui.spinBox_loop_time.setValue(loop_time)
        # 加载指令间隔
        wait_time = function_config.get_config_wait_time()
        self.ui.doubleSpinBox_global_wait_time.setValue(wait_time)

    def reset_runs_times(self):
        """重置已运行次数"""
        self.runs_times = 0

    def add_config(self):
        """新建配置文件"""
        config_name, _ = QInputDialog.getText(self, "新建配置文件", "名称:", text="默认")
        if config_name:
            checked_config = function_config.add_config(config_name)
            self.ui.comboBox_select_config.addItem(checked_config)
            self.ui.comboBox_select_config.setCurrentText(checked_config)

    def delete_config(self):
        """删除配置文件"""
        config_name = self.ui.comboBox_select_config.currentText()
        config_index = self.ui.comboBox_select_config.currentIndex()
        # 弹出确认对话框
        reply = QMessageBox.warning(self, "删除配置文件", f"是否删除【{config_name}】", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            function_config.delete_config(config_name)
            self.ui.comboBox_select_config.setCurrentIndex(0)
            self.ui.comboBox_select_config.removeItem(config_index)

        if self.ui.comboBox_select_config.count() == 0:
            self.add_config()

    def save_command_setting(self):
        """保存配置文件的设置项"""
        config = self.ui.comboBox_select_config.currentText()
        command_data_dict = {}  # 结构：{id:{args_dict字典}, ...}

        total_command_number = self.listWidget_command_area.count()
        for i in range(total_command_number):
            item = self.listWidget_command_area.item(i)
            widget = self.listWidget_command_area.itemWidget(item)
            try:
                id_widget = widget.property('id')  # 获取控件组id
            except AttributeError:
                id_widget = item.data(1)
            args_dict = self.command_dict[id_widget]  # 根据id获取args字典
            if id_widget not in command_data_dict:
                command_data_dict[id_widget] = args_dict

        command_list = list(command_data_dict.values())
        function_config.save_command_config(config, command_list)

    """
    键鼠录制相关函数
    """

    def start_listener(self):
        """开始监听"""
        reply = QMessageBox.warning(self, "监听器", f"是否开始录制键鼠操作", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.dialog = DialogListener()
            self.dialog.signal_send_listener.connect(self.get_listener_data)
            self.dialog.show()

    def get_listener_data(self, listener_list):
        """接收录制操作的数据，保存配置文件后重新读取更新ui"""
        config = self.ui.comboBox_select_config.currentText()
        function_config.save_command_config(config, listener_list)
        self.load_config_command()

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self._hotkey_listener.is_alive():
            self._hotkey_listener.stop()
        self.thread_run_command.abort()
        self.thread_run_command.quit()
        self.thread_run_command.wait(1000)
        event.accept()


def main():
    app = QApplication()
    app.setStyle('Fusion')
    show_ui = Main()
    show_ui.setWindowIcon(QIcon(icon_main))
    show_ui.show()
    app.exec()


if __name__ == "__main__":
    main()
