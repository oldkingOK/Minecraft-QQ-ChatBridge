def replace_values_recursive(target, replacement):
    """
    以replacement为参考，递归替换target的键值对
    """
    for key in replacement:
        if key in target:
            if isinstance(replacement[key], dict) and isinstance(target[key], dict):
                # 如果是字典类型，递归处理
                replace_values_recursive(target[key], replacement[key])
            else:
                # 否则直接替换值
                target[key] = replacement[key]