from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VerificationCode, UserToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理员"""
    list_display = ('phone', 'nickname', 'user_id', 'account_status', 'is_new_user', 'created_at', 'last_login')
    list_filter = ('account_status', 'is_new_user', 'created_at')
    search_fields = ('phone', 'nickname', 'user_id')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('个人信息', {'fields': ('nickname', 'avatar', 'is_new_user')}),
        ('账户状态', {'fields': ('account_status', 'is_active', 'is_staff', 'is_superuser')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
        ('权限', {'fields': ('groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'nickname'),
        }),
    )
    
    readonly_fields = ('user_id', 'created_at', 'last_login')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """验证码管理员"""
    list_display = ('phone', 'code', 'is_used', 'created_at', 'expire_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('phone',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """禁止手动添加验证码"""
        return False


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    """用户令牌管理员"""
    list_display = ('user', 'token_type', 'expires_in', 'created_at', 'is_active')
    list_filter = ('token_type', 'is_active', 'created_at')
    search_fields = ('user__phone', 'user__nickname')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """禁止手动添加令牌"""
        return False
