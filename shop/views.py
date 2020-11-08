from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from rest_framework.response import Response
from django.http import JsonResponse
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from . import models, forms
from django.shortcuts import redirect

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
    context = {'objects': objects_serializer.data, 'pages_number': paginator.num_pages}
    return JsonResponse(context, safe=False)

@login_required
@csrf_exempt
def add_product(request: HttpRequest):
    """Adds product to market"""
    if request.method == 'POST':
        prodform = forms.ProductForm(request.POST)
        print(request.POST)
        print(request.data)
        if prodform.is_valid():
            product = models.Product(
                title = prodform['title'].value(),
                description = prodform['description'].value(),
                price = prodform['price'].value(),
                photo = prodform['photo'].value(),
                seller = request.user,
                category = models.Category.objects.get(pk=
                            prodform['category'].value()),
            )
            product.save()
            return redirect('shop:home')
        return JsonResponse(prodform.errors)

@login_required
@csrf_exempt
def edit_product(request: HttpRequest):
    """Edits product"""
    print(request.user)
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops... Something went wrong!')
    try:
        product = models.Product.objects.get(pk=pk)
    except models.Product.DoesNotExist:
        return HttpResponseNotFound('This product doesn\'t exit!')
    if request.method == 'POST':
        if product.seller != request.user:
            return HttpResponseForbidden('This isn\'t your product! You can\'t edit it!')
        prodform = forms.ProductForm(request.POST, request.FILES, instance=product)
        if prodform.is_valid():
            prodform.save()
            return redirect('shop:home')
        return JsonResponse(prodform.errors)

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
        if product.seller != request.user:
            return HttpResponseForbidden('This isn\'t your product! You can\'t delete it!')
        product.delete()
        return redirect('shop:home')

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
        serializer = serializers.ProductSerializer(product)
        return JsonResponse(serializer.data, safe=False)