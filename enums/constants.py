"""
该文件(enums.py)需要放在项目根目录
"""
from utils.path_util import get_root_path

ROOT_PATH = get_root_path()
"项目根路径"
CONFIG_PATH = ROOT_PATH + "/asset/config.json"
"配置文件路径"
DEATH_MESSAGE_FILE = ROOT_PATH + "/asset/death_msg.json"
"存放死亡信息"
RETRY_TIME = 3
"mcc WebSocket重连尝试间隔（秒）；qq Ws Server结束进程检查时间间隔（秒）"
SESSION_NAME="mc-qq-chatbridge"
"tmux的session名称"

# qq_bot相关
SEND_GROUP_MSG_API = "{0}/send_group_msg?group_id={1}&message="
GET_GROUP_MEMBER_INFO_API = "{0}/get_group_member_info?group_id={1}&user_id="
GET_MSG_API = "{0}/get_msg?message_id="
MFACE_QQ_API = "https://gxh.vip.qq.com/club/item/parcel/item/{0}/{1}/300x300.png?max_age=31536000"
"表情系列中的表情图片的api，{1}是表情uid，{0}是表情uid前两位"
FACE_QQ_API = "https://raw.gitmirror.com/koishijs/QFace/master/gif/s{0}.gif"
"小表情API，{0}是表情序号，由于不是官方api，可能无法获取到某些表情"
ONE_LINE_MAX_LENGTH = 256 
"""
Minecraft单条消息长度的最大值
如果服务器版本低于1.11 16w38a就需要修改
https://minecraft.fandom.com/wiki/Chat
"""