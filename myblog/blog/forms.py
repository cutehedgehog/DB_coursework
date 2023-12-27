# blog/forms.py

from django import forms
from django.contrib.auth.models import User  # Add this import
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class EditProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea, required=False)
    avatar_url = forms.CharField(max_length=255, required=False)  # Assuming avatar_url is a CharField

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar_url']

class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class RegistrationForm(UserCreationForm):
    bio = forms.CharField(max_length=255, required=False)
    avatar_url = forms.CharField(max_length=255, required=False)  # Assuming avatar_url is a CharField

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'bio', 'avatar_url']

    def save(self, commit=True):
        user = super().save(commit=False)

        # Save the user profile
        user_profile = UserProfile(
            user=user,
            bio=self.cleaned_data['bio'],
            avatar_url=self.cleaned_data['avatar_url']
        )

        if commit:
            user.save()
            user_profile.save()

        return user

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
