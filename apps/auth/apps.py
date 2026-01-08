from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    label = 'stock_auth'  # 使用不同的标签避免与Django内置auth冲突
    verbose_name = '认证管理'

