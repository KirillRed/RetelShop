from rest_framework import serializers
from django.contrib.auth.models import User
from . import models
from django.core.paginator import Page


class ListOfComperisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListOfComparisons
        fields = ['owner', 'get_products', 'subcategory']

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartProduct
        fields = ['get_product_title', 'get_product_image', 'get_product_price', 'qty', 'pk']

class CreateProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Product
        fields = ['title', 'description', 'price', 'main_photo', 'category', 'subcategory']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = ['image']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['title']

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubCategory
        fields = ['title']

class DetailedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['title', 'description', 'price', 'likes_count', 'published']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['title', 'price', 'likes_count', 'thumbnail_main_photo', 'published']

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'