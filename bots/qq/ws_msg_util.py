import json
import requests
from enums.constants import GET_GROUP_MEMBER_INFO_API, GET_MSG_API
from enums.settings import ONEBOT_HTTP

def is_qq_group_msg(qq_group_id: str, raw_message: str) -> bool:
    qq_json = json.loads(raw_message)
    return (
        qq_json["post_type"] == "message" and
        qq_json["message_type"] == "group" and
        qq_json["sub_type"] == "normal" and
        qq_json["group_id"] == int(qq_group_id)
    )

def get_user_display_name(group_id: str, qq: str | int):
	"""
	通过qq号获取发送者的群昵称
	"""
	response = requests.get(GET_GROUP_MEMBER_INFO_API.format(ONEBOT_HTTP.qq_bot_api, group_id) + str(qq))
	if response.status_code == 200:
		response_json = json.loads(response.text)
		card = response_json["data"]["card"]
		if card == "":
			card = response_json["data"]["nickname"]
		return card
	else:
		print(f"Try to get nickname of user {qq} but got 404, return the qq")
		return qq
	
def get_msg_sender_qq_by_id(group_id: str, msg_id: str | int):
	"""
	通过消息的id获取发送者的qq号
	"""
	response = requests.get(GET_MSG_API.format(ONEBOT_HTTP, group_id) + str(msg_id))
	if response.status_code == 200:
		response_json = json.loads(response.text)
		return response_json["data"]["sender"]["user_id"]
	else:
		print(f"Try to get msg which id is {msg_id} but got 404, return the msg id")
		return msg_id