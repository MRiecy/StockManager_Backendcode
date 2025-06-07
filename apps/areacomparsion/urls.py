# areacomparsion/urls.py
from django.urls import path
from .views import area_comparison

urlpatterns = [
    path('area_comparison/', area_comparison, name='area_comparison'),
] 