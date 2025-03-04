# urls.py

from django.urls import path

from user.views import get_all_users

urlpatterns = [
    path('get_all_users/',get_all_users, name='get_all_users'),
]

