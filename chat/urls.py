from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('get_client_rooms/', views.get_client_rooms, name='get_client_rooms'),
    path('get_room_messages/', views.get_room_messages, name='get_room_messages'),
    path('edit_room_message/', views.edit_room_message, name='edit_room_message'),
    path('delete_room_message/', views.delete_room_message, name='delete_room_message'),
    path('add_to_black_list/', views.add_to_black_list, name='add_to_black_list'),
    path('remove_from_black_list/', views.remove_from_black_list, name='remove_from_black_list')
]