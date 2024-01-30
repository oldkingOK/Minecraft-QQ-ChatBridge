import lib_helper.tmux_helper as tmux_helper
import bots.mcc.config_helper as mcc_config_helper
from enums.settings import TMP_FOLDER, MCC_PATH, SUDO_PASSWD

inited = False
"""该模块是否已初始化"""

def init():
    global inited
    if inited: return
    mcc_config_helper.init()
    inited = True

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

def start_mcc(server_name: str):
    """
    运行一个mcc
    如果sudo_passwd为None，就不使用sudo
    """
    _check_init()

    if SUDO_PASSWD is not None:
        cmd = "sudo -E "
    else: cmd = ""

    cmd += f"{MCC_PATH} {TMP_FOLDER}/{server_name}.ini"
    tmux_helper.add_pane(server_name)
    tmux_helper.send_keys(server_name, cmd)
    if SUDO_PASSWD is not None: tmux_helper.send_keys(server_name, SUDO_PASSWD)

def send_msg(server_name: str, msg: str):
    tmux_helper.send_keys(server_name, msg)