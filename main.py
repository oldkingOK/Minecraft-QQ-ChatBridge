#!/usr/bin/env python3

from mcc_ws_helper import start_ws, MessageType
import mcc_config_helper
import mcc_client_helper
import mcc_message_helpler
import ok_logger
from to_qq_helper import init_to_qq_helper, send_to_qqgroup
from tmux_helper import init_tmux, attach_mcc
import threading

MCC_PATH = "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient"
CONFIG_PATH = "./asset/config.json"

def main():
    mcc_config_helper.load_config(CONFIG_PATH, "mcc_config_template.ini", "./tmp")
    mcc_client_helper.init("./tmp", MCC_PATH)
    init_tmux()
    
    # 初始化qqbot_helper, mcc_message_helper，用于发送qq消息和发送服务器消息
    init_to_qq_helper(mcc_config_helper.get_group_servers_dict(CONFIG_PATH),
                       mcc_config_helper.get_global_setting(CONFIG_PATH, "ONEBOT_HTTP"))
    mcc_message_helpler.init(mcc_config_helper.get_group_servers_dict(CONFIG_PATH))
    def msg_handler(server_name:str, msg:str, message_type: MessageType) -> None:
        if message_type != MessageType.UNKNOWN:
            send_to_qqgroup(server_name, msg)
            mcc_message_helpler.send_msg_to_other_mccs(server_name, msg)

    # 启动mcc
    server_list = mcc_config_helper.get_server_list(CONFIG_PATH)
    for server_name in server_list:
        mcc_client_helper.start_mcc(server_name=server_name, passwd="12345678")
    
    # 连接mcc的websocket
    server_config_dict = mcc_config_helper.get_server_config_dict(CONFIG_PATH)
    functions = []
    """异步执行的任务列表"""
    for server_name, config in server_config_dict.items():
        account_name = mcc_config_helper.get_account(CONFIG_PATH, server_name)
        ws_config = config["ChatBot"]["WebSocketBot"]
        ip = ws_config["Ip"]
        port = ws_config["Port"]
        passwd = ws_config["Password"]
        
        functions.append(lambda s=server_name, a=account_name, i=ip, p=port, pw=passwd, mh=msg_handler: start_ws(s, a, i, p, pw, mh))
        
    # 创建线程并运行
    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()

    # 死循环，接受用户输入
    try:
        while True:
            input("Press enter to attach, and <Ctrl-b> <d> to detach\n")
            ok_logger.pause()
            attach_mcc()
            ok_logger.start()
    except KeyboardInterrupt:
        ok_logger.get_logger().info("KeyboardInterrupt, Exit...")
        mcc_client_helper.stop_mccs(mcc_config_helper.get_server_list(CONFIG_PATH))


if __name__ == "__main__":
    main()
