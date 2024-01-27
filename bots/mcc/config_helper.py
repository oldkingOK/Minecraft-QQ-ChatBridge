import config_helper as config_helper
import toml
from os import mkdir, path
from utils.dict_util import replace_values_recursive
from enums.settings import TMP_FOLDER, MCC_INI_TEMPLATE
from bots.classes import Account, Server

inited = False
"""该模块是否已初始化"""
def init():
    global inited
    if inited: return
    _load_server_to_ini()
    inited = True

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

def _load_server_to_ini(ignore_disabled = True):
    """
    ignore_disabled 是否忽略禁用的文件夹
    """
    with open(MCC_INI_TEMPLATE, 'r') as mcc_config_template_file:
        mcc_config_template_json = toml.load(mcc_config_template_file)

    servers = config_helper.get_servers()
    for server_name in servers:
        server = servers[server_name]
        if ignore_disabled and not server["Enabled"]: continue

        account_name = server["Account"]
        # 替换
        replace_values_recursive(mcc_config_template_json["Main"]["General"],
                                  config_helper.get_accounts()[account_name])
        mcc_config_template_json["Main"]["General"]["Server"]["Host"] = server["Host"]
        replace_values_recursive(mcc_config_template_json, server["Config"])

        # 输出
        if not path.exists(TMP_FOLDER): mkdir(TMP_FOLDER)
        with open(f"{TMP_FOLDER}/{server_name}.ini", "w") as output_file:
            toml.dump(mcc_config_template_json, output_file)

def get_server(server_name: str) -> Server:
    server_dict = config_helper.get_servers()[server_name]
    return Server(server_name, server_dict, Account(config_helper.get_accounts()[server_dict["Account"]]).user_name)
