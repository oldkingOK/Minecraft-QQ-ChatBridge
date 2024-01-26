import requests
import mcc_config_helper

SEND_GROUP_MSG_API = "{0}/send_group_msg?group_id={1}&message="
ONEBOT_HTTP = ""
GROUP_ID = 0

def init(onebot_http: str):
    """
    初始化qq_helper

    group_server_dict   <群号,服务器名列表>

    onebot_http         onebot的http api，如http://127.0.0.1:5700
    """
    global ONEBOT_HTTP
    ONEBOT_HTTP = onebot_http

def send_to_qqgroup(server_name: str, msg: str):
    """参数：服务器名，消息"""
    group_id = mcc_config_helper.get_group_by_server(server_name)
    requests.get(SEND_GROUP_MSG_API.format(ONEBOT_HTTP, group_id) + msg)