import json
import toml
from dict_util import replace_values_recursive

def load_config(config_json_name: str, mcc_ini_template: str, output_file: str, server_name: str, account_name: str):
    """
    config_json_name 用于修改mcc配置的json配置文件
    mcc_ini_template 第一次运行mcc时生成的文件
    output_file 输出的ini文件
    server_name 需要加载的服务器标识符
    account_name 登录的账户标识符
    """
    with open(config_json_name, 'r') as config_json_file:
        config_json = json.load(config_json_file)
        
    with open(mcc_ini_template, 'r') as mcc_config_template_file:
        mcc_config_template_json = toml.load(mcc_config_template_file)
    
    # 替换
    replace_values_recursive(mcc_config_template_json["Main"]["General"], config_json["Accounts"][account_name])
    replace_values_recursive(mcc_config_template_json["Main"]["General"], config_json["Servers"][server_name])
    replace_values_recursive(mcc_config_template_json, config_json["Servers"][server_name]["Config"])

    # 输出
    with open(output_file, "w") as output_file:
        toml.dump(mcc_config_template_json, output_file)

def main():
    load_config("config.json", "mcc_config_template.ini", "output.ini", "Test", "QQbot")

main()