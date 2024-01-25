from websockets.sync.client import connect
from text_util import remove_color_char
from typing import Callable
import json
import re

websocket = None
DEBUG_MODE = True
DEATH_MESSAGE_FILE = "./asset/death_msg.json"
DEATH_MESSAGE_PATTERNS = {}
"""存放死亡消息的正则表达式，用于判断死亡消息"""

def connect_and_auth(address: str, password: str):
    """
    address "ws://127.0.0.1:8043"
    password "12345678"
    see https://mccteam.github.io/guide/websocket/
    """
    global websocket
    websocket = connect(address)
    data = {
        "command": "Authenticate",
        "requestId": "0",
        "parameters": [password]
    }
    websocket.send(json.dumps(data))
    message = websocket.recv()
    if DEBUG_MODE: print(f"Received: {message}")

def start_recv(msg_handler: Callable[[str], None]):
    global websocket
    try:
        while True:
            message = websocket.recv()
            handle_result = handle_mcc_json(mcc_json=json.loads(message))
            msg_handler(handle_result)
    
    except KeyboardInterrupt:
        print("Exit")

def handle_mcc_json(mcc_json) -> str | None:
    """
    处理mcc发进来的消息
    如果返回None，就是其他消息
    如果返回Str，就是要发到QQ的消息
    """
    result = None
    
    match mcc_json["event"]:
        case "OnTimeUpdate" | "OnLatencyUpdate" | "OnServerTpsUpdate":
            result = None
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
            elif re.fullmatch(pattern_achievement, text):
                # ok_bot has made the advancement §a[§aDiamonds!]
                result = f"<喜报> {remove_color_char(text)}"
            elif is_death_msg(text):
                """
                大多数死亡原因能够正常显示，
                由于mcc/MinecraftClient/Resources/en_us.json中未包含对应的翻译（未更新）
                导致显示
                [death.attack.genericKill.player] oldkingOK Zombie
                TODO 向mcc提交pull request
                """
                result = f"<悲报> {text}"
            else:
                result = text

        case "OnDisconnect" | _:
            if DEBUG_MODE: print(f"The origin mcc_json is: {json.dumps(mcc_json)}")
            return None
    
    if DEBUG_MODE: 
        print(f"The handle_mcc_json result is: {result}")
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