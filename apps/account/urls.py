# myapp/urls.py
from django.urls import path
from .views import get_account_info, get_asset_category, get_region_data, get_time_data

urlpatterns = [
    path('account-info/', get_account_info, name='account_info'),
    path('asset-category/', get_asset_category, name='asset_category'),
    path('region-data/', get_region_data, name='region_data'),
    path('time-data/', get_time_data, name='time_data'),
]

