
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomUser, UserProfile, Post, Comment, Tag, SubscriptionPlan, Like, Bookmark, Follow, Advertisement, Payment


def user_profile(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    return render(request, 'user_profile.html', {'user': user, 'profile': profile})

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})

def home(request):
    return render(request, 'home.html')