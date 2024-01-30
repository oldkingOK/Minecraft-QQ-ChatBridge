"""
WebSocket Client工具

文档：
https://websocket-client.readthedocs.io/en/latest/
"""
import websocket

from typing import Callable
from enums.constants import RETRY_TIME
from queue import Queue
import ok_logger
import json
import threading
from utils.thread_util import TimerRunnable

# websocket.enableTrace(True, handler=ok_logger.get_logger().handlers[0])

class ClientConnection:
    "作为客户端的连接"
    def __init__(self, server_name: str, address: str) -> None:
        self.server_name = server_name
        "服务器名"
        self.address = address
        "服务器ws地址，如 ws://127.0.0.1:12345"
        self.msg_listeners: set[tuple[Callable[[str], bool], Callable[[str], None],bool]] = set()
        """
        监听器tuple list，当从WebSocket收到消息就会依次调用

        listener (tuple) in listeners (list[tuple])
        - [0]: test (Callable[[str], bool]) 回调函数，用于判断获取到的ws消息是否需要处理
        - [1]: on_response (Callable[[str], None]) 当test返回True，就会调用此函数
        - [2]: one_time (bool) 是否只需要执行一次
        """

        self.ws_app = websocket.WebSocketApp(self.address, on_message=self._on_ws_message)
        self.queue: Queue[dict] = Queue(maxsize=255)
        "存储消息队列，每RETRY_TIME秒检查并发送一次"

    def start(self):
        "连接ws服务器"
        threading.Thread(target=lambda : self.ws_app.run_forever(reconnect=RETRY_TIME)).start()
        queue_process = TimerRunnable(self.process_queue, 1)
        queue_process.start()
        self.queue_process = queue_process

        ok_logger.get_logger().info(f"正在尝试连接 {self.server_name} WebSocket Server...")

    def request(self, request_json: dict, test: Callable[[str], bool], on_response: Callable[[str], None]):   
        """
        参数：
        - request_json (dict) request信息
        - test (Callable[[str], bool]) 触发on_response的条件函数
        - on_response (Callable[[str], None]) 处理相应的response信息
        """
        self.add_msg_listener(test, on_response, True)
        self.queue.put(json.dumps(request_json))

    def process_queue(self):
        # ok_logger.get_logger().info("processing...")
        if not self.ws_app.keep_running: return

        failure_list: list[dict] = []
        while not self.queue.empty():
            request_str = self.queue.get()
            try:
                self.ws_app.send(request_str)
            except BaseException as exception:
                # ok_logger.get_logger().debug(f"尝试发送 {request_str} 时遇到异常 {exception}，重试中")
                failure_list.append(request_str)
        
        for failure_dict in failure_list: self.queue.put(failure_dict)

    def _on_ws_message(self, websocket: websocket.WebSocket, message):
        """
        处理ws发来的消息
        """
        remove_on_end = set()
        for test, on_message, one_time in self.msg_listeners:
            if test(message):
                on_message(str(message))
                if one_time:
                    remove_on_end.add((test, on_message, one_time))

        self.msg_listeners = set([listener for listener in self.msg_listeners if listener not in remove_on_end])

    def add_msg_listener(self, test: Callable[[str], bool],on_message: Callable[[str], None],one_time = False):   
        """
        参数：
        - test (Callable[[str], bool]) 触发on_response的条件函数
        - on_response (Callable[[str], None]) 处理相应的response信息
        - one_time (bool) 是否只需要执行一次
        """
        self.msg_listeners.add((test, on_message, one_time))

    def stop(self):
        "重置Connection成员变量"
        self.ws_app.close()
        self.queue_process.stop()
        self.msg_listeners = set()