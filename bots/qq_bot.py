from bot import Bot
import requests
from enums.settings import ONEBOT_HTTP
from enums.constants import SEND_GROUP_MSG_API
import bots.qq.ws_helper as qq_ws_helper
import bots.qq.ws_msg_helper as qq_ws_msg_helper
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

class QQbot(Bot):
    def __init__(self, group_name: str, bot_name: str) -> None:
        _check_init()
        super().__init__(group_name, bot_name)

    def setup(self) -> None:
        return super().setup()

    def start_listen(self) -> None:
        qq_ws_helper.add_listener(self.group_name, self.on_message)

    def on_message(self, message: str) -> None:
        result = qq_ws_msg_helper.handle_qq_raw_msg(group_id=self.group_name, raw_msg=message)
        # 发送消息到同组其他成员
        group = group_manager.get_group(self.group_name)
        group.broadcast(result, self.group_name)
        ok_logger.get_logger().info(f"{self.group_name} 收到qq消息：{result}")

    def say(self, message: str) -> None:
        requests.get(SEND_GROUP_MSG_API.format(ONEBOT_HTTP, self.bot_name) + message)
        pass

    def stop(self) -> None:
        qq_ws_helper.remove_listener(self.group_name)
        return super().stop()