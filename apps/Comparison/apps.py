from django.apps import AppConfig


class ComparisonConfig(AppConfig):
    """
    Comparison应用配置类
    统一使用这个类，移除未使用的UserConfig和MyAppConfig
    
    注意：迅投初始化已在 account 应用中完成，此处不再重复初始化
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Comparison'

    def ready(self):
        # 迅投初始化已在 account 应用中完成，此处不需要再次初始化
        # 如果需要使用迅投功能，直接调用相关工具函数即可
        pass
