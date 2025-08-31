from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import uuid


class User(models.Model):
    """用户模型"""
    user_id = models.CharField(max_length=50, unique=True, primary_key=True)
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名', null=True, blank=True)
    password = models.CharField(max_length=128, verbose_name='密码', null=True, blank=True)
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号')
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称')
    avatar = models.URLField(blank=True, null=True, verbose_name='头像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login = models.DateTimeField(auto_now=True, verbose_name='最后登录时间')
    is_new_user = models.BooleanField(default=True, verbose_name='是否新用户')
    account_status = models.CharField(max_length=20, default='active', verbose_name='账户状态')
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return f"{self.nickname or self.username} ({self.user_id})"
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = f"user_{uuid.uuid4().hex[:8]}"
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        """检查密码是否正确"""
        return check_password(raw_password, self.password)


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
