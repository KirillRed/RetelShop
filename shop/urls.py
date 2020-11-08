from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/', views.edit_product, name='edit_product'),
    path('delete_product/', views.delete_product, name='delete_product'),
]
