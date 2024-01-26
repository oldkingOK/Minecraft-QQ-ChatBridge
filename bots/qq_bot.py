from bot import Bot
from group.group import Group
import requests
from enums import ONEBOT_HTTP, SEND_GROUP_MSG_API

class QQbot(Bot):
    def __init__(self, group_name: str, bot_name: str) -> None:
        super().__init__(group_name, bot_name)

    def setup(self) -> None:
        return super().setup()

    def start_listen(self) -> None:
        pass

    def say(self, message: str) -> None:
        requests.get(SEND_GROUP_MSG_API.format(ONEBOT_HTTP, self.bot_name) + message)
        pass

    def stop(self) -> None:
        return super().stop()