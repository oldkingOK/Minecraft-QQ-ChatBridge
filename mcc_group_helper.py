import mcc_config_helper
import mcc_client_helper
import mcc_config_helper
import ok_logger
import cli_helper

started_list: list[str] = []

def is_start(group_id: str):
    global started_list
    return group_id in started_list

def start(group_id: str, CONFIG_PATH: str, sudo_passwd: str | None):
    global started_list
    started_list.append(group_id)

    # 启动mcc
    group_servers = mcc_config_helper.get_group_servers_dict(CONFIG_PATH)
    server_list = group_servers[group_id]
    for server_name in server_list:
        if not mcc_config_helper.is_server_enabled(CONFIG_PATH, server_name): continue
        mcc_client_helper.start_mcc(server_name=server_name, sudo_passwd=sudo_passwd)

def stop(group_id: str):
    global started_list
    started_list.remove(group_id)

def get_group_data_dict(config_path: str,ignore_disabled: bool = True) -> dict[str,str]:
    """
    获取群组消息
    dict<群组名, 服务器列表>
    """
    return mcc_config_helper.get_group_servers_dict(config_path, ignore_disabled)

def get_id_from_cli(config_path: str) -> str | None:
    group_data_dict = get_group_data_dict(config_path, True)
    ok_logger.get_logger().info("请选择群组序号：（已省略关闭的服务器）")
    # 打印组信息
    for index, (group_id, server_list) in enumerate(group_data_dict.items()):
        ok_logger.get_logger().info(f"{index}. {group_id} {server_list}")
    # 获取组序号
    group_id_list = list(group_data_dict.keys())
    index = cli_helper.select_from_numbers(range(len(group_id_list)))
    return group_id_list[index]