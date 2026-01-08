"""
数据库连接工具模块
提供统一的MongoDB连接管理
"""

import logging
from pymongo import MongoClient
from django.conf import settings

logger = logging.getLogger(__name__)

# MongoDB连接配置
# 如果settings中有MONGODB_CONFIG，使用settings中的配置
# 否则使用默认配置
try:
    MONGODB_URI = getattr(settings, 'MONGODB_URI', 'mongodb://81.68.81.245:27017/mydatabase?authSource=admin')
    MONGODB_DB_NAME = getattr(settings, 'MONGODB_DB_NAME', 'admin')
except:
    # 如果settings未加载，使用默认值
    MONGODB_URI = 'mongodb://81.68.81.245:27017/mydatabase?authSource=admin'
    MONGODB_DB_NAME = 'admin'

# 全局客户端连接对象（单例模式）
_client = None


def get_mongodb_client():
    """
    获取MongoDB客户端连接（单例模式）
    
    返回:
        MongoClient: MongoDB客户端对象
    """
    global _client
    
    if _client is None:
        try:
            _client = MongoClient(MONGODB_URI)
            logger.info('MongoDB客户端连接创建成功')
        except Exception as e:
            logger.error(f'创建MongoDB客户端连接失败: {str(e)}', exc_info=True)
            raise
    
    return _client


def get_mongodb_db(db_name=None):
    """
    获取MongoDB数据库对象
    
    参数:
        db_name: 数据库名称，如果为None则使用默认数据库
    
    返回:
        Database: MongoDB数据库对象
    """
    if db_name is None:
        db_name = MONGODB_DB_NAME
    
    try:
        # 获取客户端连接（单例模式）
        client = get_mongodb_client()
        # 返回数据库对象（每次调用都返回新对象，因为db_name可能不同）
        # 但底层客户端连接是共享的
        db = client[db_name]
        return db
    except Exception as e:
        logger.error(f'创建MongoDB数据库对象失败: {str(e)}', exc_info=True)
        raise


def close_mongodb_connection():
    """
    关闭MongoDB连接
    """
    global _client
    
    if _client is not None:
        try:
            _client.close()
            logger.info('MongoDB连接已关闭')
        except Exception as e:
            logger.error(f'关闭MongoDB连接失败: {str(e)}', exc_info=True)
        finally:
            _client = None


# 注意：不再提供全局db对象
# 所有代码都应该通过 get_mongodb_db() 函数获取数据库对象
# 这样可以确保连接管理和错误处理的一致性

