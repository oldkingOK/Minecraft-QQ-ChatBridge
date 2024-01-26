import mcc_config_helper
import mcc_client_helper
import mcc_config_helper
import ok_logger
import cli_helper
import threading
from mcc_ws_helper import MessageType, start_ws
from typing import Callable

started_list: list[str] = []

def is_start(group_id: str):
    global started_list
    return group_id in started_list

def start_mcc(group_id: str, sudo_passwd: str | None):
    global started_list
    started_list.append(group_id)

    # 启动mcc
    server_list = mcc_config_helper.get_group_sever_list(group_id)
    for server_name in server_list:
        if not mcc_config_helper.is_server_enabled(server_name): continue
        mcc_client_helper.start_mcc(server_name=server_name, sudo_passwd=sudo_passwd)

def stop_mcc(group_id: str):
    global started_list
    started_list.remove(group_id)
    server_list = mcc_config_helper.get_group_sever_list(group_id)
    mcc_client_helper.stop_mccs(server_list)

def connect_mcc_ws(group_id: str, msg_handler: Callable[[str, str, MessageType], None]):
    functions = []
    """异步执行的任务列表"""
    server_list = mcc_config_helper.get_group_sever_list(group_id, True)
    for server_name in server_list:
        config = mcc_config_helper.get_server_config(server_name)
        account_name = mcc_config_helper.get_account(server_name)
        ws_config = config["ChatBot"]["WebSocketBot"]
        ip = ws_config["Ip"]
        port = ws_config["Port"]
        passwd = ws_config["Password"]
        
        functions.append(lambda s=server_name, a=account_name, i=ip, p=port, pw=passwd, mh=msg_handler: start_ws(s, a, i, p, pw, mh))

    # 创建线程并运行
    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()

def get_group_servers_dict(ignore_disabled: bool = True) -> dict[str,str]:
    """
    获取群组消息
    dict<群组名, 服务器列表>
    """
    return mcc_config_helper.get_group_servers_dict(ignore_disabled)

def get_id_from_cli() -> str | None:
    """
    通过用户输入，获取群号
    非法输入，返回None
    """

    group_data_dict = get_group_servers_dict(ignore_disabled=True)
    ok_logger.get_logger().info("请选择群组序号：（已省略关闭的服务器）")
    # 打印组信息
    for index, (group_id, server_list) in enumerate(group_data_dict.items()):
        ok_logger.get_logger().info(f"{index}. {group_id} {server_list}")
    # 获取组序号
    group_id_list = list(group_data_dict.keys())
    index = cli_helper.select_from_numbers(range(len(group_id_list)))
    # 合法判断
    if index is None: return None
    return group_id_list[index]

def get_started_groups() -> list[str]:
    return started_list