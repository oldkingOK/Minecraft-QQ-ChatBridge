#!/usr/bin/env python3

import config_helper
from enums.common import CmdType
import lib.tmux_helper as tmux_helper
import lib.cli_helper as cli_helper
import ok_logger

# for test
import bots.mcc_bot as mcc_bot
import bots.qq_bot as qq_bot
import group.group_manager as group_manager

def main():
    tmux_helper.init()
    mcc_bot.init()
    qq_bot.init()

    # 初始化group_manager
    for group_id, server_list in config_helper.get_groups().items():
        group = group_manager.get_group(group_id)
        group.add_bot(qq_bot.QQbot(group_name=group_id, bot_name=group_id))
        for server_name in server_list:
            group.add_bot(mcc_bot.MccBot(group_name=group_id, server_name=server_name))

    # 死循环，接受用户输入
    try:
        ok_logger.get_logger().info("欢迎使用 Mc-QQ-bridge！ 输入Help获取帮助")
        while True:
            cmdType, handed = cli_helper.get_cmd()
            if handed: continue
            match cmdType:
                case CmdType.SWITCH_STATE:
                    """切换状态"""
                    # 这里的group_name指的是组名，概念上区分于群号
                    # 本程序是把群号当成组名，所以混用
                    group_name = group_manager.get_group_from_cli()
                    if group_name is None or (group := group_manager.get_group(group_name)) is None:
                        ok_logger.get_logger().info("非法输入！退出...")
                        continue

                    if group.running:
                        group.stop()
                    else:
                        group.start()

                case CmdType.ATTACH:
                    # 获取组
                    group_name = group_manager.get_group_from_cli()
                    if group_name is None or (group := group_manager.get_group(group_name)) is None:
                        ok_logger.get_logger().info("非法输入！退出...")
                        continue
                    group.attach()

                case CmdType.EXIT:
                    ok_logger.get_logger().info("退出程序中...")
                    group_manager.stop_all()
                    break

    except KeyboardInterrupt:
        ok_logger.get_logger().info("KeyboardInterrupt, 退出程序中...")
        group_manager.stop_all()

    qq_bot.on_end()
    return

if __name__ == "__main__":
    main()