"""
认证模块URL配置
"""
from django.urls import path
from .views import token_login

urlpatterns = [
    path('token-login/', token_login, name='token_login'),
]







