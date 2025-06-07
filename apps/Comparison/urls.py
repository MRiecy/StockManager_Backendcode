# myapp/urls.py
from django.urls import path
from .views import asset_comparison

urlpatterns = [
    path('asset_comparison/', asset_comparison, name='asset_comparison'),
]

