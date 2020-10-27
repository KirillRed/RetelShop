import json
from django.http import request
from django.shortcuts import redirect
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from .forms import CreateUserForm
from django.contrib import messages

def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User has been created!')
            return redirect('login')
    return JsonResponse(form.errors)

@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'User has been logined!')
            return redirect('get_users')
        return HttpResponseBadRequest('Username or password are incorrect!')

    return HttpResponse('Hello')