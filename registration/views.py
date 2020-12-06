import json
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.urls.base import reverse_lazy
from registration.models import Client
from django.http.response import HttpResponseBadRequest, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from . import forms, models, serializers
from django.contrib import messages
from shop.models import Product
from .decorators import verified_email
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator

@csrf_exempt
def register_page(request: HttpRequest):
    if request.user.is_authenticated:
        return HttpResponseBadRequest('You are already authenticated!')
    form = forms.CreateUserForm()
    if request.method == 'POST':
        form = forms.CreateUserForm(request.POST)
        if form.is_valid():
            email = form['email'].value()
            try:
                User.objects.get(email=email)
                return HttpResponseBadRequest('User with this email already exists!')
            except User.DoesNotExist:
                pass
            form.save()
            username = form['username'].value()
            password = form['password1'].value()
            user = authenticate(request, username=username, password=password)
            login(request, user)
            g = Group.objects.get(name='no_verified_email')
            request.user.groups.set(2)
            send_verify_email(request=request, user_email=email)
            models.Client.objects.create(
                user=request.user,
                name=form['username'].value(),
                email=form['email'].value(),
            )
            messages.success(request, 'User has been created!')
            return redirect('shop:home')
        return JsonResponse(form.errors)

def send_verify_email(request: HttpRequest, user_email):
    user = request.user
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    link = reverse_lazy('registration:verify', kwargs={
                        'uidb64': uidb64, 'token': token})
    activate_url = f'http://{domain}{link}'

    email_subject = 'Verify email'
    email_body = f'Hi {user.username}! Please use this link to verify your email\n{activate_url}'

    send_mail(
        email_subject,
        email_body,
        settings.EMAIL_HOST_USER,
        [user_email],
    )

def verify_email(request: HttpRequest, uidb64, token):
    g = Group.objects.get(name='verified_email')
    g.user_set.remove(request.user.pk)
    request.user.groups.set(1)
    messages.success(request, 'Your email has been verified!')
    return redirect('shop:home')


@csrf_exempt
@login_required
@verified_email
def phone_link(request: HttpRequest):
    form = forms.PhoneLinkForm
    if request.method == 'POST':
        form = forms.PhoneLinkForm(request.POST, instance=request.user.client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Phone has been added!')
            return redirect('shop:home')
        return JsonResponse(form.errors)

@csrf_exempt
@login_required
def profile_pic_link(request: HttpRequest):
    form = forms.ProfilePicForm
    if request.method == 'POST':
        form = forms.ProfilePicForm(request.POST, request.FILES,
                                    instance=request.user.client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture has been added!')
            return redirect('shop:home')
        return JsonResponse(form.errors)


@csrf_exempt
def login_page(request: HttpRequest):
    if request.user.is_authenticated:
        return HttpResponseBadRequest('You are already authenticated!')
    form = forms.LoginForm()
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        username = form['username'].value()
        password = form['password'].value()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'User has been logined!')
            return redirect('shop:home')
        return HttpResponseBadRequest('Username or password are incorrect!')

@login_required
def logout_user(request: HttpRequest):
    logout(request)
    return redirect('registration:login')

@login_required
@csrf_exempt
def change_password(request: HttpRequest):
    form = forms.CheckPasswordForm
    if request.method == 'POST':
        form = forms.CheckPasswordForm(request.POST)
        if form.is_valid():
            username = request.user.username
            password = form['password'].value()
            user = authenticate(request, username=username, password=password)

            if not user == None:
                form = forms.ChangePasswordForm(request.POST, instance=request.user)
                if form.is_valid():
                    form.save()
                    print(request.user.is_authenticated)
                    messages.success(request, 'Password has been changed!')
                    return redirect('shop:home')
            return HttpResponseBadRequest('Password is incorrect!')

        return JsonResponse(form.errors)

@login_required
def profile_page(request: HttpRequest):
    if request.method == 'GET':
        client = request.user.client
        serializer = serializers.ClientSerializer(client)
        return JsonResponse(serializer.data, safe=False)


