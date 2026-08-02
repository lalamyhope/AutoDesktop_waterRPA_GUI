"""转换命令控件名（中英转换），获取命令对应函数"""
import functools
import os

from PySide6.QtWidgets import *

from module import function_config
from module.constant_default import *
from module.function_pyautogui import *

import ui.widget_command.command_click_image_position as command_click_image_position
import ui.widget_command.command_key_in_hotkey as command_key_in_hotkey
import ui.widget_command.command_key_in_keys as command_key_in_keys
import ui.widget_command.command_key_press as command_key_press
import ui.widget_command.command_key_release as command_key_release
import ui.widget_command.command_mouse_click as command_mouse_click
import ui.widget_command.command_mouse_move_relative as command_mouse_move_relative
import ui.widget_command.command_mouse_move_absolute as command_mouse_move_absolute
import ui.widget_command.command_mouse_press as command_mouse_press
import ui.widget_command.command_mouse_release as command_mouse_release
import ui.widget_command.command_mouse_scroll as command_mouse_scroll
import ui.widget_command.command_move_to_image_position as command_move_to_image_position
import ui.widget_command.command_paste_text as command_paste_text
import ui.widget_command.command_screenshot_fullscreen as command_screenshot_fullscreen
import ui.widget_command.command_wait_time_random as command_wait_time_random
import ui.widget_command.command_wait_time as command_wait_time


class CommandConvert:
    # 命令类型 → 控件模块 映射
    _WIDGET_MODULE_MAP = {
        'command_click_image_position': command_click_image_position,
        'command_key_in_hotkey': command_key_in_hotkey,
        'command_key_in_keys': command_key_in_keys,
        'command_key_press': command_key_press,
        'command_key_release': command_key_release,
        'command_mouse_click': command_mouse_click,
        'command_mouse_move_relative': command_mouse_move_relative,
        'command_mouse_move_absolute': command_mouse_move_absolute,
        'command_mouse_press': command_mouse_press,
        'command_mouse_release': command_mouse_release,
        'command_mouse_scroll': command_mouse_scroll,
        'command_move_to_image_position': command_move_to_image_position,
        'command_paste_text': command_paste_text,
        'command_screenshot_fullscreen': command_screenshot_fullscreen,
        'command_wait_time_random': command_wait_time_random,
        'command_wait_time': command_wait_time,
    }

    def __init__(self, command_type: str = None):
        self.command_type_en = command_type

        if command_type and command_type in command_chs_to_en_dict:
            self.command_type_en = command_chs_to_en_dict[command_type]

    def get_command_type(self):
        """获取对应的指令类型名（英文）"""
        return self.command_type_en

    def get_widget_object(self):
        """获取对应的控件对象，不支持传入参数设置"""
        if self.command_type_en and self.command_type_en in self._WIDGET_MODULE_MAP:
            module = self._WIDGET_MODULE_MAP[self.command_type_en]
            command_class_name = self.convert_command_class(self.command_type_en)
            command_widget_object = getattr(module, command_class_name)
        else:
            command_widget_object = None

        return command_widget_object

    def show_widget_object(self):
        command_widget_object = self.get_widget_object()
        app = QApplication()
        widget = command_widget_object()
        widget.show()
        app.exec()

    def get_function_object(self, args_dict: dict):
        """获取控件对象对应的命令函数，需要传入参数设置"""
        convert_arg = {'左键': 'left', '右键': 'right', '中键': 'middle'}

        wait_time = args_dict['wait_time']
        wait_time_min = args_dict['wait_time_min']
        wait_time_max = args_dict['wait_time_max']
        button = convert_arg[args_dict['button']]
        clicks = args_dict['clicks']
        interval = args_dict['interval']
        key = args_dict['key']
        keys = args_dict['keys']
        hotkey = args_dict['hotkey']
        presses = args_dict['presses']
        message = args_dict['message']
        use_clipboard = args_dict.get('use_clipboard', True)
        scroll_direction = args_dict['scroll_direction']
        scroll_distance = args_dict['scroll_distance']
        move_direction = args_dict['move_direction']
        move_distance = args_dict['move_distance']
        duration = args_dict['duration']
        screenshot_image_path = args_dict['screenshot_image_path']
        # 解析相对路径为绝对路径（基于项目根，不依赖 cwd）
        if screenshot_image_path and not os.path.isabs(screenshot_image_path):
            screenshot_image_path = os.path.normpath(
                os.path.join(function_config.get_project_root(), screenshot_image_path))
        mode_find_image = args_dict['mode_find_image']
        confidence = args_dict.get('confidence', 0.9)
        x = args_dict['x']
        y = args_dict['y']
        other = args_dict['other']

        scroll = scroll_distance if scroll_direction == '向上' else -scroll_distance
        timeout = function_config.get_config_find_image_timeout()

        # 命令类型 → 函数工厂 映射
        function_factory = {
            'command_mouse_move_relative': lambda: functools.partial(
                PyautoguiMouse.move_mouse_relative, duration, move_direction, move_distance),
            'command_mouse_move_absolute': lambda: functools.partial(
                PyautoguiMouse.move_mouse_absolute, duration, x, y),
            'command_mouse_click': lambda: functools.partial(
                PyautoguiMouse.mouse_click, button, clicks, interval, x if x > 0 else None, y if y > 0 else None),
            'command_mouse_press': lambda: functools.partial(
                PyautoguiMouse.mouse_down, button, x if x > 0 else None, y if y > 0 else None),
            'command_mouse_release': lambda: functools.partial(
                PyautoguiMouse.mouse_up, button, x if x > 0 else None, y if y > 0 else None),
            'command_mouse_scroll': lambda: functools.partial(
                PyautoguiMouse.mouse_scroll, scroll),
            'command_key_in_keys': lambda: functools.partial(
                PyautoguiKeyboard.press_keys, keys, presses, interval),
            'command_paste_text': lambda: functools.partial(
                PyautoguiKeyboard.press_text, message, presses, interval, use_clipboard),
            'command_key_in_hotkey': lambda: functools.partial(
                PyautoguiKeyboard.press_hotkey, hotkey),
            'command_key_press': lambda: functools.partial(
                PyautoguiKeyboard.press_down_key, key),
            'command_key_release': lambda: functools.partial(
                PyautoguiKeyboard.press_up_key, key),
            'command_screenshot_fullscreen': lambda: functools.partial(
                PyautoguiImage.screenshot_fullscreen, screenshot_image_path),
            'command_move_to_image_position': lambda: functools.partial(
                PyautoguiImage.move_to_pic_position, screenshot_image_path, duration,
                mode_find_image, timeout, confidence),
            'command_click_image_position': lambda: functools.partial(
                PyautoguiImage.click_pic_position, screenshot_image_path, duration,
                mode_find_image, button, clicks, interval, timeout, confidence),
            'command_wait_time': lambda: functools.partial(
                PyautoguiCustom.wait_time, wait_time),
            'command_wait_time_random': lambda: functools.partial(
                PyautoguiCustom.wait_time_random, wait_time_min, wait_time_max),
        }

        factory = function_factory.get(self.command_type_en)
        function_object = factory() if factory else None

        return function_object

    @staticmethod
    def convert_command_class(text_split):
        """将_间隔格式的文本转换为驼峰格式"""
        while '_' in text_split:
            index = text_split.find('_')
            text_split = text_split.replace('_', '', 1)
            text_split = text_split[:index] + text_split[index].upper() + text_split[index + 1:]

        text_split = text_split[0].upper() + text_split[1:]

        return text_split
