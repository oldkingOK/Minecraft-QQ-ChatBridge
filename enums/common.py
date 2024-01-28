from enum import Enum, auto

class MessageType(Enum):
    UNKNOWN = auto()
    SYSTEM = auto()
    DEATH = auto()
    CHAT = auto()
    SENT = auto()
    "已发送的消息，比如<QQbot> Test"
    ACHIEVEMENT = auto()
    DISCONNECT = auto()
    JOIN_LEAVE = auto()
    CMD = auto()
    "命令消息，比如#!list"

class CmdType(Enum):
    SWITCH_STATE = auto()
    HELP = auto()
    ATTACH = auto()
    EXIT = auto()