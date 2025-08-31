from django.db import models
from django.utils import timezone
import uuid
import random
import string


class User(models.Model):
    """用户模型"""
    user_id = models.CharField(max_length=50, unique=True, primary_key=True)
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
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
        return f"{self.nickname or self.phone} ({self.user_id})"
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = f"user_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class VerificationCode(models.Model):
    """验证码模型"""
    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expire_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        db_table = 'verification_codes'
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone} - {self.code}"
    
    @classmethod
    def generate_code(cls, phone):
        """生成验证码"""
        # 在开发环境中使用固定验证码，生产环境使用随机验证码
        import os
        if os.getenv('DJANGO_ENV') == 'production':
            # 生产环境：生成6位数字验证码
            code = ''.join(random.choices(string.digits, k=6))
        else:
            # 开发环境：使用固定验证码
            code = '123456'
        
        # 设置5分钟过期时间
        expire_at = timezone.now() + timezone.timedelta(minutes=5)
        
        # 创建验证码记录
        verification_code = cls.objects.create(
            phone=phone,
            code=code,
            expire_at=expire_at
        )
        
        return verification_code
    
    def is_expired(self):
        """检查是否过期"""
        return timezone.now() > self.expire_at


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
        return f"{self.user.phone} - {self.created_at}"
    
    def is_expired(self):
        """检查令牌是否过期"""
        from django.utils import timezone
        return timezone.now() > self.created_at + timezone.timedelta(seconds=self.expires_in)
