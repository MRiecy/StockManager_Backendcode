# myapp/urls.py
from django.urls import path
from .views import get_account_info, get_asset_category
from .auth_views import (
    send_verification_code, login_with_phone, refresh_token,
    logout, get_current_user, get_region_data
)

urlpatterns = [
    # 认证相关接口
    path('auth/send-code/', send_verification_code, name='send_verification_code'),
    path('auth/login/', login_with_phone, name='login_with_phone'),
    path('auth/refresh/', refresh_token, name='refresh_token'),
    path('auth/logout/', logout, name='logout'),
    path('auth/profile/', get_current_user, name='get_current_user'),
    
    # 账户信息相关接口
    path('account-info/', get_account_info, name='account_info'),
    path('asset-category/', get_asset_category, name='asset_category'),
    path('region-data/', get_region_data, name='get_region_data'),
]

