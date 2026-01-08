"""
URL configuration for project01 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view
from apps.Comparison.urls import timecomparison_urlpatterns, areacomparison_urlpatterns

# 策略接口占位符（临时解决404错误）
@api_view(['GET'])
def strategies_placeholder(request):
    """策略接口占位符 - 待实现完整功能"""
    return JsonResponse({
        'message': '策略功能待实现',
        'strategies': [],
        'status': 'placeholder'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    # 认证模块
    path('api/auth/', include('apps.auth.urls')),
    # 账户信息模块
    path('api/', include('apps.account.urls')),
    # 资产对比模块
    path('api/', include('apps.Comparison.urls')),
    # 时间段对比模块
    path('api/timecomparison/', include((timecomparison_urlpatterns, 'timecomparison'))),
    # 分市场对比模块
    path('api/areacomparsion/', include((areacomparison_urlpatterns, 'areacomparsion'))),
    # 风险阈值模块
    path('api/risk-threshold/', include('apps.risk_threshold.urls')),
    # 策略接口占位符（临时解决404错误）
    path('api/strategies/', strategies_placeholder, name='strategies'),
]

