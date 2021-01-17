import json
import logging
from registration import exceptions
import stripe
import os
import math
import ast


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group, UserManager
from django.urls.base import reverse_lazy
from shop import models as shop_models
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from . import forms, models, serializers, exceptions
from django.contrib import messages
from shop.models import Product
from .decorators import verified_email
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from shop.serializers import CartProductSerializer
from PIL import Image
from stripe.error import InvalidRequestError

from chat.models import BlackList
from rest_framework.authtoken.models import Token

stripe.api_key = settings.STRIPE_API_KEY

logger = logging.getLogger(__name__)

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
                if email == 'dasel5287@gmail.com':
                    raise User.DoesNotExist
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
            client = models.Client.objects.create(
                user=request.user
            )
            client.save()
            shop_models.Cart.objects.create(
                owner=client
            )
            BlackList.objects.create(
                owner=client
            )
            Token.objects.create(
                user=request.user
            )
            messages.success(request, 'User has been created!')
            return redirect('shop:home')
        return JsonResponse(form.errors)


@csrf_exempt
def get_stripe_token(request: HttpRequest):
    if request.method == 'POST':
        print(request.POST)
        return HttpResponse('success')

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
            return redirect(reverse_lazy('registration:profile_page') + f'?pk={request.user.client.pk}')
        return JsonResponse(form.errors)


def validate_profile_pic(request, form):
    MIN_RESOLUTION = (300, 300)
    profile_pic = form['profile_pic'].value()
    if profile_pic != None:
        path = default_storage.save(str(profile_pic), ContentFile(profile_pic.read()))
        fn, fext = os.path.splitext(path)
        opened_profile_pic = Image.open(profile_pic)
        if opened_profile_pic.width != opened_profile_pic.height:
            raise exceptions.NotSquareError()
        if opened_profile_pic.width < MIN_RESOLUTION[0]:
            raise exceptions.LessResolutionError()
        opened_profile_pic.thumbnail(MIN_RESOLUTION, Image.ANTIALIAS)
        profile_pic_path = r'F:\\RetelShop\\images\\' + fn + f"_thumbnail.{opened_profile_pic.format.lower()}"
        opened_profile_pic.save(profile_pic_path)
        client = request.user.client
        client.profile_pic = profile_pic_path
        client.save()
        return True


@csrf_exempt
@login_required
@verified_email
def profile_pic_link(request: HttpRequest):
    form = forms.ProfilePicForm
    if request.method == 'POST':
        form = forms.ProfilePicForm(request.POST, request.FILES,
                                    instance=request.user.client)
        if form.is_valid():
            try:
                validate_profile_pic(request, form)
            except exceptions.NotSquareError:
                return HttpResponseBadRequest('Profile picture must be square!')
            except exceptions.LessResolutionError:
                return HttpResponseBadRequest('Profile picture must be at least 300x300!')

            messages.success(request, 'Profile picture has been added!')
            return redirect(reverse_lazy('registration:profile_page') + f'?pk={request.user.client.pk}')
        return JsonResponse(form.errors)


@csrf_exempt
def login_page(request: HttpRequest):
    print(request.GET)
    if request.user.is_authenticated:
        return HttpResponseBadRequest('You are already authenticated!')
    form = forms.LoginForm()
    if request.method == 'POST':
        try:
            form = forms.LoginForm(request.POST)
            username = form['username'].value()
            password = form['password'].value()

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'User has been logined!')
                print('asd')
                return redirect('shop:home')
        except Exception as ex:
            logger.exception(ex)
            return HttpResponseBadRequest('')
        return HttpResponseBadRequest('Username or password are incorrect!')
    print(request.method)

@login_required
def logout_user(request: HttpRequest):
    logout(request)
    return redirect('registration:login')

@login_required
@csrf_exempt
@verified_email
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
                    return redirect(reverse_lazy('registration:profile_page') + f'?pk={request.user.client.pk}')
            return HttpResponseBadRequest('Password is incorrect!')

        return JsonResponse(form.errors)

@login_required
def profile_page(request: HttpRequest):
    if request.method == 'GET':
        client_pk = request.GET.get('pk', '')
        if client_pk == '':
            return HttpResponseBadRequest('Oops.. Something went wrong!')
        try:
            client = models.Client.objects.get(pk=client_pk)
        except models.Client.DoesNotExist:
            return HttpResponseNotFound('This client does not exit!')
        if client == request.user.client:
            client_serializer = serializers.ClientSerializer(client)
        else:
            client_serializer = serializers.ProfilePageSerializer(client)
        reviews = models.Review.objects.filter(target=client.pk)
        review_sarializer = serializers.ReviewSerializer(reviews, many=True)
        average_rating_request = request
        average_rating_request.GET._mutable = True
        average_rating_request.GET['pk'] = client.pk
        average_rating = get_average_rating(average_rating_request).__dict__['_container']
        average_rating = average_rating[0]
        decoded_rating= average_rating.decode('UTF-8')
        print(decoded_rating)
        dict_rating = ast.literal_eval(decoded_rating)

        context = {'client': client_serializer.data, 'reviews': review_sarializer.data,
                    'average_rating': round(dict_rating['average_rating'], 1)}
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
    try:
        reviews_about_target = models.Review.objects.filter(target=target_pk)
        reviews_about_target.get(author=request.user.client.pk)
        return HttpResponseBadRequest('You have already written review abour this client!')
    except models.Review.DoesNotExist:
        pass
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
            return redirect(reverse_lazy('registration:profile_page') + f'?pk={target_pk}')
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
           return HttpResponseForbidden('This isn\'t your review! You can\'t edit it')
        form = forms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('registration:profile_page') + f'?pk={review.target.pk}')
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
        return redirect(reverse_lazy('registration:profile_page') + f'?pk={review.target.pk}')


@csrf_exempt
def get_average_rating(request: HttpRequest):
    client_pk = request.GET.get('pk', '')
    if client_pk == '':
            return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        client = models.Client.objects.get(pk=client_pk)
    except models.Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exit!')
    client_reviews = models.Review.objects.filter(target=client_pk)
    if len(client_reviews) == 0:
        return JsonResponse({'average_rating': 0})
    ratings = []
    for review in client_reviews:
        ratings.append(review.rating)
    average_rating = sum(ratings) / len(ratings) 
    return JsonResponse({'average_rating': average_rating})



def create_stripe_customer(client, stripeToken):
    customer = stripe.Customer.create(
        email=client.email,
        name=client.name,
        source=stripeToken
    )
    return customer


@csrf_exempt
@login_required
def top_up_balance(request: HttpRequest):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data['amount'])
            if amount > 999999:
                return HttpResponseBadRequest('999999 usd is max price to top up')
            stripeToken = data['stripeToken']
            if stripeToken is None:
                return HttpResponseBadRequest('Stripe token cannot be null!')
            customer = create_stripe_customer(request.user.client, stripeToken)
            charge = stripe.Charge.create(
                    customer=customer,
                    amount=math.ceil(amount * 100),
                    currency='usd',
                    description='Top up balance'
                    )
        except KeyError as ex:
            return HttpResponseBadRequest(f'{ex} is required!')
        except InvalidRequestError as ex:
            return HttpResponseBadRequest(f'Error with stripe token. More information here:\n {ex}')
        except Exception:
            logger.exception('Error')
            return HttpResponseBadRequest('Error')
        client = request.user.client
        client.balance += amount
        messages.success(request, 'Balace was topped up succesfully!') 
        client.save()
        return redirect(reverse_lazy('registration:profile_page') + f'?pk={client.pk}')


@login_required
def purchase_history(request: HttpRequest):
    client = request.user.client
    cart_products = client.get_bought_products()
    serializer = CartProductSerializer(cart_products, many=True)
    return JsonResponse(serializer.data, safe=False)