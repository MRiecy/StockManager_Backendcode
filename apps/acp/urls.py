from django.urls import path
from . import views

urlpatterns = [
    path('asset-category/', views.get_asset_category_data, name='asset_category_data'),
    path('time-data/', views.get_time_data, name='time_data'),
    path('region-data/', views.get_region_data, name='region_data'),
    path('strategies/', views.get_strategies, name='strategies_info'),
    path('execution-result/', views.get_execution_result, name='execution_info'),
]

