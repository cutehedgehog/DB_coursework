# blog/forms.py

from django import forms
from django.contrib.auth.models import User  # Add this import
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegistrationForm(UserCreationForm):
    bio = forms.CharField(max_length=255, required=False)
    avatar_url = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'bio', 'avatar_url']

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
