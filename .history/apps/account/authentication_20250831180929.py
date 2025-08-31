from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """自定义JWT认证后端"""
    
    def get_user(self, validated_token):
        """
        根据验证后的token获取用户
        """
        try:
            # 使用父类的user_id_claim属性
            user_id = validated_token[self.user_id_claim]
        except KeyError:
            raise InvalidToken(_('Token contains no recognizable user identification'))

        try:
            # 使用我们的自定义User模型
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise InvalidToken(_('User not found'))

        if not user.is_active:
            raise InvalidToken(_('User account is disabled'))

        return user 