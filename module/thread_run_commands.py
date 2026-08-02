import time

from PySide6.QtCore import *

from module import function_config


class ThreadRunCommands(QThread):
    signal_succeed = Signal(str)  # 发送执行成功的控件组id
    signal_failed = Signal(str)  # 发送执行失败的控件组id
    signal_finished = Signal(bool)  # 执行完成后，发送带结束状态的信号
    signal_error = Signal(str)  # 执行报错，发送错误信息
    signal_aborted = Signal()  # 用户手动中止信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_function_dict = {}
        self.command_run_modes = {}  # {item_id: 'every'|'once'}
        self._executed_ids = set()   # 本循环已执行的 once 命令
        self.find_image_timeout = function_config.get_config_find_image_timeout()
        self.wait_time = function_config.get_config_wait_time()
        self._abort_flag = False

    def set_command_function(self, command_function, run_modes=None):
        """设置参数和运行模式"""
        self.command_function_dict.clear()
        self.command_function_dict = command_function
        self.command_run_modes = run_modes or {}
        self._executed_ids.clear()
        self._abort_flag = False

    def reset_loop_state(self):
        """每个循环开始前重置状态（不清除 once 记录，外部调用）"""
        pass  # _executed_ids 只在 set_command_function 时清空，跨循环保留

    def abort(self):
        """外部调用：中止执行"""
        self._abort_flag = True

    def _sleep_interruptible(self, seconds: float):
        """可中断的 sleep，每 0.1 秒检查一次中止标志"""
        elapsed = 0.0
        while elapsed < seconds:
            if self._abort_flag:
                return False
            time.sleep(0.1)
            elapsed += 0.1
        return True

    def run(self):
        result_code = True
        for item_id, function in self.command_function_dict.items():
            if self._abort_flag:
                result_code = False
                self.signal_aborted.emit()
                break

            # 检查是否"仅首次执行"且已执行过
            run_mode = self.command_run_modes.get(item_id, 'every')
            if run_mode == 'once' and item_id in self._executed_ids:
                continue  # 跳过已执行的 once 命令

            try:
                if function:
                    result = function()
                    if result:
                        self._executed_ids.add(item_id)
                        self.signal_succeed.emit(item_id)
                    else:
                        self.signal_failed.emit(item_id)
                        result_code = False
                        break
            except Exception as e:
                self.signal_failed.emit(item_id)
                error_message = f'运行出错：{e}'
                self.signal_error.emit(error_message)
                result_code = False
                break

            # 指令间等待（可中断）
            if self.wait_time:
                if not self._sleep_interruptible(self.wait_time):
                    result_code = False
                    self.signal_aborted.emit()
                    break

        self.signal_finished.emit(result_code)
