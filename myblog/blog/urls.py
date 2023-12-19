# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
path('', views.home, name='home'),  # Define your home view and URL name
path('profile/', views.user_profile, name='user_profile'),
path('posts/', views.post_list, name='post_list'),
]