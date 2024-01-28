"""
在这里启动websocket server获取qq消息
"""

from enums.settings import ONEBOT_WS_HOST, ONEBOT_WS_PORT
from typing import Callable
import bots.qq.ws_msg_util as qq_ws_msg_util
from lib.websocket_server_util import FriendlyWsServer

ws_server: FriendlyWsServer
"服务器对象"
_listeners: dict[str, Callable[[str], None]] = {}
"群号，监听器 dict"

inited = False
def init():
    global inited, ws_server
    if inited: return
    inited = True
    
    ws_server = FriendlyWsServer(ONEBOT_WS_HOST, ONEBOT_WS_PORT)
    ws_server.add_listener(_handle_msg)
    ws_server.start()

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

def on_end():
    ws_server.stop()

def _handle_msg(msg: str):
    "接收ws消息"
    global _listeners
    for qq_group_id, msg_handler in _listeners.items():
        # 判断群消息
        if not qq_ws_msg_util.is_qq_group_msg(qq_group_id, msg): continue
        # 执行
        msg_handler(msg)

def add_listener(qq_group_id: str, msg_handler: Callable[[str], None]):
    "添加监听器，指定群号"
    _check_init()

    global _listeners
    _listeners[qq_group_id] = msg_handler

def remove_listener(qq_group_id: str):
    "删除群号指定监听器"
    global _listeners
    _listeners.pop(qq_group_id)