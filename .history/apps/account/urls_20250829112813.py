# myapp/urls.py
from django.urls import path
from .views import get_account_info, get_asset_category

urlpatterns = [
    path('account-info/', get_account_info, name='account_info'),
    path('asset-category/', get_asset_category, name='asset_category'),
]

