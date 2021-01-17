from django.contrib import admin

from . import models

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'get_likes', 'seller', 'category', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

class CartAdmin(admin.ModelAdmin):
    list_display = ['owner', 'get_products', 'get_total_products', 'get_final_price', 'pk']
    list_display_links = ['owner']
    search_fields = ['owner']

class CartProductAdmin(admin.ModelAdmin):
    list_display = ['client', 'cart', 'product', 'qty', 'get_final_price', 'pk']
    list_display_links = ['client']
    search_fields = ['client']

class ListOfComparisonsAdmin(admin.ModelAdmin):
    list_display = ['owner', 'get_products', 'subcategory', 'pk']
    list_display_links = ['owner']
    search_fields = ['owner']

admin.site.register(models.ListOfComparisons, ListOfComparisonsAdmin)

admin.site.register(models.ProductImage)

admin.site.register(models.SubCategory, SubCategoryAdmin)

admin.site.register(models.Product, ProductAdmin)

admin.site.register(models.Category, CategoryAdmin)

admin.site.register(models.Cart, CartAdmin)

admin.site.register(models.CartProduct, CartProductAdmin)