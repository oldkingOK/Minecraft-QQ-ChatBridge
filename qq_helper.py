import requests
from text_util import remove_color_char

SEND_GROUP_MSG_API = "{0}/send_group_msg?group_id={1}&message="
ONEBOT_HTTP = ""
GROUP_SERVER_DICT = {}
"""群号-服务器名列表，用于从群聊发送到服务器"""
SERVER_GROUP_DICT = {}
"""服务器名-群号，用于从服务器发消息到群聊"""

GROUP_ID = 0

def init_qq_helper(group_server_dict: dict, onebot_http: str):
    """
    初始化qq_helper

    group_server_dict   <群号,服务器名列表>

    onebot_http         onebot的http api，如http://127.0.0.1:5700
    """
    global GROUP_SERVER_DICT, SERVER_GROUP_DICT, ONEBOT_HTTP
    GROUP_SERVER_DICT = group_server_dict
    ONEBOT_HTTP = onebot_http

    server_group_dict = {}
    for group_str, server_list in group_server_dict.items():
        for server_name in server_list:
            server_group_dict[server_name] = group_str

    SERVER_GROUP_DICT = server_group_dict

def send_to_qqgroup(server_name: str, msg: str):
    """参数：服务器名，消息"""
    
    global ONEBOT_HTTP, SEND_GROUP_MSG_API
    group_id = SERVER_GROUP_DICT[server_name]
    msg = f"[{server_name}] {remove_color_char(msg)}"
    requests.get(SEND_GROUP_MSG_API.format(ONEBOT_HTTP, group_id) + msg)