
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/', views.edit_product, name='edit_product'),
    path('delete_product/', views.delete_product, name='delete_product'),
    path('product_detail/', views.product_detail, name='product_detail'),
    path('mail/', views.test_send_email, name='mail'),
    path('by_category/', views.by_category, name='by_category'),
    path('like/', views.like, name='like'),
    path('your_products/', views.your_products, name='your_products'),
    path('search_products/', views.search_products, name='search_products'),
    path('add_product_image/', views.add_product_image, name='add_product_image'),
    path('edit_product_image/', views.edit_product_image, name='edit_product_image')
]
