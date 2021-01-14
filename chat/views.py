import json
import datetime

from PIL.Image import new
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Room, RoomMessage
from .serializers import RoomSerializer, RoomMessageSerializer

from registration.decorators import verified_email
from registration.models import Client
from registration.serializers import ClientSerializer


@login_required
def get_client_rooms(request: HttpRequest):
    client = request.user.client
    chats = Room.objects.by_client(client)
    serializer = RoomSerializer(chats, many=True)
    serializer_data = serializer.data
    new_serializer_data = []
    for room in serializer_data:
        room = dict(room)
        room['first'] = ClientSerializer(Client.objects.get(pk=room['first'])).data
        room['second'] = ClientSerializer(Client.objects.get(pk=room['second'])).data
        new_serializer_data.append(dict(room))
    return JsonResponse(new_serializer_data, safe=False)


@login_required
def get_room_messages(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk ==  '':
        return HttpResponseBadRequest('Oops.. Something went wrong')
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return HttpResponseNotFound('This room does not exist')
    messages = room.messages.all()
    serializer = RoomMessageSerializer(messages, many=True)
    serializer_data = serializer.data
    new_serializer_data = []
    for message in serializer_data:
        message = dict(message)
        message['client'] = ClientSerializer(Client.objects.get(pk=message['client'])).data
        new_serializer_data.append(dict(message))
    return JsonResponse(new_serializer_data, safe=False)


@login_required
@csrf_exempt
def edit_room_message(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong')
    try:
        room_message = RoomMessage.objects.get(pk=pk)
    except RoomMessage.DoesNotExist:
        return HttpResponseNotFound('This message does not exist')
    if request.method == 'POST':
        if room_message.client != request.user.client:
            return HttpResponseBadRequest('This isn\'t your message! You can\'t edit it!')
        data = json.loads(request.body)
        message = data['message']
        if message is None or message == '':
            return HttpResponseBadRequest('Message can\'t be none or empty string!')
        if message.strip() != room_message.message:
            room_message.message = message.strip()
            room_message.edited = True
            room_message.save()
        return redirect('chat:get_client_chats')


@login_required
@csrf_exempt
def delete_room_message(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong')
    try:
        room_message = RoomMessage.objects.get(pk=pk)
    except RoomMessage.DoesNotExist:
        return HttpResponseNotFound('This message does not exist')
    if request.method == 'DELETE':
        if room_message.client != request.user.client:
            return HttpResponseBadRequest('This isn\'t your message! You can\'t delete it!')
        room_message.delete()
        return redirect('chat:get_client_chats')


@login_required
@csrf_exempt
def add_to_black_list(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong')
    try:
        other_client = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exist')
    if request.method == 'POST':
        client = request.user.client
        if other_client not in client.black_list.blocked_clients.all():
            client.black_list.blocked_clients.add(other_client)
            client.save()
            return redirect('chat:get_client_chats')
        else:
            return HttpResponseBadRequest('This client is already in your black list')


@login_required
@csrf_exempt
def remove_from_black_list(request: HttpRequest):
    pk = request.GET.get('pk', '')
    if pk == '':
        return HttpResponseBadRequest('Oops.. Something went wrong')
    try:
        other_client = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return HttpResponseNotFound('This client does not exist')
    if request.method == 'DELETE':
        client = request.user.client
        if other_client in client.black_list.blocked_clients.all():
            client.black_list.blocked_clients.remove(other_client)
            client.save()
            return redirect('chat:get_client_chats')
        else:
            return HttpResponseBadRequest('This client is not in your black list')