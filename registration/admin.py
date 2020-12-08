from django.contrib import admin
from . import models

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['rating', 'title', 'text', 'target', 'author', 'pk']
    list_display_links = ['title']
    search_fields = ['title']

admin.site.register(models.Client)

admin.site.register(models.Review, ReviewAdmin)

