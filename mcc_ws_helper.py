from websockets.sync.client import connect

from text_util import remove_color_char
from typing import Callable
from enum import Enum, auto
import json
import re
import time
import ok_logger
import traceback

server_websocket_dict = {}
"""存放 <server_name, websocket> 键值对"""
DEBUG_MODE = True
DEATH_MESSAGE_FILE = "./asset/death_msg.json"
DEATH_MESSAGE_DICT: dict[str,str] = {}
"""存放死亡消息的dict，用于翻译死亡消息"""
DEATH_MESSAGE_PATTERNS = []
"""存放死亡消息的正则表达式，用于判断死亡消息"""
RETRY_TIME = 3
"""WebSocket重连尝试间隔（秒）"""

class MessageType(Enum):
    UNKNOWN = auto()
    SYSTEM = auto()
    DEATH = auto()
    CHAT = auto()
    SENT = auto()
    """已发送的消息，比如<QQbot> Test"""
    ACHIEVEMENT = auto()
    DISCONNECT = auto()
    JOIN_LEAVE = auto()

def start_ws(server_name, account_name, ip, port, passwd, msg_handler: Callable[[str, str, MessageType], None]):
    """
    与mcc连接，验证并接受消息

    服务器名

    消息接受回调函数：fun(server_name:str, msg:str, message_type: MessageType) -> None
    """
    if connect_and_auth(server_name, f"ws://{ip}:{str(port)}", passwd):
        start_recv(server_name,account_name, msg_handler)

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
            ok_logger.get_logger().info(f"Server <{server_name}> Catch exception: {exception}, retry after {RETRY_TIME} seconds...")
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
        ok_logger.get_logger().info(f"连接 {server_name} 失败")
        return False
        
    ok_logger.get_logger().info(f"连接 {server_name} 成功！")
    # 存储
    server_websocket_dict[server_name] = websocket
    return True

def start_recv(server_name: str, account_name:str, msg_handler: Callable[[str, str, MessageType], None]):
    """
    开始循环接受mcc websocket发来的消息

    服务器名

    消息接受回调函数：fun(server_name:str, msg:str, message_type: MessageType) -> None
    """
    global server_websocket_dict
    websocket = server_websocket_dict[server_name]
    try:
        while True:
            message = remove_color_char(websocket.recv())
            handle_result, message_type = handle_mcc_json(account_name, mcc_json=json.loads(message))
            if handle_result is not None: 
                msg = f"[{server_name}] {handle_result}"
                ok_logger.get_logger().debug(f"{server_name} received: [{handle_result}], which type is {message_type.name}")
                msg_handler(server_name, msg, message_type)
    
    except BaseException as exception:
        ok_logger.get_logger().info(f"Server {server_name} Catch exception: {exception}, Exit")
        ok_logger.get_logger().debug(traceback.format_exc())


def handle_mcc_json(account_name:str, mcc_json) -> str | None:
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

            pattern_join = r'([a-zA-Z0-9_]+) joined the game'
            pattern_leave = r'([a-zA-Z0-9_]+) left the game'
            pattern_player_chat = r'^<([a-zA-Z0-9_]+)> (.+)$'
            """判断玩家聊天的正则表达式"""
            pattern_achievement = r'^([a-zA-Z0-9_]+) has made the advancement.*'
            """判断成就信息的正则表达式"""
            pattern_goal = r'^([a-zA-Z0-9_]+) has reached the goal.*'
            """判断进度信息的正则表达式"""
            pattern_death = r'^(\[death\.[a-zA-Z\.]+\]).*'
            """如果未翻译出来，那么就形如 [death.attack.genericKill.player] oldkingOK Zombie"""
            if re.fullmatch(pattern_player_chat, text):
                if not text.startswith(f"<{account_name}> ") and not text.startswith(f"* {account_name} "):
                    result = text
                    message_type = MessageType.CHAT
                else: 
                    result = None
                    message_type = MessageType.SENT
            
            elif re.fullmatch(pattern_join, text) or re.fullmatch(pattern_leave, text):
                if not is_my_self(account_name, text):
                    result = text
                    message_type = MessageType.JOIN_LEAVE

            elif re.fullmatch(pattern_achievement, text) or re.fullmatch(pattern_goal, text):
                # ok_bot has made the advancement §a[§aDiamonds!]
                if not is_my_self(account_name, text):
                    result = f"<喜报> {text}"
                    message_type = MessageType.ACHIEVEMENT

            elif is_death_msg(text):
                if not is_my_self(account_name, text):
                    result = f"<悲报> {text}"
                    message_type = MessageType.DEATH

            elif re.fullmatch(pattern_death, text):
                """
                大多数死亡原因能够正常显示，
                由于mcc未获取到对应的翻译，导致显示
                [death.attack.genericKill.player] oldkingOK Zombie
                未检测出的信息从en_us.json获取
                建议向mcc提交pull request
                """
                msg = death_msg_translate(text)
                if not is_my_self(account_name, msg):
                    result = f"<悲报> {msg}"
                    message_type = MessageType.DEATH

            else:
                result = text
                message_type = MessageType.UNKNOWN

        case "OnDisconnect":
            result = None
            message_type = MessageType.DISCONNECT

        case "OnWsCommandResponse":
            result = None
            message_type = MessageType.SYSTEM
        
        case _:
            result = None
            message_type = MessageType.UNKNOWN
    
    if message_type != MessageType.UNKNOWN: 
        # 过滤掉UNKNOWN消息避免刷屏
        ok_logger.get_logger().debug(f"The handle_mcc_json type is: {message_type.name}, result is: {result}")
        ok_logger.get_logger().debug(f"The origin mcc_json is: {json.dumps(mcc_json)}")

    return result, message_type

def build_regex_pattern(pattern_str):
    # 将 %1$s, %2$s, %3$s 替换为玩家名
    pattern_str = re.sub(r'%([1-3]\$s)', r'([a-zA-Z0-9_]+)', pattern_str)
    # 构建正则表达式模式
    return re.compile(pattern_str)

def load_death_msg():
    global DEATH_MESSAGE_DICT, DEATH_MESSAGE_PATTERNS
    DEATH_MESSAGE_DICT = json.load(open(DEATH_MESSAGE_FILE, 'r'))
    DEATH_MESSAGE_PATTERNS = [build_regex_pattern(msg) for msg in list(DEATH_MESSAGE_DICT.values())]

def is_death_msg(msg) -> bool:
    """判断是否是死亡消息"""
    global DEATH_MESSAGE_PATTERNS
    if len(DEATH_MESSAGE_PATTERNS) == 0: load_death_msg()
        
    for pattern in DEATH_MESSAGE_PATTERNS:
        if pattern.match(msg):
            # 提取匹配的捕获组值
            return True
        
    return False

def death_msg_translate(text: str) -> str:
    """
    翻译死亡消息，翻译失败就返回原文
    
    [death.attack.genericKill.player] oldkingOK Zombie
    %1$s was killed whilst fighting %2$s
    """
    msg = ""
    splited = text.split(" ")
    translate_key = splited[0][1:][:-1]
    if translate_key in DEATH_MESSAGE_DICT:
        msg = DEATH_MESSAGE_DICT[translate_key]
    else: return text

    for index in range(1, len(splited)):
        msg = msg.replace(f"%{index}$s", splited[index])

    return msg

def is_my_self(account_name: str, text: str) -> bool:
    result = False
    if text.startswith(f"{account_name} "): result = True
    if text.startswith(f"* {account_name} "): result = True
    if text.startswith(f"[{account_name}] "): result = True
    return result

# "oldkingOK was killed whilst fighting Fish"
def test_death():
    ok_logger.get_logger().info(handle_mcc_json("QQbot",
        {
            "event":"OnChatRaw",
            "data":"{\"text\":\"[death.attack.genericKill.player] oldkingOK Zombie\"}"
        }
    ))