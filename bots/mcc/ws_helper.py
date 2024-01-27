"""
ws_helper
只管连接和收发消息
"""
from websockets.sync.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosedError

from typing import Callable
from bots.classes import Server
from enums.constants import RETRY_TIME
import json
import time
import ok_logger
import traceback
import threading
import bots.mcc.config_helper as mcc_config_helper

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
    websocket = try_connect(server)

    data = {
        "command": "Authenticate",
        "requestId": "0",
        "parameters": [server.passwd]
    }
    """
    {"event": "OnWsCommandResponse",
      "data": "{\"success\": true, \"requestId\": \"0\", \"command\": \"Authenticate\",
        \"result\": \"Successfully authenticated!\"}"}
    """
    websocket.send(json.dumps(data))
    recv_message_json = json.loads(websocket.recv())
    if not json.loads(recv_message_json["data"])["success"]: 
        ok_logger.get_logger().info(f"连接 {server.name} 失败")
        return
        
    ok_logger.get_logger().info(f"连接 {server.name} 成功！")
    # 开始接收消息
    start_recv(server, websocket, msg_handler)

def start_recv(server: Server, websocket: ClientConnection, msg_handler: Callable[[str], None]):
    """
    开始循环接受mcc websocket发来的消息


    消息接受回调函数：fun(msg:str, message_type: MessageType) -> None
    """
    while True:
        try:
            message = websocket.recv()
        except BaseException as exception:
            ok_logger.get_logger().info(f"服务器 <{server.name}> 尝试接收ws消息时捕获异常: {exception},  {RETRY_TIME} 秒后重试")
            # 如果不是连接断开，就打印堆栈
            if type(exception) is not ConnectionClosedError:
                ok_logger.get_logger().debug(traceback.format_exc())
            time.sleep(RETRY_TIME)
            ok_logger.get_logger().info(f"服务器 <{server.name}> 正在尝试重连...")
            # 尝试重连
            websocket = try_connect(server)
            if websocket is None: return
            continue
        
        msg_handler(message)

def try_connect(server: Server) -> ClientConnection | None:
    """
    尝试连接WebSocket server，直到成功
    如果返回None，就是程序终止
    """
    success = False
    websocket: ClientConnection
    address = f"ws://{server.ip}:{str(server.port)}"
    while not success:
        if not _can_continue(server):
            ok_logger.get_logger().info(f"服务器 {server.name} 已收到终止信号，中断连接")
            return None
        try:
            websocket = connect(address)
            success = True
        except BaseException as exception:
            ok_logger.get_logger().info(f"服务器 <{server.name}> 尝试连接时捕获异常: {exception},  {RETRY_TIME} 秒后重试")
            time.sleep(RETRY_TIME)
            ok_logger.get_logger().info(f"服务器 <{server.name}> 正在重连...")
            continue
    return websocket

def _can_continue(server: Server):
    """线程是否能够继续"""
    return server.running