# myapp/urls.py
from django.urls import path
from .views import asset_comparison, yearly_comparison, weekly_comparison, area_comparison

urlpatterns = [
    path('asset_comparison/', asset_comparison, name='asset_comparison'),
    path('timecomparison/yearly_comparison/', yearly_comparison, name='yearly_comparison'),
    path('timecomparison/weekly_comparison/', weekly_comparison, name='weekly_comparison'),
    path('areacomparsion/area_comparison/', area_comparison, name='area_comparison'),
]

