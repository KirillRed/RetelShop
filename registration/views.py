import json
import logging
import re
from registration import exceptions
import stripe
import os
import math
import ast
import base64


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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db.utils import IntegrityError

from chat.models import BlackList
from rest_framework.authtoken.models import Token

stripe.api_key = settings.STRIPE_API_KEY

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['jpeg', 'jpg', 'bmp', 'gif', 'png']

def create_models_for_user(request):
    g = Group.objects.get(name='no_verified_email')
    g.user_set.add(request.user)
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


def validate_username(username):
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long!')
    if len(username) > 12:
        raise ValidationError('Username must be maximum 12 characters long!')
    if username.isnumeric():
        raise ValidationError('Username can\'t be numeric!')
    try:
        User.objects.get(username=username)
        raise ValidationError('User with this username already exists!')
    except User.DoesNotExist:
        pass


@csrf_exempt
def register_page(request: HttpRequest):
    if request.user.is_authenticated:
        return HttpResponseBadRequest('You are already authenticated!')
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        try:
            validate_email(email)
            try:
                if email == 'dasel5287@gmail.com':
                    raise User.DoesNotExist
                User.objects.get(email=email)
                return HttpResponseBadRequest('User with this email already exists!')
            except User.DoesNotExist:
                pass
            username = data['username']
            validate_username(username)
            password = data['password1']
            password2 = data['password2']
            if password != password2:
                return HttpResponseBadRequest('Password aren\'t same!')
            user = get_user_model().objects.create_user(username=username, password=password, email=email)
            validate_password(password, user)
            user.save()
            user = authenticate(request, username=username, password=password)
            login(request, user)
            send_verify_email(request=request, user_email=email)
            return create_models_for_user(request)
        except ValidationError as ex:
            return HttpResponseBadRequest(ex)
            

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


def thumbnail_image(image, image_name, size, profile_pic=False):
    if image != settings.DEFAULT_IMAGE_PATH:
        path = default_storage.save(image_name, ContentFile(image.read()))
        fn, fext = os.path.splitext(path)
        opened_image = Image.open(image)
        if opened_image.width < size[0] or opened_image.height < size[1]:
            raise exceptions.LessResolutionError()
        if profile_pic:
            if opened_image.width != opened_image.height:
                raise exceptions.NotSquareError()
        image_path = settings.MEDIA_ROOT + fn + f'.{opened_image.format.lower()}'
        opened_image.save(image_path)
        opened_image.thumbnail(size, Image.ANTIALIAS)
        thumbnail_image_path = settings.MEDIA_ROOT + fn + f"_thumbnail.{opened_image.format.lower()}"
        opened_image.save(thumbnail_image_path)
        return thumbnail_image_path
    return settings.DEFAULT_IMAGE_PATH


def base64_to_image(image_base64):
    if not ';base64,' in image_base64:
        raise exceptions.Base64Error
    format, imgstr = image_base64.split(';base64,')
    ext = format.split('/')[-1]
    if not ext in IMAGE_EXTENSIONS:
        raise exceptions.ExtensionError
    image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return image


@csrf_exempt
@login_required
@verified_email
def phone_link(request: HttpRequest):
    if request.method == 'POST':
        data = json.loads(request.body)
        client = request.user.client
        try:
            client.phone = data['phone']
            client.full_clean()
            client.save()
        except ValidationError as ex:
            return HttpResponseBadRequest(ex)
        messages.success(request, 'Phone has been added!')
        return redirect(reverse_lazy('registration:profile_page') + f'?pk={request.user.client.pk}')


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
    if request.method == 'POST':
        data = json.loads(request.body)
        profile_pic64 = data['profile_pic']
        try:
            profile_pic_image = base64_to_image(profile_pic64)
            profile_pic_name = profile_pic_image.name
            profile_pic = thumbnail_image(profile_pic_image, profile_pic_name, settings.PROFILE_PICTURE_RESOLUTION, profile_pic=True)
            thumbnail_profile_pic = thumbnail_image(profile_pic_image, profile_pic_name, settings.THUMBNAIL_PROFILE_PICTURE_RESOLUTION, profile_pic=True)
        except exceptions.ExtensionError:
            return HttpResponseBadRequest('Extension isn\'t suportable')
        except exceptions.LessResolutionError:
            return HttpResponseBadRequest('Product image resolution is less than mimimal!')
        except exceptions.NotSquareError:
            return HttpResponseBadRequest('Profile picture must be square')
        client = request.user.client
        client.profile_pic = profile_pic
        client.thumbnail_profile_pic = thumbnail_profile_pic
        client.save()
        messages.success(request, 'Profile picture has been added!')
        return redirect(reverse_lazy('registration:profile_page') + f'?pk={request.user.client.pk}')


@csrf_exempt
def login_page(request: HttpRequest):
    print(request.GET)
    if request.user.is_authenticated:
        return HttpResponseBadRequest('You are already authenticated!')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']

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
    else:
        return HttpResponse('Login page')


@login_required
def logout_user(request: HttpRequest):
    logout(request)
    return redirect('registration:login')


@login_required
@csrf_exempt
@verified_email
def change_password(request: HttpRequest):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.user.username
        password = data['password']
        user = authenticate(request, username=username, password=password)
        if not user == None:
            try:
                password1 = data['password1']
                password2 = data['password2']
                if password1 != password2:
                    return HttpResponseBadRequest('Password aren\'t same!')
                validate_password(password1, request.user)
            except ValidationError as ex:
                return HttpResponseBadRequest(ex)
            request.user.set_password(password1)
            request.user.save()
            login(request, request.user)
            messages.success(request, 'Password has been changed!')
            return redirect(reverse_lazy('registration:profile_page') + f'?pk={request.user.client.pk}')
        return HttpResponseBadRequest('Password is incorrect!')


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
        data = json.loads(request.body)
        try:
            review = models.Review(
                rating = int(data['rating']),
                title = data['title'],
                text = data['text'],
                target = target,
                author = request.user.client
            )
            review.full_clean()
            review.save()
        except IntegrityError as ex:
            return HttpResponseBadRequest(ex.args[0][:ex.args[0].find('\n')])
        except ValueError:
            return HttpResponseBadRequest('Please, write a valid values')
        except ValidationError as ex:
            return HttpResponseBadRequest(ex)
        return redirect(reverse_lazy('registration:profile_page') + f'?pk={target_pk}')

@verified_email
@csrf_exempt
def edit_review(request: HttpRequest):
    review_pk = request.GET.get('pk', '')
    if review_pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        review = models.Review.objects.get(pk=review_pk)
    except models.Review.DoesNotExist:
        return HttpResponseNotFound('This review does not exit!')
    if request.method == 'POST':
        if review.author != request.user.client:
           return HttpResponseForbidden('This isn\'t your review! You can\'t edit it')
        data = json.loads(request.body)
        try:
            review.rating = data['rating']
            review.title = data['title']
            review.text = data['text']
            review.full_clean()
            review.save()
        except IntegrityError as ex:
            return HttpResponseBadRequest(ex.args[0][:ex.args[0].find('\n')])
        except ValueError:
            return HttpResponseBadRequest('Please, write a valid values')
        except ValidationError as ex:
            return HttpResponseBadRequest(ex)
        return redirect(reverse_lazy('registration:profile_page') + f'?pk={review.target.pk}')

@verified_email
@csrf_exempt
def delete_review(request: HttpRequest):
    review_pk = request.GET.get('pk', '')
    if review_pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong!')
    try:
        review = models.Review.objects.get(pk=review_pk)
    except models.Review.DoesNotExist:
        return HttpResponseNotFound('This review does not exit!')
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