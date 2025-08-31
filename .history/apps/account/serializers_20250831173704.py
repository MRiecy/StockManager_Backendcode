from rest_framework import serializers
from .models import User, UserToken


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['user_id', 'username', 'phone', 'nickname', 'avatar', 'is_new_user', 
                 'created_at', 'last_login', 'account_status']
        read_only_fields = ['user_id', 'created_at', 'last_login']


class RegisterSerializer(serializers.Serializer):
    """注册序列化器 - 简化版"""
    username = serializers.CharField(
        max_length=50, 
        min_length=3,
        help_text="用户名，3-50个字符"
    )
    password = serializers.CharField(
        max_length=128, 
        min_length=6, 
        write_only=True,
        help_text="密码，至少6位"
    )
    nickname = serializers.CharField(
        max_length=50, 
        required=False, 
        allow_blank=True,
        help_text="昵称（可选）"
    )
    phone = serializers.CharField(
        max_length=11, 
        required=False, 
        allow_blank=True,
        help_text="手机号（可选）"
    )
    
    def validate_username(self, value):
        """验证用户名是否已存在"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value
    
    def validate_password(self, value):
        """验证密码强度"""
        if len(value) < 6:
            raise serializers.ValidationError("密码长度至少6位")
        return value


class LoginSerializer(serializers.Serializer):
    """登录序列化器 - 支持用户名或手机号登录"""
    username_or_phone = serializers.CharField(
        max_length=50,
        help_text="用户名或手机号"
    )
    password = serializers.CharField(
        max_length=128, 
        write_only=True,
        help_text="密码"
    )
    
    def validate(self, data):
        """验证用户名/手机号和密码"""
        username_or_phone = data.get('username_or_phone')
        password = data.get('password')
        
        # 尝试通过用户名查找
        try:
            user = User.objects.get(username=username_or_phone)
        except User.DoesNotExist:
            # 尝试通过手机号查找
            try:
                user = User.objects.get(phone=username_or_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("用户名或手机号不存在")
        
        if not user.check_password(password):
            raise serializers.ValidationError("密码错误")
        
        data['user'] = user
        return data


class TokenSerializer(serializers.ModelSerializer):
    """令牌序列化器"""
    class Meta:
        model = UserToken
        fields = ['access_token', 'refresh_token', 'token_type', 'expires_in']


class LoginResponseSerializer(serializers.Serializer):
    """登录响应序列化器"""
    user = UserSerializer()
    token = TokenSerializer()


class ProfileResponseSerializer(serializers.Serializer):
    """用户信息响应序列化器"""
    user_id = serializers.CharField()
    username = serializers.CharField()
    phone = serializers.CharField()
    nickname = serializers.CharField()
    avatar = serializers.CharField()
    created_at = serializers.DateTimeField()
    last_login = serializers.DateTimeField()
    account_status = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField()) 