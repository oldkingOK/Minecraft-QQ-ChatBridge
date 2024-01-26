import json, re
import ok_logger
from enums import MessageType, DEATH_MESSAGE_FILE
from bots.mcc.config_helper import Server
from utils.text_util import remove_color_char

DEATH_MESSAGE_PATTERNS = []
"""存放死亡消息的正则表达式，用于判断死亡消息"""

def handle_mcc_raw_msg(server: Server, raw_msg: str) -> tuple[str, MessageType]:
    """
    处理mcc发进来的消息
    如果返回None，就是其他消息
    如果返回Str，就是要发到QQ的消息
    """
    result = None
    message_type = MessageType.UNKNOWN
    mcc_json = json.loads(remove_color_char(raw_msg))
    
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
            pattern_player_me = r'^\* ([a-zA-Z0-9_]+) (.+)$'
            """判断玩家聊天的正则表达式"""
            pattern_achievement = r'^([a-zA-Z0-9_]+) has made the advancement.*'
            """判断成就信息的正则表达式"""
            pattern_goal = r'^([a-zA-Z0-9_]+) has reached the goal.*'
            """判断进度信息的正则表达式"""
            pattern_death = r'^(\[death\.[a-zA-Z\.]+\]).*'
            """如果未翻译出来，那么就形如 [death.attack.genericKill.player] oldkingOK Zombie"""
            if re.fullmatch(pattern_player_chat, text) or re.fullmatch(pattern_player_me, text):
                if not is_my_self(server.account_name, text):
                    result = text
                    message_type = MessageType.CHAT
                else: 
                    result = None
                    message_type = MessageType.SENT
            
            elif re.fullmatch(pattern_join, text) or re.fullmatch(pattern_leave, text):
                if not is_my_self(server.account_name, text):
                    result = text
                    message_type = MessageType.JOIN_LEAVE

            elif re.fullmatch(pattern_achievement, text) or re.fullmatch(pattern_goal, text):
                # ok_bot has made the advancement §a[§aDiamonds!]
                if not is_my_self(server.account_name, text):
                    result = f"<喜报> {text}"
                    message_type = MessageType.ACHIEVEMENT

            elif is_death_msg(text):
                if not is_my_self(server.account_name, text):
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
                if not is_my_self(server.account_name, msg):
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