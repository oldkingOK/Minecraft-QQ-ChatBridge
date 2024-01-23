from websockets.sync.client import connect
import json
import re

websocket = None

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
    print(f"Received: {message}")

def start_recv():
    global websocket
    try:
        while True:
            message = websocket.recv()
            handle_mcc_json(mcc_json=json.loads(message))
    
    except KeyboardInterrupt:
        print("Exit")

def handle_mcc_json(mcc_json):
    match mcc_json["event"]:
        case "OnTimeUpdate" | "OnLatencyUpdate" | "OnServerTpsUpdate":
            return
        case "OnChatRaw":
            """
            "text":"<oldkingOK> hi"

            "text":"[death.attack.genericKill] oldkingOK"
                包含 "[death." 的一般为死亡信息，包括 "[death.fell.*]" "[death.attack.*]"

            "data": "{\"text\":\"oldkingOK has made the advancement
                包含 "has made the advancement"
            """
            text = json.loads(mcc_json["data"])["text"]
            print(f"The text is {text}")

            pattern_player_chat = r'<[a-zA-Z]*> .*'
            pattern_death = r'.*\[death\..*'
            pattern_achievement = r'.*has made the advancement.*'
            if re.fullmatch(pattern_player_chat, text):
                print(text)
            elif re.fullmatch(pattern_achievement, text):
                # ok_bot has made the advancement §a[§aDiamonds!]
                # TODO 需要删掉颜色符号
                print(f"<喜报> {text}")
            elif re.fullmatch(pattern_death, text):
                # 这里需要找到对应的翻译文件，比如从server-1.20.1.jar解包出的en_US.json：
                # "death.attack.genericKill.player": "%1$s was killed whilst fighting %2$s"
                # 否则就会像下面这样显示：
                # [death.attack.genericKill.player] oldkingOK Zombie
                print(f"<悲报> {text}")
            else:
                print("未知消息")

            print(json.dumps(mcc_json))
        case "OnDisconnect" | _:
            print(json.dumps(mcc_json))