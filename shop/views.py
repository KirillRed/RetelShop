import os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from registration.exceptions import LessResolutionError
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
from PIL import Image

"""This app works with products logic"""

def test_send_email(request):
    send_mail('Hello',
    'Test',
    'htds8891@gmail.com',
    ['dasel5287@gmail.com'],
    fail_silently=False)

    return HttpResponse('hello')

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

def thumbnail_product_image(form, photo_name_in_form):
    DEFAULT_IMAGE_PATH = r'F:\RetelShop\images\default_main_photo.png'
    product_image = form[photo_name_in_form].value()
    if str(product_image) != DEFAULT_IMAGE_PATH:
        path = default_storage.save(str(product_image), ContentFile(product_image.read()))
        fn, fext = os.path.splitext(path)
        opened_product_image = Image.open(product_image)
        if opened_product_image.width < settings.MIN_PHOTO_RESOLUTION[0] or opened_product_image.height < settings.MIN_PHOTO_RESOLUTION[1]:
            raise LessResolutionError()
        opened_product_image.thumbnail(settings.MIN_PHOTO_RESOLUTION, Image.ANTIALIAS)
        product_image_path = settings.MEDIA_ROOT + fn + f"_thumbnail.{opened_product_image.format.lower()}"
        opened_product_image.save(product_image_path)
        return product_image_path
    return DEFAULT_IMAGE_PATH


@login_required
@csrf_exempt
def add_product(request: HttpRequest):
    """Adds product to market"""
    if request.method == 'POST':
        prodform = forms.ProductForm(request.POST, request.FILES)
        if prodform.is_valid():
            try:
                product = models.Product(
                    title = prodform['title'].value(),
                    description = prodform['description'].value(),
                    price = prodform['price'].value(),
                    main_photo = prodform['main_photo'].value(),
                    thumbnail_main_photo = thumbnail_product_image(prodform, 'main_photo'),
                    seller = request.user.client,
                    category = models.Category.objects.get(pk=
                                prodform['category'].value()),
                    subcategory = models.SubCategory.objects.get(pk=
                                prodform['subcategory'].value())
                )
            except LessResolutionError:
                return HttpResponseBadRequest('Product image resolution is less than mimimal!')
            product.save()
            product_image = models.ProductImage(
                image = prodform['main_photo'].value(),
                thumbnail_image = thumbnail_product_image(prodform, 'main_photo') ,
                product = models.Product.objects.get(pk=product.pk)
            )
            product_image.save()
            product.images.add(product_image)
            return redirect('shop:home')
        return JsonResponse(prodform.errors)


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
        prodform = forms.ProductForm(request.POST, request.FILES, instance=product)
        if prodform.is_valid():
            prodform.save()
            print(prodform['main_photo'].value())
            try:
                if prodform['main_photo'].value() != product.main_photo:
                    product.thumbnail_main_photo =  thumbnail_product_image(prodform)
                    product.save()
            except LessResolutionError:
                return HttpResponseBadRequest('Product image resolution is less than mimimal!')
            return redirect('shop:home')
        return JsonResponse(prodform.errors)

@login_required
@csrf_exempt  
def add_product_image(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops... Something went wrong!')
    try:
        product = models.Product.objects.get(pk=pk)
    except models.Product.DoesNotExist:
        return HttpResponseNotFound('This product doesn\'t exit!')
    if product.images.count() == 8:
        return HttpResponseBadRequest('You have already 8 images on you photo!')
    if request.method == 'POST':
        if product.seller != request.user.client:
            return HttpResponseForbidden('This isn\'t your product! You can\'t edit it!')
        formset = forms.ImageFormSet(request.POST, request.FILES, queryset=product.images.all(), prefix='pfix')
        print(formset.is_valid())
        if formset.is_valid():
            formset.save()
            print(formset.new_objects)
        else:
            return JsonResponse(formset.errors)
        
        # if form.is_valid():
        #     image = form['image'].value()
        #     opened_image = Image.open(image)
        #     try:
        #         if opened_image.width < settings.MIN_PHOTO_RESOLUTION[0] or opened_image.height < settings.MIN_PHOTO_RESOLUTION[1]:
        #             raise LessResolutionError()
        #     except LessResolutionError:
        #         return HttpResponseBadRequest('Product image resolution is less than mimimal!')
        #     product_image = models.ProductImage(
        #         image = form['image'].value(),
        #         thumbnail_image = thumbnail_product_image(form, 'image') ,
        #         product = models.Product.objects.get(pk=product.pk)
        #     )
        #     product_image.save()
        #     product.images.add(product_image)
        #     return redirect('shop:home')
        # else:
        #     return JsonResponse(form.errors)

@login_required
@csrf_exempt              
def edit_product_image(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops... Something went wrong!')
    try:
        product_image = models.ProductImage.objects.get(pk=pk)
    except models.ProductImage.DoesNotExist:
        return HttpResponseNotFound('This image doesn\'t exit!')
    product = product_image.product
    if request.method == 'POST':
        if product.seller != request.user.client:
            return HttpResponseForbidden('This isn\'t your product! You can\'t edit it!')
        form = forms.ImageForm(request.POST, request.FILES, instance=product_image)
        if form.is_valid():
            image = form['image'].value()
            opened_image = Image.open(image)
            try:
                if opened_image.width < settings.MIN_PHOTO_RESOLUTION[0] or opened_image.height < settings.MIN_PHOTO_RESOLUTION[1]:
                    raise LessResolutionError()
            except LessResolutionError:
                return HttpResponseBadRequest('Product image resolution is less than mimimal!')
            form.save()
            product_image.thumbnail_image = thumbnail_product_image(form, 'image')
            product_image.save()
            return redirect('shop:home')
        return JsonResponse(form.errors)
            
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