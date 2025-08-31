# apps/account/urls.py
from django.urls import path
from .views import get_account_info, get_asset_category
from .auth_views import register, login, get_user_profile, update_user_profile, logout, refresh_token

urlpatterns = [
    # 认证相关API
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/profile/', get_user_profile, name='profile'),
    path('auth/profile/update/', update_user_profile, name='profile_update'),
    path('auth/logout/', logout, name='logout'),
    path('auth/refresh/', refresh_token, name='refresh_token'),
    
    # 业务相关API
    path('account-info/', get_account_info, name='account_info'),
    path('asset-category/', get_asset_category, name='asset_category'),
]

