from websockets.sync.client import connect
from websockets import ConnectionClosed, ConnectionClosedError

from text_util import remove_color_char
from typing import Callable
from enum import Enum, auto
import json
import re
import time

server_websocket_dict = {}
"""存放 <server_name, websocket> 键值对"""
DEBUG_MODE = True
DEATH_MESSAGE_FILE = "./asset/death_msg.json"
DEATH_MESSAGE_PATTERNS = {}
"""存放死亡消息的正则表达式，用于判断死亡消息"""
RETRY_TIME = 3
"""WebSocket重连尝试间隔（秒）"""

class MessageType(Enum):
    UNKNOWN = auto()
    SYSTEM = auto()
    DEATH = auto()
    CHAT = auto()
    ACHIEVEMENT = auto()
    DISCONNECT = auto()

def start_ws(server_name, ip, port, passwd):
    """传入参数，连接，验证并接受消息"""
    if connect_and_auth(server_name, f"ws://{ip}:{str(port)}", passwd):
        start_recv(server_name, print)

def connect_and_auth(server_name: str, address: str, password: str) -> bool:
    """
    连接并验证
    server_name 服务器名

    address "ws://127.0.0.1:8043"

    password "12345678"

    返回是否成功

    见 https://mccteam.github.io/guide/websocket/
    """
    global server_websocket_dict
    success = False
    while not success:
        try:
            websocket = connect(address)
            success = True
        except BaseException as exception:
            print(f"Server <{server_name}> Catch exception: {exception}, retry after {RETRY_TIME} seconds...")
            time.sleep(RETRY_TIME)
            continue

    data = {
        "command": "Authenticate",
        "requestId": "0",
        "parameters": [password]
    }
    """
    {"event": "OnWsCommandResponse",
      "data": "{\"success\": true, \"requestId\": \"0\", \"command\": \"Authenticate\",
        \"result\": \"Successfully authenticated!\"}"}
    """
    websocket.send(json.dumps(data))
    recv_message_json = json.loads(websocket.recv())
    if not json.loads(recv_message_json["data"])["success"]: 
        print(f"连接 {server_name} 失败")
        return False
        
    print(f"连接 {server_name} 成功！")
    # 存储
    server_websocket_dict[server_name] = websocket
    return True

def start_recv(server_name: str, msg_handler: Callable[[str], None]):
    """开始循环接受mcc websocket发来的消息"""
    global server_websocket_dict
    websocket = server_websocket_dict[server_name]
    try:
        while True:
            message = websocket.recv()
            handle_result = handle_mcc_json(mcc_json=json.loads(message))
            if handle_result is not None: 
                if DEBUG_MODE: print(f"{server_name} received: {handle_result}")
                msg_handler(handle_result)
    
    except BaseException as exception:
        print(f"Server {server_name} Catch exception: {exception}, Exit")


def handle_mcc_json(mcc_json) -> str | None:
    """
    处理mcc发进来的消息
    如果返回None，就是其他消息
    如果返回Str，就是要发到QQ的消息
    """
    result = None
    message_type = MessageType.UNKNOWN
    
    match mcc_json["event"]:
        case "OnChatRaw":
            """
            "text":"<oldkingOK> hi"

            "text":"[death.attack.genericKill] oldkingOK"
                包含 "[death." 的一般为死亡信息，包括 "[death.fell.*]" "[death.attack.*]"

            "data": "{\"text\":\"oldkingOK has made the advancement
                包含 "has made the advancement"
            """
            text = json.loads(mcc_json["data"])["text"]

            pattern_player_chat = r'^<([a-zA-Z0-9_]+)> (.+)$'
            """判断玩家聊天的正则表达式"""
            pattern_achievement = r'.*has made the advancement.*'
            """判断成就信息的正则表达式"""
            if re.fullmatch(pattern_player_chat, text):
                result = text
                message_type = MessageType.CHAT
            elif re.fullmatch(pattern_achievement, text):
                # ok_bot has made the advancement §a[§aDiamonds!]
                result = f"<喜报> {remove_color_char(text)}"
                message_type = MessageType.ACHIEVEMENT
            elif is_death_msg(text):
                """
                大多数死亡原因能够正常显示，
                由于mcc/MinecraftClient/Resources/en_us.json中未包含对应的翻译（未更新）
                导致显示
                [death.attack.genericKill.player] oldkingOK Zombie
                TODO 向mcc提交pull request
                """
                result = f"<悲报> {text}"
                message_type = MessageType.DEATH
            else:
                result = text

        case "OnDisconnect":
            result = None
            message_type = MessageType.DISCONNECT

        case "OnWsCommandResponse":
            result = None
            message_type = MessageType.SYSTEM
        
        case _:
            result = None
            message_type = MessageType.UNKNOWN
    
    if DEBUG_MODE and message_type != MessageType.UNKNOWN: 
        # 过滤掉UNKNOWN消息避免刷屏
        print(f"The handle_mcc_json type is: {message_type.name}, result is: {result}")
        print(f"The origin mcc_json is: {json.dumps(mcc_json)}")

    return result

def build_regex_pattern(pattern_str):
    # 将 %1$s, %2$s, %3$s 替换为玩家名
    pattern_str = re.sub(r'%([1-3]\$s)', r'([a-zA-Z0-9_]+)', pattern_str)
    # 构建正则表达式模式
    return re.compile(pattern_str)

def load_death_msg():
    death_msg_dict = json.load(open(DEATH_MESSAGE_FILE, 'r'))
    global DEATH_MESSAGE_PATTERNS
    DEATH_MESSAGE_PATTERNS = [build_regex_pattern(msg) for msg in list(death_msg_dict.values())]

def is_death_msg(msg) -> bool:
    """判断是否是死亡消息"""
    global DEATH_MESSAGE_PATTERNS
    if len(DEATH_MESSAGE_PATTERNS) == 0: load_death_msg()
        
    for pattern in DEATH_MESSAGE_PATTERNS:
        if pattern.match(msg):
            # 提取匹配的捕获组值
            return True
        
    return False

# "oldkingOK was killed whilst fighting Fish"
def test_death():
    print(handle_mcc_json(
        {
            "event":"OnChatRaw",
            "data":"{\"text\":\"oldkingOK was killed whilst fighting Fish\"}"
        }
    ))