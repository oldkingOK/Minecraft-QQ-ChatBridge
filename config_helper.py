import json
from enums.constants import CONFIG_PATH

config_json: dict
"""存储config.json的数据，避免多次io操作"""

inited = False
def _init():
    global inited, config_json
    inited = True
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)

def _check_init():
    global inited
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

def get_json() -> dict:
    _check_init()
    return config_json

def get_settings() -> dict:
    _check_init()
    return config_json["Settings"]

def get_groups() -> dict:
    _check_init()
    return config_json["Groups"]

def get_servers() -> dict:
    _check_init()
    return config_json["Servers"]

def get_accounts() -> dict:
    _check_init()
    return config_json["Accounts"]

if not inited: _init()