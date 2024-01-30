"""
从qq群里接收命令的处理类
"""

import group.group_manager as group_manager
from bots.mcc_bot import MccBot
from queue import Queue
from typing import Callable
import threading
import time
import ok_logger

def log(msg: str): ok_logger.get_logger().info(msg)

def handle_command(qq_group_id: str, raw_cmd: str, on_done: Callable[[str],None] = log) -> None:
    """
    处理命令
    raw_text：
    #!help
    #!list

    参数：
    - qq_group_id (str) qq群号
    - raw_cmd (str) 带`#!`的消息
    - on_done (Callable[[str],None]) 执行完之后，会将结果传入该函数
    """
    # 删掉 `#!``
    cmd_label = raw_cmd[2:]
    
    match cmd_label:
        case "help":
            on_done(
                "【命令帮助】\n"
                "#!help 命令帮助\n"
                "#!list 玩家列表"
            )
        
        case "list":
            on_done("正在查询...")
            group = group_manager.get_group(group_name=qq_group_id)
            queue:Queue[tuple[str, list[str]]] = Queue(maxsize=255)
            for bot in group.bots.values():
                if not isinstance(bot, MccBot): continue
                # 筛出MccBot
                bot: MccBot
                bot.get_player_list(queue)

            def task():
                time.sleep(5.0)
                # Time's up
                result = ""
                while not queue.empty():
                    server_name, player_list = queue.get()
                    if len(player_list) == 0:
                        result += f"[{server_name}] 鬼服\n没有玩家在线\n"
                    else:
                        result += f"[{server_name}] 在线玩家：\n"
                        for player_name in player_list: result += player_name + "\n"
                    result += "\n"
                on_done(result[:-2]) # 删掉多余的换行符\n\n
                    
            threading.Thread(target=task).start()

        case _:
            on_done("未知命令，使用#!help获取帮助")

if __name__ == "__main__":
    print(handle_command("#!help"))
    test_dict = {
        "i": "2",
        "b": "3"
    }