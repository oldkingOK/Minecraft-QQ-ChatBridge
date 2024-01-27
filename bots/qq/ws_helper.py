"""
在这里启动websocket server获取qq消息
"""

from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedError
from bots.classes import Server
from enums import ONEBOT_WS_HOST, ONEBOT_WS_PORT, RETRY_TIME
from typing import Callable
import threading
import asyncio
import bots.qq.ws_msg_util as qq_ws_msg_util
import ok_logger

_listeners: dict[str, Callable[[str], None]] = {}
"群号，监听器 dict"

inited = False
def init():
    global inited
    if inited: return
    inited = True
    threading.Thread(target=asyncio.run, args=(_async_serve(),)).start()

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

async def _async_serve():
    async with serve(_handle_ws, ONEBOT_WS_HOST, ONEBOT_WS_PORT):
        await wait_until_stop()  # run until main thread stop
        
async def wait_until_stop():
    "运行直到主线程停止"
    while True:
        if not threading.main_thread().is_alive(): return
        await asyncio.sleep(RETRY_TIME)

async def _handle_ws(websocket: WebSocketServerProtocol):
    "接收ws消息"
    global _listeners
    try:
        async for msg in websocket:
            for qq_group_id, msg_handler in _listeners.items():
                # 判断群消息
                if not qq_ws_msg_util.is_qq_group_msg(qq_group_id, msg): continue
                # 执行
                msg_handler(msg)
    
    except ConnectionClosedError as exception:
        if not str(exception) == "no close frame received or sent":
            ok_logger.get_logger().info(f"尝试获取qq信息时捕获到异常：{exception}")

    except BaseException as exception:
        ok_logger.get_logger().info(f"尝试获取qq信息时捕获到异常：{exception}")

def add_listener(qq_group_id: str, msg_handler: Callable[[str], None]):
    "添加监听器，指定群号"
    _check_init()

    global _listeners
    _listeners[qq_group_id] = msg_handler