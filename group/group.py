from bot import Bot
import lib.tmux_helper as tmux_helper
import ok_logger

class Group:
    def __init__(self, group_name: str) -> None:
        self.group_name = group_name
        self.bots: dict[str, Bot] = {}
        "dict[bot名称，Bot对象]"
        self.running = False
        pass

    def add_bot(self, bot: Bot):
        self.bots[bot.bot_name] = bot

    def start(self):
        self.running = True
        for bot in list(self.bots.values()):
            bot.setup()
            bot.start_listen()

    def stop(self):
        if not self.running: return
        self.running = False
        for bot in list(self.bots.values()):
            bot.stop()

    def attach(self):
        if not self.running: 
            ok_logger.get_logger().info(f"组 {self.group_name} 未启动！")
            return
        
        mcc_bot_list: list[str] = []
        for name in list(self.bots.keys()):
            if self.group_name == name: continue
            mcc_bot_list.append(name)
        # 附加
        tmux_helper.attach(mcc_bot_list)

    def broadcast(self, message: str | list[str], except_bot: str | None):
        "向组内成员发送消息，除了except_bot以外"
        for bot in list(self.bots.values()):
            if except_bot != None and except_bot == bot.bot_name: continue
            
            if isinstance(message, list):
                for line in message:
                    bot.say(line)
            else:
                bot.say(message)