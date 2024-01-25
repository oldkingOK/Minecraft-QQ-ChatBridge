from tmux_helper import add_mcc_pane, send_cmd

TMP_FOLDER = ""
"""临时ini存储文件夹"""
MCC_PATH = ""
"""MCC程序的路径"""
PASSWD = "12345678"

def init_mcc_starter(tmp_folder: str, mcc_path: str):
    global TMP_FOLDER, MCC_PATH
    TMP_FOLDER = tmp_folder
    MCC_PATH = mcc_path

def start_mcc(server_name: str, passwd: str | None):
    """
    运行一个mcc
    如果passwd为None，就不使用sudo
    """
    if passwd is not None:
        cmd = "sudo -E "
    else: cmd = ""

    cmd += f"{MCC_PATH} {TMP_FOLDER}/{server_name}.ini"
    add_mcc_pane(server_name)
    send_cmd(server_name, cmd)
    if passwd is not None: send_cmd(server_name, PASSWD)

def stop_mccs(server_list: list):
    for server_name in server_list: send_cmd(server_name, "/quit")

# def main():
#     init_mcc_starter("config.json", "mcc_config_template.ini", "./tmp", "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient")
    
#     start_mcc("Test")

# main()