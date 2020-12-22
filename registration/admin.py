from django.contrib import admin
from . import models

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['rating', 'title', 'text', 'target', 'author', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email', 'phone', 'profile_pic', 'pk']
    list_display_links = ['name']
    search_fields = ['name']

admin.site.register(models.Client, ClientAdmin)

admin.site.register(models.Review, ReviewAdmin)

