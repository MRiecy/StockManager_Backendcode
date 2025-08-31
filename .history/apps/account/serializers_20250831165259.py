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
    """注册序列化器"""
    username = serializers.CharField(max_length=50, min_length=3)
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=11, required=False, allow_blank=True)
    
    def validate_username(self, value):
        """验证用户名是否已存在"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value
    
    def validate(self, data):
        """验证密码确认"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("两次输入的密码不一致")
        return data


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, data):
        """验证用户名和密码"""
        username = data.get('username')
        password = data.get('password')
        
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError("用户名或密码错误")
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("用户名或密码错误")
        
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