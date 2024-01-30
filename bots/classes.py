from lib_helper.websocket_client_util import ClientConnection

class Account():
    def __init__(self, account_dict: dict) -> None:
        self.user_name = account_dict["Account"]["Login"]

class Server():
    def __init__(self, name, server_dict: dict, account_name: str) -> None:
        self.name = name
        self.config = server_dict["Config"]
        self.account_name = account_name
        ws_config = self.config["ChatBot"]["WebSocketBot"]
        self.ip = ws_config["Ip"]
        self.port = ws_config["Port"]
        self.passwd = ws_config["Password"]
        # 连接实例
        self.connection: ClientConnection = None