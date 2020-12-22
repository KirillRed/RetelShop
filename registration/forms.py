import os
import io
import urllib

from django.core.files import File  # you need this somewhere
from django.contrib.auth.forms import UserCreationForm
from django.core import validators
from django.contrib.auth.models import User
from django import forms
from django.db.models import fields
from . import models
from PIL import Image
from django.forms import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

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
    MIN_RESOLUTION = 300, 300

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].help_text = 'Your profile picture resolution must be at least {0}x{1}\
            resolution and must be square!'.format(self.MIN_RESOLUTION[0], self.MIN_RESOLUTION[1])
    
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

class BalanceForm(forms.Form):
    balance = forms.IntegerField(validators=[validators.MinValueValidator(25, '25 is minimal sum to top up!'),
                                            validators.MaxValueValidator(666666, '666666 is maximal to top up!')])