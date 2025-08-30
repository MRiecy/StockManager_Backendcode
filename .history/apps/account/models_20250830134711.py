from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import random
import string


class User(AbstractUser):
    """自定义用户模型"""
    user_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.URLField(blank=True, verbose_name='头像')
    is_new_user = models.BooleanField(default=True, verbose_name='是否新用户')
    account_status = models.CharField(
        max_length=20, 
        choices=[
            ('active', '活跃'),
            ('inactive', '非活跃'),
            ('suspended', '暂停')
        ],
        default='active',
        verbose_name='账户状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login = models.DateTimeField(auto_now=True, verbose_name='最后登录时间')
    
    # 覆盖默认字段
    username = None
    email = None
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'account_user'
    
    def __str__(self):
        return f"{self.nickname or self.phone}"
    
    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = f"用户{self.phone[-4:]}"
        super().save(*args, **kwargs)


class VerificationCode(models.Model):
    """验证码模型"""
    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expire_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        db_table = 'account_verification_code'
        indexes = [
            models.Index(fields=['phone', 'created_at']),
            models.Index(fields=['expire_at']),
        ]
    
    def __str__(self):
        return f"{self.phone}-{self.code}"
    
    def is_expired(self):
        """检查验证码是否过期"""
        return timezone.now() > self.expire_at
    
    @classmethod
    def generate_code(cls, phone):
        """生成验证码"""
        # 生成6位数字验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 设置过期时间为5分钟后
        expire_at = timezone.now() + timezone.timedelta(minutes=5)
        
        # 创建验证码记录
        verification_code = cls.objects.create(
            phone=phone,
            code=code,
            expire_at=expire_at
        )
        
        return verification_code


class UserToken(models.Model):
    """用户令牌模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    access_token = models.TextField(verbose_name='访问令牌')
    refresh_token = models.TextField(verbose_name='刷新令牌')
    token_type = models.CharField(max_length=20, default='Bearer', verbose_name='令牌类型')
    expires_in = models.IntegerField(default=3600, verbose_name='过期时间(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    
    class Meta:
        verbose_name = '用户令牌'
        verbose_name_plural = '用户令牌'
        db_table = 'account_user_token'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['access_token']),
        ]
    
    def __str__(self):
        return f"{self.user.phone}-{self.token_type}"
    
    def is_expired(self):
        """检查令牌是否过期"""
        from django.utils import timezone
        expire_time = self.created_at + timezone.timedelta(seconds=self.expires_in)
        return timezone.now() > expire_time
