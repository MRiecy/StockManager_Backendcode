from django.urls import path
from .views import (
    asset_comparison,
    yearly_comparison,
    weekly_comparison,
    area_comparison
)

# 时间段对比模块路由
timecomparison_urlpatterns = [
    path('yearly_comparison/', yearly_comparison, name='yearly_comparison'),
    path('weekly_comparison/', weekly_comparison, name='weekly_comparison'),
]

# 分市场对比模块路由
areacomparison_urlpatterns = [
    path('area_comparison/', area_comparison, name='area_comparison'),
]

# 资产对比模块路由
urlpatterns = [
    path('asset_comparison/', asset_comparison, name='asset_comparison'),
]
