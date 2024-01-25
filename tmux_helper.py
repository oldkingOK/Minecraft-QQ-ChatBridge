import libtmux

"""
用群号定位window（如group-11223344），每当要attach session的时候，从source window里面
找到对应的server pane然后转移到群号window
"""
SESSION_NAME="mcc"
source_session = None
"""session"""
source_window = None
"""源window，临时存储所有Pane"""
server_pane_dict = {}
"""存储 <server_name, Pane> 键值对"""

def init_tmux():
    init_source_session()
    print("Tmux init successful.")

def init_source_session():
    tmux_server = libtmux.Server()
    global source_session
    source_session = tmux_server.new_session(session_name=SESSION_NAME, kill_session=True)

    global source_window
    source_window = source_session.new_window(window_name="source", attach=True)
    

def add_mcc_pane(server_name: str):
    """
    添加新pane，运行mcc
    """
    global source_window, server_pane_dict
    pane = source_window.split_window()
    server_pane_dict[server_name] = pane
    pane.send_keys(cmd="test", enter=True)

def send_cmd(server_name: str, cmd: str):
    """
    运行指定命令
    """
    server_pane_dict[server_name].send_keys(cmd=cmd, enter=True)

def attach_mcc():
    """
    附加到mcc上 使用 <ctrl-d> 返回
    """
    global source_session, source_window
    # 水平方向平均分割
    source_window.select_layout("even-horizontal")
    source_session.attach_session()