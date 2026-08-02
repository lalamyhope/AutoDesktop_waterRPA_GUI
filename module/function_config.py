"""配置文件相关方法（JSON 格式）
全局设置: global.json
命令配置: configs/{配置名}/widget_command.json"""

import json
import os

import send2trash

from module.constant_default import *
from module.function_general import *

_current_config_name = ''
_PROJECT_ROOT = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_project_root():
    return _PROJECT_ROOT


def set_current_config(name: str):
    global _current_config_name
    _current_config_name = name


def get_current_config_image_dir():
    name = _current_config_name or '默认'
    path = os.path.join(_PROJECT_ROOT, configs_folder, name)
    os.makedirs(path, exist_ok=True)
    return path


def _read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---- INI→JSON 迁移 ----

def _try_migrate_global():
    """将旧的 global_setting.ini 迁移为 global.json"""
    json_path = os.path.join(_PROJECT_ROOT, global_config)
    if os.path.exists(json_path):
        return
    # 尝试旧文件名
    old_path = os.path.join(_PROJECT_ROOT, 'global.ini')
    for legacy in [old_path, os.path.join(_PROJECT_ROOT, 'global_setting.ini')]:
        if os.path.exists(legacy):
            import configparser
            cp = configparser.ConfigParser(interpolation=None)
            cp.read(legacy, encoding='utf-8')
            data = {k: cp.get('DEFAULT', k) for k in cp.options('DEFAULT')}
            # 转换类型
            for k in ('loop_time', 'find_image_timeout'):
                if k in data:
                    data[k] = int(data[k])
            if 'global_wait_time' in data:
                data['global_wait_time'] = float(data['global_wait_time'])
            _write_json(json_path, data)
            return


def _try_migrate_config(config_name: str):
    """将旧的 widget_command.ini 迁移为 widget_command.json"""
    config_dir = os.path.join(_PROJECT_ROOT, configs_folder, config_name)
    json_path = os.path.join(config_dir, command_config)
    if os.path.exists(json_path):
        return
    old_path = os.path.join(config_dir, 'widget_command.ini')
    if os.path.exists(old_path):
        import configparser
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(old_path, encoding='utf-8')
        command_list = []
        for section in cp.sections():
            args_dict = {}
            for key in cp.options(section):
                value = cp.get(section, key)
                try:
                    import ast
                    conv = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    conv = value
                args_dict[key] = conv
            command_list.append(args_dict)
        _write_json(json_path, command_list)


# ---- 全局设置 ----

def _default_global():
    return {'loop_time': 1, 'global_wait_time': 0.5, 'find_image_timeout': 60}


def _read_global():
    path = os.path.join(_PROJECT_ROOT, global_config)
    _try_migrate_global()
    if not os.path.exists(path):
        data = _default_global()
        _write_json(path, data)
        return data
    return _read_json(path)


def _write_global(data):
    _write_json(os.path.join(_PROJECT_ROOT, global_config), data)


def check_default_config():
    configs_dir = os.path.join(_PROJECT_ROOT, configs_folder)
    screenshot_dir = os.path.join(_PROJECT_ROOT, screenshot_folder)
    os.makedirs(configs_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)
    _read_global()  # 确保 global.json 存在
    config_list = [i for i in os.listdir(configs_dir) if os.path.isdir(os.path.join(configs_dir, i))]
    if not config_list:
        add_config('默认')
    else:
        for config_name in config_list:
            config_path = os.path.join(configs_dir, config_name, command_config)
            if not os.path.exists(config_path):
                save_command_config(config_name)


def get_config_find_image_timeout():
    return _read_global().get('find_image_timeout', 60)


def update_config_find_image_timeout(timeout: int):
    data = _read_global()
    data['find_image_timeout'] = timeout
    _write_global(data)


def update_config_loop_time(loop_time: int):
    data = _read_global()
    data['loop_time'] = loop_time
    _write_global(data)


def get_config_loop_time():
    return _read_global().get('loop_time', 1)


def update_config_wait_time(wait_time: float):
    data = _read_global()
    data['global_wait_time'] = wait_time
    _write_global(data)


def get_config_wait_time():
    return _read_global().get('global_wait_time', 0.5)


def get_config_items():
    configs_dir = os.path.join(_PROJECT_ROOT, configs_folder)
    if not os.path.exists(configs_dir):
        return []
    return [i for i in os.listdir(configs_dir) if os.path.isdir(os.path.join(configs_dir, i))]


def add_config(config_name: str):
    config_list = get_config_items()
    checked_config = check_filename_feasible(config_name, replace=True)
    if checked_config in config_list:
        random_string = ''.join(random.choices(string.ascii_lowercase, k=6))
        checked_config = f"{checked_config}_{random_string}"
    config_path = os.path.join(_PROJECT_ROOT, configs_folder, checked_config)
    os.makedirs(config_path)
    save_command_config(checked_config)
    return checked_config


def delete_config(config_name: str):
    config_path = os.path.join(_PROJECT_ROOT, configs_folder, config_name)
    if os.path.exists(config_path):
        send2trash.send2trash(config_path)


def get_command_list(config_name: str):
    config_path = os.path.join(_PROJECT_ROOT, configs_folder, config_name, command_config)
    _try_migrate_config(config_name)
    if not os.path.exists(config_path):
        return [default_args_dict.copy()]
    return _read_json(config_path)


def save_command_config(config_name: str, command_list: list = None):
    config_dir = os.path.join(_PROJECT_ROOT, configs_folder, config_name)
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, command_config)
    if command_list is None:
        command_list = [default_args_dict.copy()]
    _write_json(config_path, command_list)