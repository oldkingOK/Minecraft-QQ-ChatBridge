from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from ok_logger import get_logger
from enums.common import CmdType

history = InMemoryHistory()

def get_cmd() -> tuple[CmdType, bool]:
    """
    从用户输入获取命令
    CmdType 命令种类
    bool handled
    """
    global history
    command_completer = WordCompleter(words=['SwitchState', 'Help', 'Attach', 'Exit'], ignore_case=True)
    text = prompt('> ', completer=command_completer, history=history)
    match text:
        case "SwitchState": return CmdType.SWITCH_STATE, False
        case "Attach": return CmdType.ATTACH, False
        case "Exit": return CmdType.EXIT, False
        case "Help"| _: 
            print_help()
            return CmdType.HELP, True

def print_help():
    get_logger().info(
                "Mc-QQ-bridge 命令帮助：\n"
                " SwitchState    - 开关群组状态\n"
                " Attach         - 附加到群组的session上, 用 <Ctrl-B> <d> 来退出\n"
                " Help           - 打印帮助信息\n"
                " Exit           - 退出程序\n"
                "提示：使用<Tab>可以补全命令"
            )
    
def select_from_numbers(num_list: list[int]) -> int | None:
    """
    从列表中选择，返回序号
    如果非法输入，就返回None
    """
    global history
    command_completer = WordCompleter(words=[str(i) for i in range(len(num_list))], ignore_case=True)
    try:
        index = int(prompt('> ', completer=command_completer, history=history))
    except ValueError:
        return None
    if index not in num_list: return None
    return index