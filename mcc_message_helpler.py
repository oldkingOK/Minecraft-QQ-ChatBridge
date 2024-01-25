from mcc_client_helper import send_msg

GROUP_SERVER_DICT = {}
"""群号-服务器名列表，用于发送消息到同组其他服务器"""

def init(group_server_dict: dict):
    """
    用来向mcc发送消息
    
    初始化mcc_message_helper

    group_server_dict   <群号,服务器名列表>
    """
    global GROUP_SERVER_DICT
    GROUP_SERVER_DICT = group_server_dict

def send_msg_to_other_mccs(server_name: str, msg: str):
    """
    发送消息到同组其他服务器
    """
    # 获取其他服务器 并发送消息
    global GROUP_SERVER_DICT
    for server_list in list(GROUP_SERVER_DICT.values()):
        if server_name not in server_list: continue
        for server in server_list:
            if server == server_name: continue
            send_msg(server, f"/me {msg}")
            
            
    