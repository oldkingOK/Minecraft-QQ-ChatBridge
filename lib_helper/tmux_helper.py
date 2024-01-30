import libtmux
import ok_logger
from enums.constants import SESSION_NAME

"""
用群号定位window（如group-11223344），每当要attach session的时候，从source window里面
找到对应的server pane然后转移到群号window
"""
one_session: libtmux.session.Session = None
"""session"""
source_window: libtmux.window.Window = None
"""源window，临时存储所有Pane"""
server_pane_dict: dict[str, libtmux.Pane] = {}
"""存储 <server_name, Pane> 键值对"""

inited = False
def init():
    global inited
    if inited: return
    inited = True
    init_source_session()
    ok_logger.get_logger().info("Tmux 初始化成功.")

def _check_init():
    if not inited: raise ImportError(f"模块 {__file__} 未初始化！")

def init_source_session():
    """初始化Session"""
    tmux_server = libtmux.Server()
    global one_session
    one_session = tmux_server.new_session(session_name=SESSION_NAME, kill_session=True)
    
    global source_window
    source_window = one_session.new_window(window_name="source", attach=True)
    
def add_pane(pane_name: str):
    """
    添加新pane，运行mcc
    """
    _check_init()
    global source_window, server_pane_dict
    
    source_window.select_layout("even-horizontal")
    pane = source_window.split_window()
    server_pane_dict[pane_name] = pane

def kill_pane(pane_name: str):
    _check_init()
    server_pane_dict[pane_name].cmd('kill-pane')

def send_keys(pane_name: str, keys: str):
    """
    运行指定命令
    """
    _check_init()
    server_pane_dict[pane_name].send_keys(cmd=keys, enter=True)

def attach(pane_name_list: list[str]):
    """
    附加到mcc上 使用 <ctrl-b> <d>返回
    """
    _check_init()
    # 暂停日志输出
    ok_logger.pause()

    global one_session, moved_panes, source_window
    tmp_window = one_session.new_window(window_name="temp", attach=True)
    for pane_name in pane_name_list:
        # 转移pane
        # https://stackoverflow.com/questions/9592969/how-to-join-two-tmux-windows-into-one-as-panes
        # join-pane -s 1.1 -t 2.0
        pane = server_pane_dict[pane_name]
        pane.cmd("join-pane", '-s', f"{source_window.window_index}.{pane.pane_index}", '-t', f"{tmp_window.index}.0")
        # join-pane -t 1

    # 水平方向平均分割
    tmp_window.select_layout("even-horizontal")
    one_session.attach_session()
    
    # 在detach的时候
    for pane_name in pane_name_list:
        pane = server_pane_dict[pane_name]
        pane.cmd("join-pane", '-s', f"{tmp_window.window_index}.{pane.pane_index}", '-t', f"{source_window.index}.0")

    one_session.select_window(source_window.index)
    tmp_window.kill_window()

    # 继续日志输出
    ok_logger.start()
