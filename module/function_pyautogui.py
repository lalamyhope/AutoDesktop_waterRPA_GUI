"""pyautogui的封装"""
import random
import time
from typing import Tuple, Union

import numpy
import pyautogui
import pyperclip
from PIL import Image
from pynput.keyboard import Controller as PynputKeyboard, Key as PynputKey

"""
参数默认设置
"""
_default_duration: float = 0.25  # 默认移动所需时间
_default_clicks: int = 1  # 默认点击次数
_default_interval: float = 0.1  # 默认每次点击间隔时间
_default_presses: int = 1  # 默认重复次数
_default_confidence = 0.9  # 默认寻图精度
_default_move_direction = '向左'  # 默认移动方向
_default_move_distance = 100  # 默认移动距离
_default_X = 1  # 默认x坐标轴
_default_Y = 1  # 默认y坐标轴
_max_x, _max_y = pyautogui.size()  # x,y坐标值的最大值限制（屏幕大小）


def image_read_from_chinese_path(image_file_name):
    # 将路径对应的图片转换为numpy图片对象（pyautogui库不支持中文名图片，需要通过numpy库中转）
    image_numpy_data = numpy.array(Image.open(image_file_name))

    return image_numpy_data


class PyautoguiMouse:
    """pyautogui的鼠标操作的简单封装

    内部变量说明：
    x 为x坐标轴
    y 为y坐标轴
    duration 为移动所需时间，0为瞬间移动
    button 为对应的鼠标按键，可设置为"left", "middle", right"
    clicks 为点击次数
    interval 为多次点击时的点击间隔时间
    tween 为移动鼠标时的速率函数，默认为线性速度移动"""

    @staticmethod
    def _get_mouse_position() -> Tuple[int, int]:
        """获取鼠标当前位置"""
        current_mouse_x, current_mouse_y = pyautogui.position()

        return current_mouse_x, current_mouse_y

    @staticmethod
    def move_mouse_to_position(x: int, y: int, duration: float = _default_duration):
        """移动鼠标至指定坐标轴
        duration 为移动所需时间，0为瞬间移动"""
        if x == 0 and y == 0:
            x, y = 1, 1
        pyautogui.moveTo(x, y, duration=duration)

        return x, y

    @staticmethod
    def drag_mouse_to_position(x: int, y: int, button: str = 'left', duration: float = _default_duration):
        """按下鼠标键，拖拽至指定坐标轴
        button 为指定键，可设置为"left", "middle", right"
        duration 为移动所需时间，0为瞬间移动"""
        if x == 0 and y == 0:
            x, y = 1, 1
        pyautogui.dragTo(x, y, button=button, duration=duration)

        return x, y

    @staticmethod
    def move_mouse_relative(duration: float = _default_duration, move_direction: str = _default_move_direction,
                            move_distance: int = _default_move_distance):
        """向指定方向移动鼠标"""
        x, y = pyautogui.position()
        if move_direction in ['向左', 'left']:
            x -= move_distance
        elif move_direction in ['向右', 'right']:
            x += move_distance
        elif move_direction in ['向上', 'up']:
            y -= move_distance
        elif move_direction in ['向下', 'down']:
            y += move_distance

        if x < 0:
            x = 1
        if x > _max_x:
            x = _max_x

        if y < 0:
            y = 1
        if y > _max_y:
            y = _max_x

        if x == 0 and y == 0:
            x, y = 1, 1
        pyautogui.moveTo(x, y, duration=duration)

        return x, y

    @staticmethod
    def move_mouse_absolute(duration: float = _default_duration, x: int = _default_X,
                            y: int = _default_Y):
        """移动鼠标至指定坐标轴"""
        if x == 0 and y == 0:
            x, y = 1, 1
        pyautogui.moveTo(x, y, duration=duration)

        return x, y

    @staticmethod
    def mouse_click(button: str = 'left', clicks: int = _default_clicks,
                    interval: float = _default_interval,
                    x: int = None, y: int = None):
        """点击鼠标
        button 为点击的按键，可设置为"left", "middle", right
        clicks 为点击次数
        interval 为点击间隔时间
        x, y 为可选的目标坐标，传入则先移动到该位置再点击"""
        if x is not None and y is not None:
            if x == 0 and y == 0:
                x, y = 1, 1
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)
        else:
            pyautogui.click(button=button, clicks=clicks, interval=interval)

        return button

    @staticmethod
    def mouse_down(button: str = 'left', x: int = None, y: int = None):
        """按下鼠标
        button 为点击的按键，可设置为"left", "middle", right
        x, y 为可选的目标坐标，传入则先移动到该位置再按下"""
        if x is not None and y is not None:
            if x == 0 and y == 0:
                x, y = 1, 1
            pyautogui.moveTo(x, y)
        pyautogui.mouseDown(button=button)

        return button

    @staticmethod
    def mouse_up(button: str = 'left', x: int = None, y: int = None):
        """释放鼠标
        button 为点击的按键，可设置为"left", "middle", right
        x, y 为可选的目标坐标，传入则先移动到该位置再释放"""
        if x is not None and y is not None:
            if x == 0 and y == 0:
                x, y = 1, 1
            pyautogui.moveTo(x, y)
        pyautogui.mouseUp(button=button)

        return button

    @staticmethod
    def mouse_scroll(distance: int):
        """滚动滚轮
        distance 为滚动格数，正数向上滚动，负数向下滚动"""
        pyautogui.scroll(clicks=distance)

        return distance


class PyautoguiKeyboard:
    """pyautogui的键盘操作的简单封装

    内部变量说明：
    massage 为输入的文本
    keys 为按下的键，有固定名称，传入多个str，不可传入list
    presses 为重复次数
    interval 为间隔时间"""

    @staticmethod
    def press_text(message: str, presses: int = _default_presses, interval: float = _default_interval,
                   use_clipboard: bool = False):
        """输入字符串（剪贴板 + Ctrl+V）
        use_clipboard=False → 复制上方文本到剪贴板再粘贴
        use_clipboard=True → 直接粘贴剪贴板现有内容"""
        for _ in range(presses):
            if not use_clipboard and message:
                pyperclip.copy(message)
            PyautoguiKeyboard.press_hotkey('ctrl+v')
            time.sleep(interval)

        return True

    @staticmethod
    def _pynput_key(key_str: str):
        """将 pyautogui 键名转为 pynput Key 对象"""
        key_str = key_str.strip().lower()
        _map = {
            'ctrl': PynputKey.ctrl, 'ctrlleft': PynputKey.ctrl_l, 'ctrlright': PynputKey.ctrl_r,
            'shift': PynputKey.shift, 'shiftleft': PynputKey.shift_l, 'shiftright': PynputKey.shift_r,
            'alt': PynputKey.alt, 'altleft': PynputKey.alt_l, 'altright': PynputKey.alt_r,
            'win': PynputKey.cmd, 'winleft': PynputKey.cmd_l, 'winright': PynputKey.cmd_r, 'cmd': PynputKey.cmd,
            'enter': PynputKey.enter, 'space': PynputKey.space, 'tab': PynputKey.tab,
            'esc': PynputKey.esc, 'escape': PynputKey.esc,
            'backspace': PynputKey.backspace, 'delete': PynputKey.delete, 'del': PynputKey.delete,
            'up': PynputKey.up, 'down': PynputKey.down, 'left': PynputKey.left, 'right': PynputKey.right,
            'home': PynputKey.home, 'end': PynputKey.end,
            'pageup': PynputKey.page_up, 'pagedown': PynputKey.page_down,
            'insert': PynputKey.insert, 'printscreen': PynputKey.print_screen,
            'capslock': PynputKey.caps_lock, 'numlock': PynputKey.num_lock, 'scrolllock': PynputKey.scroll_lock,
        }
        for i in range(1, 25):
            _map[f'f{i}'] = getattr(PynputKey, f'f{i}', None)
        if key_str in _map:
            return _map[key_str]
        if len(key_str) == 1:
            return key_str
        return None

    @staticmethod
    def press_keys(keys: Union[list, str], presses: int = _default_presses, interval: float = _default_interval):
        """敲击指定键（pynput 实现）"""
        if type(keys) is str:
            keys = keys.split(' ')
        kb = PynputKeyboard()
        for _ in range(presses):
            for k in keys:
                pk = PyautoguiKeyboard._pynput_key(k)
                if pk:
                    kb.press(pk)
                    kb.release(pk)
                    if interval:
                        time.sleep(interval)
        return True

    @staticmethod
    def press_down_key(key: str):
        """按下指定按键（不释放）"""
        pk = PyautoguiKeyboard._pynput_key(key)
        if pk:
            PynputKeyboard().press(pk)
        return True

    @staticmethod
    def press_up_key(key: str):
        """释放指定按键"""
        pk = PyautoguiKeyboard._pynput_key(key)
        if pk:
            PynputKeyboard().release(pk)
        return True

    @staticmethod
    def press_hotkey(hotkeys: Union[list, str]):
        """按下组合键（pynput 实现）
        hotkeys: list 或 'ctrl+c' / 'ctrl shift c' 格式"""
        if type(hotkeys) is str:
            import re
            hotkeys = re.split(r'[+ ]+', hotkeys.strip())
        if not hotkeys:
            return True

        kb = PynputKeyboard()
        resolved = [PyautoguiKeyboard._pynput_key(k) for k in hotkeys]
        resolved = [r for r in resolved if r is not None]
        time.sleep(0.02)
        for key in resolved:
            kb.press(key)
        for key in reversed(resolved):
            kb.release(key)

        return True


class PyautoguiImage:
    """pyautogui的图像操作的简单封装

    图像的操作调用了PyScreeze库
    参数说明：
    confidence 为定位精度，0~1，越大越精准"""

    @staticmethod
    def screenshot_fullscreen(pic_file: str = 'screenshot.png'):
        """截全屏并保存图片
        pic_file 可指定保存路径与名称"""
        pyautogui.screenshot(pic_file)

        return pic_file

    @staticmethod
    def screenshot_area(area: Union[tuple, list], pic_file: str = 'screenshot.png'):
        """指定区域截图并保存图片
        截取区域 area 参数为(左上角X坐标值, 左上角Y坐标值, 右下角X坐标值, 右下角X坐标值)
        pic_file 可指定保存路径与名称"""
        # 转换area参数至pyautogui的格式
        region = (area[0], area[1], area[2] + area[0], area[3] + area[1])
        pyautogui.screenshot(pic_file, region=region)

        return pic_file

    @staticmethod
    def _search_pic_first_position(pic_file: str,
                                   confidence: float = _default_confidence
                                   ) -> Tuple[Union[int, None], Union[int, None]]:
        """获得在屏幕上第一个找到的文件图片的中心点坐标，如果没有找到则返回None
        confidence 为查找精度"""
        pic_file_to_image = image_read_from_chinese_path(pic_file)  # 转换为image对象，以处理中文名图片
        position = pyautogui.locateCenterOnScreen(pic_file_to_image, confidence=confidence)

        if position:
            x, y = position.x, position.y
        else:
            x, y = None, None
        return x, y

    @staticmethod
    def _search_pic_all_position(pic_file: str, confidence: float = _default_confidence, timeout: int = 60) -> list:
        """获得在屏幕上所有找到的文件图片的中心点坐标，如果没有找到则返回None
        返回的坐标格式为[(x, y), (x_1, y_2)]
        confidence 为查找精度
        timeout 为超时时间"""
        pic_file_to_image = image_read_from_chinese_path(pic_file)  # 转换为image对象，以处理中文名图片
        time_start = time.time()
        all_center_position = []
        while True:
            result = pyautogui.locateAllOnScreen(pic_file_to_image, confidence=confidence)
            for pos in result:
                mid_x = pos.left + pos.width // 2
                mid_y = pos.top + pos.height // 2
                all_center_position.append((mid_x, mid_y))
            if all_center_position:
                break

            time_current = time.time()
            run_time = time_start - time_current
            if run_time >= timeout:
                break
            else:
                time.sleep(0.1)

        return all_center_position

    @staticmethod
    def move_to_pic_position(pic_file, duration=_default_duration, find_model: str = '第一个',
                             timeout: int = 60, confidence: float = _default_confidence) -> bool:
        """匹配图片并移动指令（两个函数的组合）
        pic_file 为图片文件路径
        duration 为移动所需时间，0为瞬间移动
        find_model 为查找模式，'第一个'或'全部'，用于点击
        timeout 超时时间
        confidence 匹配精度，0~1，默认0.9"""
        all_center_position = PyautoguiImage._search_pic_all_position(pic_file, confidence=confidence, timeout=timeout)
        if all_center_position:
            if find_model in ['第一个', 'first']:
                x, y = all_center_position[0]
                PyautoguiMouse.move_mouse_to_position(x=x, y=y, duration=duration)
            elif find_model in ['全部', 'all']:
                for i in range(len(all_center_position)):
                    x, y = all_center_position[i]
                    PyautoguiMouse.move_mouse_to_position(x=x, y=y, duration=duration)
            return True
        else:
            return False

    @staticmethod
    def click_pic_position(pic_file, duration=_default_duration,
                           find_model: str = '第一个', button: str = 'left', clicks: int = _default_clicks,
                           interval: float = _default_interval, timeout: int = 60,
                           confidence: float = _default_confidence) -> bool:
        """匹配图片并点击指令（两个函数的组合）
        button 为点击的按键，可设置为"left", "middle", right
        pic_file 为图片文件路径
        clicks 为点击次数
        interval 为点击间隔时间
        duration 为移动所需时间，0为瞬间移动
        find_model 为查找模式，'第一个匹配项'或'全部匹配项'，用于点击
        timeout 超时时间
        confidence 匹配精度，0~1，默认0.9"""
        all_center_position = PyautoguiImage._search_pic_all_position(pic_file, confidence=confidence, timeout=timeout)
        if all_center_position:
            if find_model in ['第一个', 'first']:
                x, y = all_center_position[0]
                PyautoguiMouse.move_mouse_to_position(x=x, y=y, duration=duration)
                PyautoguiMouse.mouse_click(button=button, clicks=clicks, interval=interval)
            elif find_model in ['全部', 'all']:
                for i in range(len(all_center_position)):
                    x, y = all_center_position[i]
                    PyautoguiMouse.move_mouse_to_position(x=x, y=y, duration=duration)
                    PyautoguiMouse.mouse_click(button=button, clicks=clicks, interval=interval)
            return True
        else:
            return False


class PyautoguiCustom:
    """pyautogui的其他操作的简单封装"""

    @staticmethod
    def wait_time(wait_time: float):
        """等待指定时间，传入float"""
        if wait_time == 0:
            wait_time = 0.01

        time.sleep(wait_time)

        return wait_time

    @staticmethod
    def wait_time_random(wait_time_min: int, wait_time_max: int):
        wait_time_random = round(random.uniform(wait_time_min, wait_time_max), 2)

        if wait_time_random == 0:
            wait_time_random = 0.01

        time.sleep(wait_time_random)

        return wait_time_random
