import traceback
from utils.log import logger


def traceback_info(e: Exception):
    """错误信息格式化"""
    msg = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(msg)


def log_exception(func):
    """装饰器：捕捉异常并记录到日志中"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = traceback_info(e)
            logger.error("发生错误：%s", str(e))
            logger.error("详细错误信息：%s", error_message)
            # 可以选择重新抛出异常，或不抛出，根据需求决定
            # raise

    return wrapper
