"""
Token管理工具模块
统一管理迅投Token的获取和更新
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# 运行时Token存储（优先级最高）
_runtime_token = None


def get_xt_token():
    """
    获取当前的迅投Token
    
    优先级：
    1. 运行时Token（通过token_login接口更新的）
    2. settings.XT_CONFIG['TOKEN']（配置文件中的）
    
    返回:
        str: 当前Token
    """
    global _runtime_token
    
    # 优先使用运行时Token
    if _runtime_token:
        return _runtime_token
    
    # 否则使用settings中的Token
    return settings.XT_CONFIG.get('TOKEN', '')


def set_xt_token(token):
    """
    设置迅投Token（运行时）
    
    参数:
        token: 新的Token值
    """
    global _runtime_token
    _runtime_token = token
    
    # 同时更新settings中的配置（用于其他模块）
    if hasattr(settings, 'XT_CONFIG'):
        settings.XT_CONFIG['TOKEN'] = token
        logger.info(f'Token已更新（运行时），长度: {len(token)}')


def clear_xt_token():
    """
    清除运行时Token（恢复到settings中的默认值）
    """
    global _runtime_token
    _runtime_token = None
    logger.info('运行时Token已清除')







