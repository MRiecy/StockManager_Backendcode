"""
风险阈值模块 - URL配置
"""

from django.urls import path
from .views import (
    get_risk_assessment,
    get_max_principal_loss,
    get_volatility,
    get_max_drawdown,
    get_var_value
)

urlpatterns = [
    # 综合风险评估接口
    path('assessment/', get_risk_assessment, name='risk_assessment'),
    
    # 各项指标的独立接口
    path('max-principal-loss/', get_max_principal_loss, name='max_principal_loss'),
    path('volatility/', get_volatility, name='volatility'),
    path('max-drawdown/', get_max_drawdown, name='max_drawdown'),
    path('var/', get_var_value, name='var_value'),
]

