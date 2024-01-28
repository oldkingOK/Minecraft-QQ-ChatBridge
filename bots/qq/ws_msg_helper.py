import json
from enums.settings import FACE_TO_LINK
from enums.constants import FACE_QQ_API, MFACE_QQ_API, ONE_LINE_MAX_LENGTH
from enums.common import MessageType
from bots.qq.ws_msg_util import get_user_display_name, get_msg_sender_qq_by_id
from lib.chatimage_util import image_url_to_cicode

def handle_qq_raw_msg(group_id: str, raw_msg: str) -> tuple[list[str] | str, MessageType]:
    """
    处理QQ发送过来的json消息
    """

    # 是否将表情或图片转为 ChatImage 链接发送，以便客户端查看
    show_image = FACE_TO_LINK
    qq_json = json.loads(raw_msg)
    
    sender = qq_json["sender"]["card"]
    if sender == "": sender = qq_json["sender"]["nickname"]
    prefix = f"<{sender}> "
    result: list[str] = [prefix]
    index = 0
    """
    Message example:
    "message":[
        {"data":{"text":"首先是需要加个材质包"},"type":"text"},
        {"data":{"file":"1356f3c153","url":"https://i.m.url"},"type":"image"}
        ]
    """
    for item in qq_json["message"]:
        data_type = item["type"]
        sub_msg = ""

        match data_type:
            # 常规消息
            case "text": sub_msg = item["data"]["text"]
            case "at":
                qq = item["data"]["qq"]
                if qq == "0" or qq == "all":
                    sub_msg = "@全体成员"
                else:
                    # 获取群昵称 或者 昵称
                    sub_msg = f"@{get_user_display_name(group_id, qq)}"
            case "face": 
                # 小表情
                if show_image: sub_msg = image_url_to_cicode(FACE_QQ_API.format(item["data"]["id"]),"表情")
                else: sub_msg = "[表情]"
                
            case "mface":
                # mface 是表情系列中的一个表情，如“玉狐狸”系列表情中的“摸摸鱼鱼”，如何获取官方api:
                # 把“表情详情页”转发给好友以获取该网页的链接
                # Firefox 打开 about:config
                # 添加键值对：general.useragent.override
                # Mozilla/5.0 (Linux; Android 5.1; OPPO R9tm Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043128 Safari/537.36 V1_AND_SQ_7.0.0_676_YYB_D PA QQ/7.0.0.3135 NetType/4G WebP/0.3.0 Pixel/1080
                # 访问表情系列对应网站（需要登录）如 https://zb.vip.qq.com/hybrid/emoticonmall/detail?id=234978
                # 右键表情复制链接即可得到表情的api
                mface_uid = item["data"]["id"]
                if show_image: sub_msg = image_url_to_cicode(MFACE_QQ_API.format(mface_uid[0:2], mface_uid), "动画表情")
                else: sub_msg = "[动画表情]"
            case "reply":
                msg_id = item["data"]["id"]
                reply_to_name = get_user_display_name(group_id, get_msg_sender_qq_by_id(group_id, msg_id))
                sub_msg = f"回复 @{reply_to_name} : "
                
            # 媒体消息
            case "image":
                if show_image:
                    image_url = item["data"]["url"]
                    sub_msg = image_url_to_cicode(image_url, "图片")
                else:
                    sub_msg = "[图片]"
            case "record": sub_msg = "[语音]"
            case "file": sub_msg = "[文件]"
            case "video": sub_msg = "[视频]"
            
            # 特殊消息
            case "basketball": sub_msg = "[篮球]"
            case "new_rps": sub_msg = "[猜拳]"
            case "new_dice": sub_msg = "[骰子]"
            case "dice": sub_msg = "[骰子]"
            case "rps": sub_msg = "[剪刀石头布]"
            case "touch": 
                touched_name = get_user_display_name(group_id, get_msg_sender_qq_by_id(group_id, item["data"]["id"]))
                sub_msg = f"{sender} 戳了戳 {touched_name}"
            case "music": sub_msg = "[音乐]"
            case "weather": sub_msg = "[天气]"
            case "location": sub_msg = "[位置]"
            case "share": sub_msg = "[链接分享]"
            case "gift": sub_msg = "[礼物]"

        if len(prefix) + len(result[index]) + len(sub_msg) > ONE_LINE_MAX_LENGTH:
            # 如果长度超过一行，就加行
            result.append(prefix + sub_msg)
            index += 1

        result[index] += sub_msg

    # 如果以#!起手，就只取第一行，并把prefix删掉
    if result[0].startswith(f"{prefix}#!"): return result[0][len(prefix):], MessageType.CMD
    # 否则就时聊天信息
    return result, MessageType.CHAT