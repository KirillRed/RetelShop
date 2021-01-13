from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api_chatbot/', views.send_message, name='api_chatbot')
]