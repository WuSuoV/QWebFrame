from datetime import datetime


def my_response(success=True, code=200, msg=None, data=None):
    return {
        'success': success,
        'code': code,
        'msg': msg,
        'data': data,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
