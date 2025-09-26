"""
用户模型扩展
添加XtQuant Token相关字段
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """扩展的用户模型，添加XtQuant Token字段"""
    
    # 新增Token相关字段
    xt_token = models.CharField(
        max_length=200, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="迅投Token",
        help_text="用户的迅投平台Token"
    )
    token_encrypted = models.BooleanField(
        default=True, 
        verbose_name="Token已加密",
        help_text="标识Token是否已加密存储"
    )
    token_created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Token创建时间",
        help_text="Token首次创建时间"
    )
    token_last_used = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Token最后使用时间",
        help_text="Token最后一次使用时间"
    )
    token_status = models.CharField(
        max_length=20,
        choices=[
            ('active', '有效'),
            ('expired', '已过期'),
            ('invalid', '无效'),
        ],
        default='active',
        verbose_name="Token状态",
        help_text="Token当前状态"
    )
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        db_table = "account_user"
    
    def __str__(self):
        return self.username
    
    def get_decrypted_token(self):
        """获取解密后的Token"""
        if not self.xt_token:
            return None
        
        try:
            from .token_manager import TokenManager
            return TokenManager.decrypt_token(self.xt_token)
        except Exception:
            return None
    
    def update_token_usage(self):
        """更新Token使用时间"""
        self.token_last_used = timezone.now()
        self.save(update_fields=['token_last_used'])
