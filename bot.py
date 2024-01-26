"""
往qq群和server插入Listener和Sender
这个Listener和Sender
- 在qq群是qq号
- 在Server是mcc客户端

因此定义基类：
Bot
- `__init__` bot初始化
- `setup` 启动bot（告诉bot在哪个组
- `start_listen` 开始听取
- `handle_raw_message` 处理听取到的信息
- `say` 在所在地方说话
- `stop` 关闭bot
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
        while True:
            msg = input("I\'m listening: ")
            print(self.handle_raw_message(msg))
        
    def handle_raw_message(self, message: str) -> str:
        return message

    def say(self, message: str) -> None:
        print(message)

    def stop(self) -> None:
        pass