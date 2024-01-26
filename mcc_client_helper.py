import tmux_helper

TMP_FOLDER = ""
"""临时ini存储文件夹"""
MCC_PATH = ""
"""MCC程序的路径"""
PASSWD = "12345678"

def init(tmp_folder: str, mcc_path: str):
    global TMP_FOLDER, MCC_PATH
    TMP_FOLDER = tmp_folder
    MCC_PATH = mcc_path

def start_mcc(server_name: str, sudo_passwd: str | None):
    """
    运行一个mcc
    如果sudo_passwd为None，就不使用sudo
    """
    if sudo_passwd is not None:
        cmd = "sudo -E "
    else: cmd = ""

    cmd += f"{MCC_PATH} {TMP_FOLDER}/{server_name}.ini"
    tmux_helper.add_mcc_pane(server_name)
    tmux_helper.send_cmd(server_name, cmd)
    if sudo_passwd is not None: tmux_helper.send_cmd(server_name, PASSWD)

def stop_mccs(server_list: list):
    for server_name in server_list:
        tmux_helper.send_cmd(server_name, "/quit")
        tmux_helper.kill_mcc_pane(server_name)

def send_msg(server_name: str, msg: str):
    """向服务器发消息"""
    tmux_helper.send_cmd(server_name, msg)
# def main():
#     init_mcc_starter("config.json", "mcc_config_template.ini", "./tmp", "/home/oldkingok/Minecraft-QQ-ChatBridge/Minecraft-Console-Client/MinecraftClient/bin/Release/net7.0/linux-arm64/publish/MinecraftClient")
    
#     start_mcc("Test")

# main()