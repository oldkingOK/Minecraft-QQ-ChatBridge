from os import path, pardir

def get_root_path() -> str:
    "获取项目根路径"
    return path.abspath(path.join(path.abspath(path.dirname(__file__)), pardir))