# myapp/urls.py
from django.urls import path
from .views import get_account_info, debug_params, debug_xtquant, test_xtquant_environment

urlpatterns = [
    path('account-info/', get_account_info, name='account_info'),
    path('debug-params/', debug_params, name='debug_params'),
    path('debug-xtquant/', debug_xtquant, name='debug_xtquant'),
    path('test-xtquant-env/', test_xtquant_environment, name='test_xtquant_environment'),
]

