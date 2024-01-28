"""
requests.get()使用了urllib3库，会导致多次尝试
该模块提供进行单次get的函数
参考：
https://stackoverflow.com/a/15431343/23243615
"""
from requests.adapters import HTTPAdapter
import requests

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=1))

def request_get(url: str) : return s.get(url=url)