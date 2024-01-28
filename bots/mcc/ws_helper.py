"""
ws_helper
只管连接和收发消息
"""

from typing import Callable
from bots.classes import Server
from queue import Queue
import json
import ok_logger
import threading
import bots.mcc.ws_cmd_helper as mcc_cmd_helper
import lib.websocket_client_util as websocket_client_util

DEATH_MESSAGE_DICT: dict[str,str] = {}
"""存放死亡消息的dict，用于翻译死亡消息"""

def start_ws(server: Server, msg_handler: Callable[[str], None]):
    """
    与mcc连接，验证并接受消息

    服务器名

    消息接受回调函数：fun(msg:str) -> None
    """

    threading.Thread(target=_start, args=[
        server, msg_handler
    ]).start()

def _start(server: Server, msg_handler):
    """
    连接并验证
    server_name 服务器名

    address "ws://127.0.0.1:8043"

    password "12345678"

    见 https://mccteam.github.io/guide/websocket/
    """
    connection = websocket_client_util.ClientConnection(
        server.name, f"ws://{server.ip}:{str(server.port)}"
    )
    connection.start()
    server.connection = connection

    # 发送 Request
    auth_request = mcc_cmd_helper.Authenticate(
        lambda msg: ok_logger.get_logger().info(
            f"验证服务器 {server.name} 成功！" 
                if json.loads(json.loads(msg)["data"])["success"] 
                else f"验证服务器 {server.name} 失败..."
            ),
        server.passwd
    )
    
    connection.request(
        auth_request.request_json,
        auth_request.test,
        auth_request.on_response
    )

    # 开始接收消息
    # start_recv(server, msg_handler)
    connection.add_listener(test=TRUE, on_message=msg_handler, one_time=False)

def get_player_list(server: Server, queue: Queue[tuple[str, list[str]]]) -> None:
    """
    获取该服务器玩家列表（已排除bot本身）

    参数：
    - server (bots.classes.Server)
    - queue (Queue[tuple[str, list[str]]]) 列表队列，用于存储已经获取到的玩家列表
        - tuple (server_name: str, player_list: list[str])
    
    返回值：
    - player_list (list[str])
    """

    """
    接收到的数据示例：
    {"event": "OnWsCommandResponse",
      "data": "{\"success\": true,
        \"requestId\": \"614569\",
        \"command\": \"GetOnlinePlayers\",
        \"result\": [\"QQbot\"]}"
    }
    """
    def on_msg(msg):
        player_list:list[str] = json.loads(json.loads(msg)["data"])["result"]
        player_list.remove(server.account_name)
        queue.put((server.name, player_list))

    # lambda msg: queue.put((server.name, json.loads(json.loads(msg)["data"])["result"].remove(server.account_name)))
    player_list_request = mcc_cmd_helper.GetOnlinePlayers(
        on_msg
    )
    server.connection.request(
        player_list_request.request_json,
        player_list_request.test,
        player_list_request.on_response
    )
    pass

def TRUE(*args):
    return True