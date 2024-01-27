from enum import Enum, auto
from enums.constants import ROOT_PATH
import config_helper

# Config: 给ide类型提示
SUDO_PASSWD: str
"如果程序需要root执行，就设置密码，否则None (null)"
TMP_FOLDER: str
"临时ini文件存放路径"
MCC_INI_TEMPLATE: str
"第一次执行mcc后生成的配置文件"
MCC_PATH: str
"mcc程序的路径"
ONEBOT_HTTP: str
"Onebot主动http地址，如http://127.0.0.1:5700"
ONEBOT_WS_HOST: str
"Onebot被动websocket host"
ONEBOT_WS_PORT: int
"Onebot被动websocket port"
FACE_TO_LINK: bool
"是否将 图片/表情 转换成 ci 链接"

class Config(Enum):
    "存放设置"

    SUDO_PASSWD = auto()
    TMP_FOLDER = auto()
    MCC_INI_TEMPLATE = auto()
    MCC_PATH = auto()
    ONEBOT_HTTP=auto()
    ONEBOT_WS_HOST = auto()
    ONEBOT_WS_PORT = auto()
    FACE_TO_LINK = auto()

def load_from_setting_json(setting_json: dict[str, str]):
    """
    从配置文件的"Settings"加载键值对
    
    支持变量：{root} 项目根目录，如 /home/oldkingOK/Minecraft-QQ-ChatBridge
    """

    for config in Config:
        setting = setting_json[config.name]
        if type(setting) == str and '{root}' in setting: setting = setting.format(root=ROOT_PATH)
        globals()[config.name] = setting


inited = False
def _init():
    global inited, config_json
    inited = True
    load_from_setting_json(config_helper.get_settings())
if not inited: _init()