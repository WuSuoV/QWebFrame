import yaml

from utils.dir_path import my_path


def my_config(*keys):
    """封装配置"""
    with open(my_path('config.yaml'), 'r', encoding='utf-8') as f:
        conf = yaml.safe_load(f)
    if not keys:
        return conf  # 如果无参数，则返回整个配置
    result = conf
    result_log = 'result'
    for key in keys:
        # 根据参数递进依次获取
        try:
            result = result.get(key)
            result_log = f'{result_log}["{key}"]'
        except AttributeError:
            return None
        except Exception as e:
            raise
    return result
