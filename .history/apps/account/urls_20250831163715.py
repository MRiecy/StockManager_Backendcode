# myapp/urls.py
from django.urls import path
from .views import get_account_info, get_asset_category
from .auth_views import (
    send_verification_code_api, 
    login_with_phone, 
    refresh_token,
    logout,
    get_user_profile,
    update_user_profile
)

urlpatterns = [
    # 账户信息相关
    path('account-info/', get_account_info, name='account_info'),
    path('asset-category/', get_asset_category, name='asset_category'),
    
    # 认证相关
    path('auth/send-code/', send_verification_code_api, name='send_verification_code'),
    path('auth/login/', login_with_phone, name='login'),
    path('auth/refresh/', refresh_token, name='refresh_token'),
    path('auth/logout/', logout, name='logout'),
    path('auth/profile/', get_user_profile, name='get_user_profile'),
    path('auth/profile/update/', update_user_profile, name='update_user_profile'),
]

