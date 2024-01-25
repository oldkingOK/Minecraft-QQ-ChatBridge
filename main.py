#!/usr/bin/env python3

from mcc_ws_helper import start_ws
from mcc_config_helper import load_config, get_server_dict, get_server_config_dict
from mcc_client_helper import init_mcc_starter, start_mcc, stop_mccs
from tmux_helper import init_tmux, attach_mcc
import threading

MCC_PATH = "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient"
CONFIG_PATH = "./asset/config.json"

def main():
    load_config(CONFIG_PATH, "mcc_config_template.ini", "./tmp")
    init_mcc_starter("./tmp", MCC_PATH)
    init_tmux()

    # 启动mcc
    server_dict = get_server_dict(CONFIG_PATH)
    for server_name, enabled in server_dict.items():
        if enabled: start_mcc(server_name=server_name, passwd="12345678")
    
    # 连接mcc的websocket
    server_config_dict = get_server_config_dict(CONFIG_PATH)
    functions = []
    """异步执行的任务列表"""
    for server_name, config in server_config_dict.items():
        ws_config = config["ChatBot"]["WebSocketBot"]
        ip = ws_config["Ip"]
        port = ws_config["Port"]
        passwd = ws_config["Password"]
        
        functions.append(lambda s=server_name, i=ip, p=port, pw=passwd: start_ws(s, i, p, pw))
        
    # 创建线程并运行
    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()
    
    # 死循环，接受用户输入
    try:
        while True:
            input("Press enter to attach, and <Ctrl-b> <d> to detach\n")
            attach_mcc()
    except KeyboardInterrupt:
        print("KeyboardInterrupt, Exit...")
        stop_mccs(list(get_server_dict(CONFIG_PATH).keys()))


if __name__ == "__main__":
    main()
