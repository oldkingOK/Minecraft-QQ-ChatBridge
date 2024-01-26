import json
import toml
from os import mkdir, path
from dict_util import replace_values_recursive

CONFIG_PATH: str

def init(config_path: str, mcc_ini_template: str, tmp_folder: str):
    global CONFIG_PATH
    CONFIG_PATH = config_path
    _load_config(mcc_ini_template, tmp_folder)

def _load_config(mcc_ini_template: str, tmp_folder: str):
    """
    config_path 用于修改mcc配置的json配置文件
    mcc_ini_template 第一次运行mcc时生成的文件
    """
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)
        
    with open(mcc_ini_template, 'r') as mcc_config_template_file:
        mcc_config_template_json = toml.load(mcc_config_template_file)

    servers = config_json["Servers"]
    for server_name in servers:
        server = servers[server_name]
        if not server["Enabled"]: continue

        account_name = server["Account"]
        # 替换
        replace_values_recursive(mcc_config_template_json["Main"]["General"],
                                  config_json["Accounts"][account_name])
        mcc_config_template_json["Main"]["General"]["Server"]["Host"] = config_json["Servers"][server_name]["Host"]
        replace_values_recursive(mcc_config_template_json, config_json["Servers"][server_name]["Config"])

        # 输出
        if not path.exists(tmp_folder): mkdir(tmp_folder)
        with open(f"{tmp_folder}/{server_name}.ini", "w") as output_file:
            toml.dump(mcc_config_template_json, output_file)

def get_server_list(ignore_disabled: bool = True) -> list:
    """
    获取配置文件中服务器名列表
    
    ignore_disabled 是否排除未启用的服务器
    """
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    result = []
    servers = config_json["Servers"]
    for server_name in servers:
        server = servers[server_name]
        if ignore_disabled and server["Enabled"]: result.append(server_name)

    return result

def _get_server_config_dict(ignore_disabled: bool = True) -> dict:
    """
    <server_name, config_dict>
    
    ignore_disabled 是否排除未启用的服务器

    其中config_dict详细请看config.json的 Servers.server_name.Config
    """
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    result = {}
    servers = config_json["Servers"]
    for server_name in servers:
        server = servers[server_name]
        if ignore_disabled and not server["Enabled"]: continue
        result[server_name] = server["Config"]

    return result

def get_group_servers_dict(ignore_disabled: bool = True) -> dict[str, list[str]]:
    """
    <群号, 服务器列表> 的dict
    
    ignore_disabled 是否排除未启用的服务器
    """
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    groups = config_json["Groups"]
    # 如果要排除，就遍历
    if ignore_disabled:
        new_groups = {}
        for group_id, server_list in groups.items():
            new_list = [server_name for server_name in server_list if is_server_enabled(server_name)]
            new_groups[group_id] = new_list

        groups = new_groups

    return groups

def get_global_setting(key: str) -> any:
    """获取全局设置，即根节点“Settings”中内容"""
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)
    return config_json["Settings"][key]

def get_account(server_name: str) -> str:
    with open(CONFIG_PATH, 'r') as config_json_file:
        config_json = json.load(config_json_file)
    account_name = config_json["Servers"][server_name]["Account"]
    return config_json["Accounts"][account_name]["Account"]["Login"]

def get_server_config(server_name: str, ignore_disabled=True) -> dict:
    return _get_server_config_dict(ignore_disabled)[server_name]

def is_server_enabled(server_name: str):
    return server_name in get_server_list(ignore_disabled=True)

def get_group_sever_list(group_id: set, ignore_disabled: bool = True) -> list[str]:
    return get_group_servers_dict(ignore_disabled)[group_id]

# def main():
#     load_config("config.json", "mcc_config_template.ini", "./tmp")

# main()