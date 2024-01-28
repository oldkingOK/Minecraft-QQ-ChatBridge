from typing import Callable
from random import randint
import json

class MccCmd():
    def __init__(self, on_response: Callable[[str], None], command: str, *args) -> None:
        """
        参数：
        - on_response ((raw_response_str) -> None) 当得到response时，调用的回调函数
            - raw_response_str (str) 得到的response字符串
        - command (str) WebSocket命令名，详细请看
            Minecraft-Console-Client/MinecraftClient/ChatBots/WebSocketBot.cs
        - *args WebSocket命令需要的参数
        """
        self.requestId = str(get_rand_int())
        self.request_json = {
            "command": command,
            "requestId": self.requestId,
            "parameters": list(args)
        }
        self.on_response = on_response

    def test(self, raw_response_str: str) -> bool:
        """
        测试函数，判断message是否是符合要求的Response

        {"event": "OnWsCommandResponse",
            "data": "{\"success\": true,
              \"requestId\": \"0\",
                \"command\": \"Authenticate\",
            \"result\": \"Successfully authenticated!\"}"
        }

        参数：
        - raw_response_str (str) 得到的response字符串
        """
        response_json = json.loads(raw_response_str)
        if response_json["event"] != "OnWsCommandResponse": return False
        data_json = json.loads(response_json["data"])
        return data_json["requestId"] == self.requestId

class Authenticate(MccCmd):
    def __init__(self, on_response: Callable[[str], None], ws_passwd: str, ) -> None:
        super().__init__(on_response, "Authenticate", ws_passwd)

class GetOnlinePlayers(MccCmd):
    def __init__(self, on_response: Callable[[str], None]) -> None:
        super().__init__(on_response, "GetOnlinePlayers")

def get_rand_int():
    return randint(100000, 999999)