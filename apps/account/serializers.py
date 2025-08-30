from rest_framework import serializers
from .models import User, VerificationCode, UserToken


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['user_id', 'phone', 'nickname', 'avatar', 'is_new_user', 
                 'created_at', 'last_login', 'account_status']
        read_only_fields = ['user_id', 'created_at', 'last_login']


class VerificationCodeSerializer(serializers.Serializer):
    """验证码序列化器"""
    phone = serializers.CharField(max_length=11, min_length=11)
    
    def validate_phone(self, value):
        """验证手机号格式"""
        if not value.isdigit():
            raise serializers.ValidationError("手机号必须为数字")
        return value


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    phone = serializers.CharField(max_length=11, min_length=11)
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_phone(self, value):
        """验证手机号格式"""
        if not value.isdigit():
            raise serializers.ValidationError("手机号必须为数字")
        return value
    
    def validate_code(self, value):
        """验证验证码格式"""
        if not value.isdigit():
            raise serializers.ValidationError("验证码必须为数字")
        return value


class TokenSerializer(serializers.ModelSerializer):
    """令牌序列化器"""
    class Meta:
        model = UserToken
        fields = ['access_token', 'refresh_token', 'token_type', 'expires_in']


class LoginResponseSerializer(serializers.Serializer):
    """登录响应序列化器"""
    user = UserSerializer()
    token = TokenSerializer()


class SendCodeResponseSerializer(serializers.Serializer):
    """发送验证码响应序列化器"""
    expire_time = serializers.IntegerField()
    can_resend_time = serializers.IntegerField()


class ProfileResponseSerializer(serializers.Serializer):
    """用户信息响应序列化器"""
    user_id = serializers.CharField()
    phone = serializers.CharField()
    nickname = serializers.CharField()
    avatar = serializers.CharField()
    created_at = serializers.DateTimeField()
    last_login = serializers.DateTimeField()
    account_status = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField()) 