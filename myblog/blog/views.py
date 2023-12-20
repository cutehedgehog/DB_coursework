# blog/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .requests import register_user, authenticate_user, get_all_posts, get_user_profile
from .forms import RegistrationForm, LoginForm
from .models import CustomUser, UserProfile, Post, Comment, Tag, SubscriptionPlan, Like, Bookmark, Follow, Advertisement, Payment


@login_required
def user_profile(request):
    user = request.user
    profile = get_user_profile(user.id)
    return render(request, 'user_profile.html', {'user': user, 'profile': profile})

def post_list(request):
    posts = get_all_posts()
    return render(request, 'post_list.html', {'posts': posts})

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')
