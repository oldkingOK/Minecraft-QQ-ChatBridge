import lib.cli_helper as cli_helper
import config_helper
import ok_logger
import group.group_manager as group_manager
from group.group import Group

groups: dict[str, Group] = {}
"dict[群组名,群组]"

def get_group(group_name: str) -> Group:
    return groups.setdefault(group_name, Group(group_name))

def get_group_from_cli() -> str | None:
    """
    通过用户输入，获取群号
    非法输入，返回None
    """
    ok_logger.get_logger().info("请选择群组序号：（已省略未启用的服务器）")

    # 打印组信息
    groups: dict = config_helper.get_groups()
    for index, (group_id, server_list) in enumerate(groups.items()):
        running = "Running" if group_manager.get_group(group_id).running else "Waiting"
        ok_logger.get_logger().info(f"{index}. {running} | {group_id} | {server_list}")

    # 获取组序号
    group_id_list = list(groups.keys())
    index = cli_helper.select_from_numbers(range(len(group_id_list)))
    # 合法判断
    if index is None: return None
    return group_id_list[index]

def stop_all() -> None:
    for group in groups.values():
        group.stop()