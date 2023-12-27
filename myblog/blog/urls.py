# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [  # Define your home view and URL name
path('profile/', views.user_profile, name='user_profile'),
path('profile/edit/', views.edit_profile, name='edit_profile'),
path('', views.post_list, name='post_list'),
path('register/', views.register, name='register'),
path('login/', views.login, name='login'),
path('logout/', views.logout, name='logout'),
path('posts/<int:post_id>/', views.post_details, name='post_details'),
path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
path('posts/<int:post_id>/add_comment/', views.add_comment, name='add_comment'),
path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like'),
path('toggle_follow/<int:target_user_id>/', views.toggle_follow, name='toggle_follow'),
path('profile/<int:user_id>/', views.profile_view, name='profile_view'),


]
