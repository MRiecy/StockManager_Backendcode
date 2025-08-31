from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()  # 使用Django的标准User模型


class UserToken(models.Model):
    """用户令牌模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    access_token = models.TextField(verbose_name='访问令牌')
    refresh_token = models.TextField(verbose_name='刷新令牌')
    expires_in = models.IntegerField(default=3600, verbose_name='过期时间(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    
    class Meta:
        db_table = 'user_tokens'
        verbose_name = '用户令牌'
        verbose_name_plural = '用户令牌'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
    
    def is_expired(self):
        """检查令牌是否过期"""
        from django.utils import timezone
        return timezone.now() > self.created_at + timezone.timedelta(seconds=self.expires_in)
