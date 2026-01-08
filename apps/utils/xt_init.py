"""
迅投统一初始化模块
避免重复初始化，确保只初始化一次
"""
import threading
import logging
import os
from django.conf import settings
from xtquant import xtdatacenter as xtdc
from xtquant import xtdata

logger = logging.getLogger(__name__)

# 使用模块级别的锁，确保跨线程安全
_init_lock = threading.Lock()
_init_attempted = False
_init_thread = None


def init_xtdatacenter_once():
    """
    初始化迅投数据中心（只初始化一次）
    使用单例模式，确保多个应用不会重复初始化
    """
    global _init_attempted, _init_thread
    
    # 快速检查（无锁）：如果已经尝试过，直接返回
    if _init_attempted:
        return
    
    # 获取锁
    with _init_lock:
        # 双重检查（有锁）：再次确认
        if _init_attempted:
            return
        
        # 立即标记为已尝试，防止其他线程进入
        _init_attempted = True
        
        try:
            logger.info('开始初始化迅投数据中心...')
            
            # 设置 token（优先使用运行时Token，否则使用settings中的Token）
            from apps.utils.token_manager import get_xt_token
            token = get_xt_token()
            xtdc.set_token(token)
            logger.info('迅投Token已设置')
            
            # 设置连接池地址（从配置文件读取）
            xtdc.set_allow_optmize_address(settings.XT_CONFIG['ADDR_LIST'])
            logger.info('迅投连接池地址已设置')
            
            # 初始化（参数根据需要调整）
            xtdc.init(False)
            logger.info('迅投数据中心初始化完成')
            
            # 监听端口
            port = settings.XT_CONFIG['PORT']
            xtdc.listen(port=port)
            logger.info(f'迅投服务启动，开放端口：{port}')
            
            # 打印连接状态
            try:
                print('-----连接上了------')
                print(f'数据目录: {xtdata.data_dir}')
                servers = xtdata.get_quote_server_status()
                for k, v in servers.items():
                    print(f'服务器 {k}: {v}')
            except Exception as e:
                logger.warning(f'获取服务器状态失败: {str(e)}')
            
            # 在后台线程运行 xtdata.run()（阻塞调用）
            def run_xtdata():
                try:
                    logger.info('启动xtdata.run()...')
                    xtdata.run()
                except Exception as e:
                    logger.error(f'xtdata.run() 执行失败: {str(e)}', exc_info=True)
            
            _init_thread = threading.Thread(target=run_xtdata, daemon=True)
            _init_thread.start()
            
            logger.info('迅投数据中心初始化成功')
            
        except Exception as e:
            # 初始化失败时，只记录一次错误，不抛出异常
            # 这样不会影响Django启动，系统可以继续使用模拟数据
            logger.error(f'迅投数据中心初始化失败: {str(e)}')
            logger.info('系统将继续运行，将使用模拟数据模式')


def is_initialized():
    """检查是否已初始化（已尝试初始化）"""
    return _init_attempted

