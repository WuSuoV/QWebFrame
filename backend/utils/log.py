import logging
import traceback
from logging.handlers import RotatingFileHandler
from utils.dir_path import my_path
from utils.load_config import my_config


def setup_custom_logger(name, console=True, console_level=logging.DEBUG, file=None, file_level=logging.DEBUG,
                        colorable=True, logger_level=logging.DEBUG,
                        max_bytes=my_config('log', 'max_size') * 1024 * 1024, backup_count=10):
    # 默认格式
    default_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    if colorable:
        try:
            import colorlog
            formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'blue',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'purple'
                }
            )
        except ImportError:
            formatter = default_formatter
    else:
        formatter = default_formatter

    logger = logging.getLogger(name)
    logger.setLevel(logger_level)

    if not logger.handlers:
        # 控制台日志
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)  # 控制台日志级别
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        # 文件日志
        if file:
            file_handler = RotatingFileHandler(file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
            file_handler.setLevel(file_level)  # 文件日志级别
            file_handler.setFormatter(default_formatter)
            logger.addHandler(file_handler)

    return logger


def logger_error_fmt(e: Exception):
    msg = traceback.format_exception(type(e), e, e.__traceback__)
    logger.error(''.join(msg))


logger = setup_custom_logger('my_logger', console=my_config('log', 'console'),
                             colorable=my_config('log', 'colorable'),
                             file=my_path('log/my_log.log'))

if __name__ == '__main__':
    # 测试日志记录
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
