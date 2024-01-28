from bot import Bot
import bots.mcc.client_helper as client_helper
import ok_logger
import bots.mcc.ws_helper as mcc_ws_helper
import bots.mcc.ws_msg_helper as mcc_ws_msg_helper
import group.group_manager as group_manager
from bots.mcc.config_helper import get_server
from enums.common import MessageType
from queue import Queue

inited = False
def init():
    global inited
    if inited: return
    inited = True
    client_helper.init()

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

class MccBot(Bot):
    def __init__(self, group_name: str, server_name: str) -> None:
        _check_init()
        super().__init__(group_name, bot_name=server_name)
        self.server = get_server(server_name)

    def setup(self) -> None:
        # 启动mcc实例
        client_helper.start_mcc(self.bot_name)
        return super().setup()

    def say(self, message: str) -> None:
        client_helper.send_msg(self.server.name, f"/me {message}")

    def start_listen(self) -> None:
        mcc_ws_helper.start_ws(self.server,self.on_message)

    def on_message(self, message: str) -> None:
        result, message_type = self.handle_raw_message(message)

        if result is not None and message_type is not MessageType.UNKNOWN: 
            message = f"[{self.server.name}] {result}"
            ok_logger.get_logger().debug(f"服务器 {self.server.name} 收到: {result}, 消息种类：{message_type.name}")
            group_manager.get_group(self.group_name).broadcast(message, self.bot_name)

    def handle_raw_message(self, message: str) -> tuple[str, MessageType]:
        # return: (result:str, message_type: MessageType)
        return mcc_ws_msg_helper.handle_mcc_raw_msg(self.server, message)
    
    def stop(self) -> None:
        client_helper.send_msg(self.server.name, "/quit")
        self.server.connection.stop()

    def get_player_list(self, queue: Queue[tuple[str, list[str]]]) -> list[str]:
        """
        获取该服务器玩家列表（已排除bot本身）

        参数：
        - queue (Queue[tuple[str, list[str]]]) 列表队列，用于存储已经获取到的玩家列表
            - tuple (server_name: str, player_list: list[str])
        """
        mcc_ws_helper.get_player_list(self.server, queue)
        pass
        