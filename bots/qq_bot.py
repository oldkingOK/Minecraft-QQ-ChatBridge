from bot import Bot
import requests
from enums.settings import ONEBOT_HTTP
from enums.constants import SEND_GROUP_MSG_API
from enums.common import MessageType
from urllib.parse import quote
import bots.qq.ws_helper as qq_ws_helper
import bots.qq.ws_msg_helper as qq_ws_msg_helper
import bots.qq.cmd_helper as qq_cmd_helper
import group.group_manager as group_manager
import ok_logger

inited = False
def init():
    global inited
    if inited: return
    inited = True
    qq_ws_helper.init()

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

def on_end():
    qq_ws_helper.on_end()

class QQbot(Bot):
    def __init__(self, group_name: str, bot_name: str) -> None:
        _check_init()
        super().__init__(group_name, bot_name)

    def setup(self) -> None:
        return super().setup()

    def start_listen(self) -> None:
        qq_ws_helper.add_listener(self.group_name, self.on_message)

    def on_message(self, message: str) -> None:
        result, message_type  = self.handle_raw_message(message)
        ok_logger.get_logger().info(f"{self.group_name} 收到类型是 {message_type} 的qq消息：{result}，")
        # 发送消息到同组其他成员
        group = group_manager.get_group(self.group_name)
        if message_type == MessageType.CHAT:
            group.broadcast(result, self.group_name)
        elif message_type == MessageType.CMD:
            qq_cmd_helper.handle_command(
                qq_group_id=self.group_name, raw_cmd=result, on_done=self.say
            )

    def handle_raw_message(self, message: str):
        return qq_ws_msg_helper.handle_qq_raw_msg(group_id=self.group_name, raw_msg=message)

    def say(self, message: str) -> None:
        requests.get(SEND_GROUP_MSG_API.format(ONEBOT_HTTP, self.bot_name) + quote(message))
        pass

    def stop(self) -> None:
        qq_ws_helper.remove_listener(self.group_name)
        return super().stop()