from django.apps import AppConfig
import threading


class AccountConfig(AppConfig):
    """
    账户应用配置类
    统一使用这个类，移除未使用的MyAppConfig
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        # 使用统一的初始化模块（避免重复初始化）
        from apps.utils.xt_init import init_xtdatacenter_once
        
        # 通过线程启动初始化过程，防止阻塞主进程
        # init_xtdatacenter_once 内部有锁机制，确保只初始化一次
        thread = threading.Thread(target=init_xtdatacenter_once, daemon=True)
        thread.start()
