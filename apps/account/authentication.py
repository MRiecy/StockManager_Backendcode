from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """自定义JWT认证后端"""
    
    def get_user(self, validated_token):
        """
        根据验证后的token获取用户
        """
        try:
            # 从JWT配置中获取user_id_claim
            user_id_claim = getattr(settings, 'SIMPLE_JWT', {}).get('USER_ID_CLAIM', 'user_id')
            user_id = validated_token[user_id_claim]
        except KeyError:
            raise InvalidToken(_('Token contains no recognizable user identification'))

        try:
            # 使用标准的Django User模型
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise InvalidToken(_('User not found'))

        if not user.is_active:
            raise InvalidToken(_('User account is disabled'))

        return user 