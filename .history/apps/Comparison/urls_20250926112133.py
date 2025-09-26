# myapp/urls.py
from django.urls import path
from .views import asset_comparison, yearly_comparison, weekly_comparison, area_comparison, AssetComparisonView

urlpatterns = [
    path('asset_comparison/', AssetComparisonView.as_view(), name='asset_comparison'),
    path('timecomparison/yearly_comparison/', yearly_comparison, name='yearly_comparison'),
    path('timecomparison/weekly_comparison/', weekly_comparison, name='weekly_comparison'),
    path('areacomparsion/area_comparison/', area_comparison, name='area_comparison'),
]

