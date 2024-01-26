import re

def remove_color_char(text: str) -> str:
    color_pattern = re.compile(r'§[a-zA-Z]')
    return re.sub(color_pattern, '', text)