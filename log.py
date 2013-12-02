#coding=utf-8

import logging

class Logging(object):
    def __init__(self):
        # 创建一个logger
        self.logger = logging.getLogger('mylogger')
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        self.fh = logging.FileHandler('error.log')
        self.fh.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(self.fh)
        
    def get_logger(self):
        return self.logger


if __name__ == "__main__":
    logging = Logging()
    logger = logging.get_logger();
    logger.info("for test")
