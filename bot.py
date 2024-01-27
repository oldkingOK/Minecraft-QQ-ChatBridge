"""
往qq群和server插入Listener和Sender
这个Listener和Sender
- 在qq群是qq客户端
- 在Server是mcc客户端

因此定义基类 Bot
"""

class Bot():
    """
    所有bot的基类
    """

    def __init__(self, group_name: str, bot_name: str) -> None:
        "成员变量初始化的函数"
        self.group_name = group_name
        self.bot_name = bot_name

    def setup(self) -> None:
        "服务、程序的启动函数"
        print(f"{self.bot_name} 完成Setup！")

    def start_listen(self) -> None:
        "开始收听所在地方的消息"
        while True:
            msg = input(f"{self.bot_name} is listening: ")
            self.on_message(msg)
    
    def on_message(self, message: str) -> None:
        "当接收到消息，调用的函数"
        print(self.handle_raw_message(message))

    def handle_raw_message(self, message: str) -> str:
        "处理源消息（一般为json string），变为可发送的消息（如 <oldkingOK> ok）"
        return message

    def say(self, message: str) -> None:
        "在所在地方说话"
        print(message)

    def stop(self) -> None:
        "关闭bot"
        pass