"""
WebSocket Server工具

文档：
https://github.com/Pithikos/python-websocket-server
"""
from typing import Callable
import websocket_server
import ok_logger
import logging

class FriendlyWsServer:
    def __init__(self, host: str, port: int) -> None:
        ws_server = websocket_server.WebsocketServer(host, port, logging.WARNING)
        ws_server.set_fn_new_client(self.new_client)
        ws_server.set_fn_client_left(self.client_left)
        ws_server.set_fn_message_received(self.on_message)
        
        self.ws_server = ws_server
        self.listeners: list[Callable[[str], None]] = []
        pass
    
    def start(self):
        "开始Websocket Server服务"
        self.ws_server.run_forever(threaded=True)

    def stop(self):
        "关闭WebSocket Server服务"
        self.ws_server.shutdown_abruptly()

    def new_client(self, client, server):
        ok_logger.get_logger().info("WebSocket 客户端 {0} 连接到了本程序".format(client["address"]))

    def client_left(self, client, server):
        if client is None: return
        ok_logger.get_logger().info("WebSocket 客户端 {0} 断开了".format(client["address"]))

    def add_listener(self, msg_hander: Callable[[str], None]):
        self.listeners.append(msg_hander)

    def on_message(self, client, server, message):
        for msg_hander in self.listeners:
            msg_hander(message)