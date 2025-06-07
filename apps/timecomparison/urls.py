# timecomparison/urls.py
from django.urls import path
from .views import weekly_comparison, yearly_comparison

urlpatterns = [
    path('weekly_comparison/', weekly_comparison, name='weekly_comparison'),
    path('yearly_comparison/', yearly_comparison, name='yearly_comparison'),
] 