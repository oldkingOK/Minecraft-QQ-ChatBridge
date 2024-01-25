import json
import toml
from os import mkdir, path
from dict_util import replace_values_recursive

def load_config(config_json_name: str, mcc_ini_template: str, tmp_folder: str):
    """
    config_json_name 用于修改mcc配置的json配置文件
    mcc_ini_template 第一次运行mcc时生成的文件
    """
    with open(config_json_name, 'r') as config_json_file:
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

def get_server_dict(config_json_name: str) -> dict:
    with open(config_json_name, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    result = {}
    servers = config_json["Servers"]
    for server_name in servers:
        server = servers[server_name]
        result[server_name] = server["Enabled"]

    return result

def get_server_config_dict(config_json_name: str) -> dict:
    """
    <server_name, config_dict>
    
    自动排除未启用的服务器

    其中config_dict详细请看config.json的 Servers.server_name.Config
    """
    with open(config_json_name, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    result = {}
    servers = config_json["Servers"]
    for server_name in servers:
        server = servers[server_name]
        if not server["Enabled"]: continue
        result[server_name] = server["Config"]

    return result

def get_group_servers_dict(config_json_name: str) -> dict:
    """<群号, 服务器列表> 的dict"""
    with open(config_json_name, 'r') as config_json_file:
        config_json = json.load(config_json_file)

    return config_json["Groups"]

def get_global_setting(config_json_name: str, key: str) -> any:
    """获取全局设置，即根节点“Settings”中内容"""
    with open(config_json_name, 'r') as config_json_file:
        config_json = json.load(config_json_file)
    return config_json["Settings"][key]

# def main():
#     load_config("config.json", "mcc_config_template.ini", "./tmp")

# main()