from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from ok_logger import get_logger
from enum import Enum, auto

class CmdType(Enum):
    SWITCH_STATE = auto()
    HELP = auto()
    ATTACH = auto()
    EXIT = auto()

def get_cmd() -> tuple[CmdType, bool]:
    """
    从用户输入获取命令
    CmdType 命令种类
    bool handled
    """

    command_completer = WordCompleter(words=['SwitchState', 'Help', 'Attach', 'Exit'], ignore_case=True)
    text = prompt('> ', completer=command_completer)
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
    
def select_from_numbers(num_list: list[int]) -> int:
    """从列表中选择，返回序号"""
    command_completer = WordCompleter(words=[str(i) for i in range(len(num_list))], ignore_case=True)
    index = int(prompt('> ', completer=command_completer))
    return index