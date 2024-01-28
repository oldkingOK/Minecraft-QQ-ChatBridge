from typing import Callable
from enums.constants import RETRY_TIME
import threading
import time

class TimerRunnable:
    "创建线程，每persecond秒执行callable"
    def __init__(self, callable: Callable[[], None], persecond = RETRY_TIME) -> None:
        self.callable = callable
        self.running = False
        self.persecond = persecond
        "运行间隔时长（秒）"
        pass

    def start(self):
        if self.running: return
        else: 
            self.running = True
            threading.Thread(target=self.run).start()

    def run(self):
        while True:
            if not self.running: return
            self.callable()
            time.sleep(self.persecond)

    def stop(self): self.running = False