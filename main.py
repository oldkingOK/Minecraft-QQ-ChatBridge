#!/usr/bin/env python3

from mcc_ws_helper import MessageType
import mcc_config_helper
import mcc_client_helper
import mcc_message_helpler
import mcc_group_helper
import ok_logger
import cli_helper
import to_qq_helper
from tmux_helper import init_tmux, attach_mcc

MCC_PATH = "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient"
CONFIG_PATH = "./asset/config.json"

def main():
    mcc_config_helper.load_config(CONFIG_PATH, "mcc_config_template.ini", "./tmp")
    mcc_client_helper.init("./tmp", MCC_PATH)
    init_tmux()
    
    # 初始化qqbot_helper, mcc_message_helper，用于发送qq消息和发送服务器消息
    to_qq_helper.init(mcc_config_helper.get_group_servers_dict(CONFIG_PATH),
                       mcc_config_helper.get_global_setting(CONFIG_PATH, "ONEBOT_HTTP"))
    mcc_message_helpler.init(mcc_config_helper.get_group_servers_dict(CONFIG_PATH))
    def msg_handler(server_name:str, msg:str, message_type: MessageType) -> None:
        if message_type != MessageType.UNKNOWN:
            to_qq_helper.send_to_qqgroup(server_name, msg)
            mcc_message_helpler.send_msg_to_other_mccs(server_name, msg)
    def on_exit():
        group_list = mcc_group_helper.get_started_groups()
        for group_id in group_list:
            mcc_client_helper.stop_mccs(mcc_config_helper.get_group_sever_list(CONFIG_PATH,group_id, True))
        
    # 死循环，接受用户输入
    try:
        ok_logger.get_logger().info("欢迎使用 Mc-QQ-bridge！ 输入Help获取帮助")
        while True:
            cmdType, handed = cli_helper.get_cmd()
            if handed: continue
            match cmdType:
                case cli_helper.CmdType.SWITCH_STATE:
                    """切换状态"""
                    group_id = mcc_group_helper.get_id_from_cli(CONFIG_PATH)
                    if group_id is None:
                        ok_logger.get_logger().info("非法输入！退出...")
                        continue

                    if not mcc_group_helper.is_start(group_id):
                        # 开始mccs
                        ok_logger.get_logger().info(f"正在启动 {group_id}")
                        mcc_group_helper.start_mcc(group_id, CONFIG_PATH, "12345678")
                        
                        # 连接mcc的websocket
                        mcc_group_helper.connect_mcc_ws(group_id,CONFIG_PATH, msg_handler)

                    else:
                        ok_logger.get_logger().info(f"正在关闭 {group_id}")
                        mcc_group_helper.stop_mcc(group_id, CONFIG_PATH)

                case cli_helper.CmdType.ATTACH:
                    """附加tmux"""
                    ok_logger.pause()
                    # TODO 附加指定群组
                    attach_mcc()
                    ok_logger.start()
                    print()
                case cli_helper.CmdType.EXIT:
                    ok_logger.get_logger().info("退出程序")
                    on_exit()
                    break
            
    except KeyboardInterrupt:
        ok_logger.get_logger().info("KeyboardInterrupt, Exit...")
        on_exit()

    return

if __name__ == "__main__":
    main()
