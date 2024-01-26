import os
from enum import Enum, auto

# 该文件需要放在根目录
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

SUDO_PASSWD = "12345678"
"如果程序需要root执行，就设置密码，否则None"

TMP_FOLDER = ROOT_PATH + "/tmp"
"临时文件路径"

CONFIG_PATH = ROOT_PATH + "/asset/config.json"
"程序配置文件路径"

MCC_INI_TEMPLATE = ROOT_PATH + "/asset/mcc_config_template.ini"

DEATH_MESSAGE_FILE = ROOT_PATH + "/asset/death_msg.json"

MCC_PATH = ROOT_PATH +  "/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient"
"mcc程序的路径"

SESSION_NAME="mc-qq-chatbridge"
"tmux的session名称"

ONEBOT_HTTP="http://127.0.0.1:5700"
SEND_GROUP_MSG_API = "{0}/send_group_msg?group_id={1}&message="

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

class CmdType(Enum):
    SWITCH_STATE = auto()
    HELP = auto()
    ATTACH = auto()
    EXIT = auto()