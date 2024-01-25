import subprocess
import asyncio
from mcc_config_helper import load_config
from tmux_helper import init_tmux, add_mcc_pane, send_cmd, attach_mcc

TMP_FOLDER = ""
"""临时ini存储文件夹"""
MCC_PATH = ""
"""MCC程序的路径"""
PASSWD = "12345678"

def init(config_json_name: str, mcc_ini_template: str, tmp_folder: str, mcc_path: str):
    global TMP_FOLDER, MCC_PATH
    TMP_FOLDER = tmp_folder
    MCC_PATH = mcc_path
    load_config(config_json_name, mcc_ini_template, tmp_folder)

def start_mcc(server_name: str):
    """
    运行一个mcc
    """
    cmd = f"sudo -E {MCC_PATH} {TMP_FOLDER}/{server_name}.ini"
    add_mcc_pane(server_name)
    send_cmd(server_name, cmd)
    send_cmd(server_name, PASSWD)
    attach_mcc()

    print("hi")

def main():
    init("config.json", "mcc_config_template.ini", "./tmp", "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient")
    init_tmux()

    start_mcc("Test")

main()