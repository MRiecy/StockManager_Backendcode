# myapp/urls.py
from django.urls import path
from .views import get_account_info

urlpatterns = [
    path('account-info/', get_account_info, name='account_info'),
]

