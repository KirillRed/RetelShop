from django.contrib import admin

from . import models

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'likes', 'seller', 'category', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

admin.site.register(models.Product, ProductAdmin)

admin.site.register(models.Category, CategoryAdmin)
