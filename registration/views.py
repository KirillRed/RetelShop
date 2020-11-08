import json
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from . import forms
from django.contrib import messages

@csrf_exempt
def register_page(request):
    form = forms.CreateUserForm()
    if request.method == 'POST':
        form = forms.CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User has been created!')
            return redirect('registration:login')
    return JsonResponse(form.errors)

@csrf_exempt
def login_page(request):
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

def logout_user(request):
    logout(request)
    return redirect('registration:login')
