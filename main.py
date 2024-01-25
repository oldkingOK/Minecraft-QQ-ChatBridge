#!/usr/bin/env python3

from mcc_config_helper import load_config, get_server_dict
from mcc_start_helper import init_mcc_starter, start_mcc
from tmux_helper import init_tmux, attach_mcc

MCC_PATH = "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient"

def main():
    load_config("config.json", "mcc_config_template.ini", "./tmp")
    init_mcc_starter("./tmp", MCC_PATH)
    init_tmux()

    server_dict = get_server_dict("config.json")
    for server_name, enabled in server_dict.items():
        if enabled: start_mcc(server_name=server_name, passwd="12345678")
    
    attach_mcc()

    # connect_and_auth("ws://127.0.0.1:8043", "12345678")
    # start_recv(print)
    # start mcc

if __name__ == "__main__":
    main()
