import json
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group, UserManager
from django.urls.base import reverse_lazy
from registration.models import Client
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
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
            #form.save()
            username = form['username'].value()
            password = form['password1'].value()
            get_user_model().objects.create_user(username=username, password=password, email=email)
            user = authenticate(request, username=username, password=password)
            login(request, user)
            g = Group.objects.get(name='no_verified_email')
            g.user_set.add(user)
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
    user_id = int(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=user_id)
    no_verified = Group.objects.get(name='no_verified_email')
    no_verified.user_set.remove(user.pk)
    verified = Group.objects.get(name='verified_email')
    verified.user_set.add(user.pk)
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
@verified_email
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
def my_profile_page(request: HttpRequest):
    if request.method == 'GET':
        client = request.user.client
        client_serializer = serializers.ClientSerializer(client)
        reviews = models.Review.objects.filter(target=client.pk)
        review_sarializer = serializers.ReviewSerializer(reviews, many=True)
        avarage_rating_request = request
        avarage_rating_request.GET._mutable = True
        avarage_rating_request.GET['pk'] = client.pk
        avarage_rating = get_avarage_rating(avarage_rating_request).__dict__['_container']
        avarage_rating = str(avarage_rating)
        index = avarage_rating.find(':') + 2
        avarage_rating_str = avarage_rating[index: len(avarage_rating) - 3]
        print(index, len(avarage_rating) - 3, avarage_rating)
        context = {'client': client_serializer.data, 'reviews': review_sarializer.data,
                    'avarage_rating': float(avarage_rating_str)}
        return JsonResponse(context, safe=False)

@verified_email
@csrf_exempt
def add_review(request: HttpRequest):
    target_pk = request.GET.get('pk', '')
    if target_pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        target = models.Client.objects.get(pk=target_pk)
    except models.Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exit!')
    print(type(request.user.client.pk), type(target_pk))
    if int(target_pk) == request.user.client.pk:
        return HttpResponseForbidden('You can\'t add review about yourself')
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST)
        if form.is_valid():
            review = models.Review(
                rating = form['rating'].value(),
                title = form['title'].value(),
                text = form['text'].value(),
                target = target,
                author = request.user.client
            )
            review.save()
            return redirect('shop:home')
        else:
            return JsonResponse(form.errors)

@verified_email
@csrf_exempt
def edit_review(request: HttpRequest):
    review_pk = request.GET.get('pk', '')
    if review_pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        review = models.Review.objects.get(pk=review_pk)
    except models.Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exit!')
    if request.method == 'POST':
        if review.author != request.user.client:
           return HttpResponseForbidden('This isn\'t your review! You can\'t remove it')
        form = forms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('shop:home')
        else:
            return JsonResponse(form.errors)

@verified_email
@csrf_exempt
def delete_review(request: HttpRequest):
    review_pk = request.GET.get('pk', '')
    if review_pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        review = models.Review.objects.get(pk=review_pk)
    except models.Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exit!')
    if request.method == 'DELETE':
        if review.author != request.user.client:
            return HttpResponseForbidden('This isn\'t your review! You can\'t remove it')
        review.delete()
        return redirect('shop:home')

@verified_email
@csrf_exempt
def get_avarage_rating(request: HttpRequest):
    client_pk = request.GET.get('pk', '')
    if client_pk == '':
            return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        client = models.Client.objects.get(pk=client_pk)
    except models.Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exit!')
    client_reviews = models.Review.objects.filter(target=client_pk)
    if len(client_reviews) == 0:
        return JsonResponse({'avarage_rating': 0})
    ratings = []
    for review in client_reviews:
        ratings.append(review.rating)
    avarage_rating = sum(ratings) / len(ratings) 
    return JsonResponse({'avarage_rating': avarage_rating})
    

