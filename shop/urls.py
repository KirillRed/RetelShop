
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/', views.edit_product, name='edit_product'),
    path('delete_product/', views.delete_product, name='delete_product'),
    path('product_detail/', views.product_detail, name='product_detail'),
    path('by_category/', views.by_category, name='by_category'),
    path('like/', views.like, name='like'),
    path('your_products/', views.your_products, name='your_products'),
    path('search_products/', views.search_products, name='search_products'),
    path('add_product_images/', views.add_product_images, name='add_product_images'),
    path('edit_product_image/', views.edit_product_image, name='edit_product_image'),
    path('delete_product_image/', views.delete_product_image, name='delete_product_image'),
    path('add_product_to_cart/', views.add_product_to_cart, name='add_product_to_cart'),
    path('remove_product_from_cart/', views.remove_product_from_cart, name='remove_product_from_cart'),
    path('get_products_in_cart/', views.get_products_in_cart, name='get_products_in_cart'),
    path('pay_cart/', views.pay_cart, name='pay_cart'),
    path('get_product_specifications/', views.get_product_specifications, name='get_product_specifications'),
    path('set_product_specifications/', views.set_product_specifications, name='set_product_specifications'),
    path('compare_show_all/', views.compare_show_all, name='compare_show_all'),
    path('get_client_lists_of_comparisons/', views.get_client_lists_of_comparisons, name='get_client_lists_of_comparisons'),
    path('add_product_to_comparison_list/', views.add_product_to_comparison_list, name='add_product_to_comparison_list'),
    path('remove_product_from_comparison_list/', views.remove_product_from_compraison_list, name='remove_product_from_compraison_list')
]
