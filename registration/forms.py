from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.db.models import fields
from . import models

class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].null = True
        self.fields['email'].required = True
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ChangePasswordForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class PhoneLinkForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ['phone']

class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ['profile_pic']

class CheckPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ['rating', 'title', 'text']