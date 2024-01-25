import logging

class OkFormatter(logging.Formatter):
    def format(self, record):
        log_time = self.formatTime(record, "%H:%M:%S")  # 格式化时间
        log_message = record.getMessage()  # 获取日志消息

        log_output = f"[{log_time}] [{record.filename}<line:{record.lineno}>/{record.levelname}]: {log_message}"
        return log_output

class InfiniteBufferHandler(logging.Handler):
    def __init__(self, can_log=True):
        super().__init__()
        self.buffer = []
        self.can_log = can_log

    def emit(self, record):
        self.buffer.append(self.format(record))
        if self.can_log: self.flush_buffer()

    def flush_buffer(self):
        for message in self.buffer:
            self.emit_log_message(message)
        self.buffer = []

    def emit_log_message(self, message):
        print(message)

buffer_handler: InfiniteBufferHandler = None
logger: logging.Logger = None

def init_ok_logger() -> None:
    global buffer_handler, logger
    logger = logging.getLogger("Main")
    logger.setLevel(logging.DEBUG)
    
    buffer_handler = InfiniteBufferHandler()
    buffer_handler.setLevel(logging.DEBUG)
    buffer_handler.setFormatter(OkFormatter())

    logger.addHandler(buffer_handler)

def get_logger() -> logging.Logger:
    global buffer_handler, logger
    if logger is None: init_ok_logger()
    return logger

def start():
    """继续输出，并刷新缓冲区"""
    buffer_handler.flush_buffer()
    buffer_handler.can_log = True

def pause():
    """暂停输出，之后的输出都暂时存放在缓冲区"""
    buffer_handler.can_log = False

if __name__ == "__main__":
    get_logger().info("Hihihi")