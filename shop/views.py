import json
import os
import logging
import base64
from registration.decorators import verified_email

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from registration.exceptions import LessResolutionError, Base64Error, ExtensionError
from registration.models import Client
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from rest_framework.response import Response
from django.http import JsonResponse
from django.conf import settings
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from . import models, forms
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.db.utils import IntegrityError
from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['jpeg', 'jpg', 'bmp', 'gif', 'png']

"""This app works with products logic"""


def home(request: HttpRequest):
    """Home page with last added products"""
    products = models.Product.objects.all()
    paginator = Paginator(products, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    objects = page.object_list
    objects_serializer = serializers.ProductSerializer(objects, many=True)
    print(objects_serializer)
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    user = request.user
    context = {'objects': objects_serializer.data, 'pages_number': paginator.num_pages,
                'page': page_num, 'vapid_key': vapid_key}
    return JsonResponse(context, safe=False)


def thumbnail_product_image(image, image_name):
    product_image = image
    if image != settings.DEFAULT_IMAGE_PATH:
        path = default_storage.save(image_name, ContentFile(product_image.read()))
        fn, fext = os.path.splitext(path)
        opened_product_image = Image.open(product_image)
        if opened_product_image.width < settings.MIN_PHOTO_RESOLUTION[0] or opened_product_image.height < settings.MIN_PHOTO_RESOLUTION[1]:
            raise LessResolutionError()
        product_image_path = settings.MEDIA_ROOT + fn + f'.{opened_product_image.format.lower()}'
        opened_product_image.save(product_image_path)
        opened_product_image.thumbnail(settings.MIN_PHOTO_RESOLUTION, Image.ANTIALIAS)
        thumbnail_product_image_path = settings.MEDIA_ROOT + fn + f"_thumbnail.{opened_product_image.format.lower()}"
        opened_product_image.save(thumbnail_product_image_path)
        return thumbnail_product_image_path
    return settings.DEFAULT_IMAGE_PATH


def base64_to_image(image_base64):
    if not ';base64,' in image_base64:
        raise Base64Error
    format, imgstr = image_base64.split(';base64,')
    ext = format.split('/')[-1]
    if not ext in IMAGE_EXTENSIONS:
        raise ExtensionError
    image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return image


@login_required
@csrf_exempt
def add_product(request: HttpRequest):
    """Adds product to market"""
    if request.method == 'POST':
        product_serializer = json.loads(request.body)['product']
        image_serializer = json.loads(request.body)['images']
        if len(image_serializer) > 7:
            return HttpResponseBadRequest('You already have 8 images on your photo!')
        try:
            main_photo_base64 = product_serializer['main_photo']
            if main_photo_base64 is not None:
                main_photo = base64_to_image(main_photo_base64)
                main_photo_name = main_photo.name
            else:
                main_photo = settings.DEFAULT_IMAGE_PATH
                main_photo_name = '' # I didn't invented hoe to name it so it is empty string
            product = models.Product(
                title = product_serializer['title'],
                description = product_serializer['description'],
                price = product_serializer['price'],
                main_photo = main_photo,
                thumbnail_main_photo = thumbnail_product_image(main_photo, main_photo_name),
                seller = request.user.client,
                category = models.Category.objects.get(pk=
                            product_serializer['category']),
                subcategory = models.SubCategory.objects.get(pk=
                            product_serializer['subcategory'])
            )
            product.save()
        except ExtensionError:
            return HttpResponseBadRequest('Extension isn\'t suportable')
        except KeyError as ex:
            return HttpResponseBadRequest(f'You must indicate {ex}')
        except LessResolutionError:
            return HttpResponseBadRequest('Product image resolution is less than mimimal!')
        except IntegrityError as ex:
            return HttpResponseBadRequest(ex.args[0][:ex.args[0].find('\n')])
        except (models.Category.DoesNotExist, models.SubCategory.DoesNotExist, TypeError, ValidationError, ValueError, OSError) as ex:
            return HttpResponseBadRequest(ex)
        except Exception as ex:
            logger.exception('Some error detected')
            return HttpResponseBadRequest('Some error detected')
        return add_product_image(request=request, product=product)


@login_required
@csrf_exempt  
def add_product_image(request: HttpRequest, product: models.Product):
    image_serializer = json.loads(request.body)['images']
    for product_image in image_serializer:
        try:
            image_base64 = product_image['image']
            if image_base64 is not None:
                image = base64_to_image(image_base64)
                product_image = models.ProductImage(
                    image = image,
                    thumbnail_image = thumbnail_product_image(image, image.name),
                    product = models.Product.objects.get(pk=product.pk))
                product_image.save()
        except ExtensionError:
            return HttpResponseBadRequest('Extension isn\'t suportable')
        except KeyError as ex:
            return HttpResponseBadRequest(f'You must indicate {ex}')
        except LessResolutionError:
            return HttpResponseBadRequest('Product image resolution is less than mimimal!')
        except IntegrityError as ex:
            return HttpResponseBadRequest(ex.args[0][:ex.args[0].find('\n')])
        except (models.Category.DoesNotExist, models.SubCategory.DoesNotExist, TypeError, ValidationError, ValueError, OSError) as ex:
            return HttpResponseBadRequest(ex)
        except:
            logger.exception('Some error detected')
            return HttpResponseBadRequest('Some error detected')
    return redirect('shop:home')


@login_required
@csrf_exempt
def edit_product(request: HttpRequest):
    """Edits product"""
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops... Something went wrong!')
    try:
        product = models.Product.objects.get(pk=pk)
    except models.Product.DoesNotExist:
        return HttpResponseNotFound('This product doesn\'t exit!')
    if request.method == 'POST':
        if product.seller != request.user.client:
            return HttpResponseForbidden('This isn\'t your product! You can\'t edit it!')
        product_serializer = json.loads(request.body)['product']
        try:
            main_photo_base64 = product_serializer['main_photo']
            if main_photo_base64 is not None:
                main_photo = base64_to_image(main_photo_base64)
                main_photo_name = main_photo.name
            else:
                main_photo = settings.DEFAULT_IMAGE_PATH
                main_photo_name = 'main'
            product.main_photo = main_photo
            product.thumbnail_main_photo = thumbnail_product_image(main_photo, main_photo_name)
            product.title = product_serializer['title']
            product.description = product_serializer['description']
            product.price = product_serializer['price']
            product.category = models.Category.objects.get(pk=product_serializer['category'])
            product.subcategory = models.SubCategory.objects.get(pk=product_serializer['subcategory'])
            product.save()
        except ExtensionError:
            return HttpResponseBadRequest('Extension isn\'t suportable')
        except KeyError as ex:
            return HttpResponseBadRequest(f'You must indicate {ex}')
        except LessResolutionError:
            return HttpResponseBadRequest('Product image resolution is less than mimimal!')
        except IntegrityError as ex:
            return HttpResponseBadRequest(ex.args[0][:ex.args[0].find('\n')])
        except (models.Category.DoesNotExist, models.SubCategory.DoesNotExist, TypeError, ValidationError, ValueError, OSError) as ex:
            return HttpResponseBadRequest(ex)
        except UnidentifiedImageError:
            return HttpResponseBadRequest('This isn\'t image!')
        except FileNotFoundError:
            return HttpResponseBadRequest('This file doesn\'t exist!')
        except:
            logger.exception('Some error detected')
            return HttpResponseBadRequest('Some error detected')
        return redirect('shop:home')



@login_required
@csrf_exempt              
def edit_product_image(request: HttpRequest):
    product_image_pk = request.GET.get('product_image_pk', '')
    if product_image_pk == '':
        return HttpResponseBadRequest('Oops... Something went wrong!')
    try:
        product_image = models.ProductImage.objects.get(pk=product_image_pk)
    except models.ProductImage.DoesNotExist:
        return HttpResponseNotFound('This image doesn\'t exit!')
    if request.method == 'POST':
        if product_image.product.seller != request.user.client:
            return HttpResponseForbidden('This isn\'t your product! You can\'t edit it!')
        try:
            image_serializer = json.loads(request.body)['image']
            image_base64 = image_serializer['image']
            if image_base64 is not None:
                image = base64_to_image(image_base64)
                product_image.image = image
                product_image.thumbnail_image = thumbnail_product_image(image, image.name)
                product_image.save()
        except ExtensionError:
            return HttpResponseBadRequest('Extension isn\'t suportable')
        except KeyError as ex:
            return HttpResponseBadRequest(f'You must indicate {ex}')
        except LessResolutionError:
            return HttpResponseBadRequest('Product image resolution is less than mimimal!')
        except IntegrityError as ex:
            return HttpResponseBadRequest(ex.args[0][:ex.args[0].find('\n')])
        except (models.Category.DoesNotExist, models.SubCategory.DoesNotExist, TypeError, ValidationError, ValueError, OSError) as ex:
            return HttpResponseBadRequest(ex)
        except UnidentifiedImageError:
            return HttpResponseBadRequest('This isn\'t image!')
        except FileNotFoundError:
            return HttpResponseBadRequest('This file doesn\'t exist!')
        except Base64Error:
            return HttpResponseBadRequest('Base64 was incorrect')
        except:
            logger.exception('Some error detected')
            return HttpResponseBadRequest('Some error detected')
        return redirect('shop:home')
        
            
@login_required
@csrf_exempt
def delete_product(request: HttpRequest):
    """Deletes product"""
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseNotFound('Oops... Something went wrong!')
    try:
        product = models.Product.objects.get(pk=pk)
    except models.Product.DoesNotExist:
        return HttpResponseNotFound('This product doesn\'t exit!')
    if request.method == 'DELETE':
        if product.seller != request.user.client:
            return HttpResponseForbidden('This isn\'t your product! You can\'t delete it!')
        product.delete()
        return redirect('shop:home')


@login_required
@csrf_exempt
def delete_product_image(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseNotFound('Oops... Something went wrong!')
    try:
        product_image = models.ProductImage.objects.get(pk=pk)
    except models.ProductImage.DoesNotExist:
        return HttpResponseNotFound('This image doesn\'t exit!')
    if request.method == 'DELETE':
        if product_image.product.seller != request.user.client:
            return HttpResponseForbidden('This isn\'t your product! You can\'t delete it!')
        product_image.delete()
        return redirect('shop:home')
    print(request.method)

@csrf_exempt
def search_products(request: HttpRequest):
    form = forms.SearchForm(request.POST)
    if not form.is_valid():
        return JsonResponse(form.errors)
    query = form['word'].value()
    results = models.Product.objects.filter(Q(description__icontains=query) | Q(title__icontains=query))
    paginator = Paginator(results, 3)
    if 'page' in request.GET:
        page_num = request.GET.get('page')
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    objects = page.object_list
    objects_serializer = serializers.ProductSerializer(objects, many=True)
    context = {'products': objects_serializer.data, 'num_pages': paginator.num_pages,
                'page': page_num}
    return JsonResponse(context, safe=False)

@csrf_exempt
def product_detail(request: HttpRequest):
    """Detailed info about selected product"""
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseNotFound('Oops... Something went wrong!')
    try:
        product = models.Product.objects.get(pk=pk)
    except models.Product.DoesNotExist:
        return HttpResponseNotFound('This product doesn\'t exit!')
    if request.method == 'GET':
        product_serializer = serializers.DetailedProductSerializer(product)
        image_serializer = serializers.ImageSerializer(product.images.all(), many=True)
        context = {'products': product_serializer.data, 'product_images': image_serializer.data}
        return JsonResponse(context, safe=False)

@csrf_exempt
def by_category(request):
    category_pk = request.GET.get('category_pk', '')
    if category_pk == '':
        return HttpResponseBadRequest('Oops... Something went wrong')
    try:
        models.Category.objects.get(pk=category_pk)
    except models.Category.DoesNotExist:
        return HttpResponseNotFound('This category doesn\'t exit!')
    products = models.Product.objects.filter(category=category_pk)
    paginator = Paginator(products, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    objects = page.object_list
    objects_serializer = serializers.ProductSerializer(objects, many=True)
    context = {'objects': objects_serializer.data, 'pages_number': paginator.num_pages}
    return JsonResponse(context, safe=False)


@login_required
@csrf_exempt
def like(request: HttpRequest):
    if request.method == 'POST':
        client = request.user.client
        product_pk = request.GET.get('pk', '')
        if product_pk == '':
            return HttpResponseBadRequest('Oops... Something went wrong')
        try:
            models.Product.objects.get(pk=product_pk)
        except models.Product.DoesNotExist:
            return HttpResponseNotFound('This product does not exit!')
        product = models.Product.objects.get(pk=product_pk)
        if product == '':
            return HttpResponseBadRequest('Oops... Something went wrong!')
        if client in product.likes.all():
            product.likes.remove(client)
            messages.success(request, 'Like was removed succesfully!')
            serializer = serializers.ProductSerializer(product)
            return JsonResponse(serializer.data, safe=False)
        else:
            product.likes.add(client)
            messages.success(request, 'Product was liked succesfully!')
            serializer = serializers.ProductSerializer(product)
            return JsonResponse(serializer.data, safe=False)
            

@login_required
def your_products(request: HttpRequest):
    if request.method == 'GET':
        client = request.user.client
        products = models.Product.objects.filter(seller=client)
        if products.count() == 0:
            return HttpResponse('You haven\'t got any product!')
        print(products)
        serializer = serializers.ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@login_required
@verified_email
def add_product_to_cart(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseNotFound('Oops... Something went wrong!')
    try:
        product = models.Product.objects.get(pk=pk)
    except models.Product.DoesNotExist:
        return HttpResponseNotFound('This product doesn\'t exit!')
    data = json.loads(request.body)
    quantity = int(data['quantity'])
    client = request.user.client
    cart = models.Cart.objects.get(owner=client)
    cart_product = models.CartProduct(
        client=client,
        cart=cart,
        product=product,
        qty=quantity,
        final_price=product.price * quantity
    )
    cart_product.save()
    cart.related_products.add(cart_product)
    cart.total_products += cart_product.qty
    cart.final_price += cart_product.final_price
    cart.save()
    messages.success(request, 'Product was added to cart successfully!')
    return redirect('shop:home')