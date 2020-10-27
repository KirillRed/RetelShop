from django.urls import path
from . import views

urlpatterns = [
    path('get_users', views.get_users, name='get_users'),
    path('register', views.register, name='register'),
    path('login', views.login_page, name='login'),
]
