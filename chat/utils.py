from datetime import datetime

from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware

from .models import Room, RoomMessage
from registration.models import Client

from .exceptions import InBlockedListException, ClientException

@database_sync_to_async
def get_user_by_token(headers):
    try:
        token_name, token_key = headers[b'authorization'].decode().split()
        if token_name == 'Token':
            token = Token.objects.get(key=token_key)
            return token.user
        else:
            raise ValueError
    except Token.DoesNotExist:
        return AnonymousUser()
    except ValueError:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            scope['user'] = await get_user_by_token(headers)
        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))

@database_sync_to_async
def get_or_create_room(user, other_client_name):
    client = user.client
    return Room.objects.get_or_new(client, other_client_name)[0]

@database_sync_to_async
def get_client_or_error(user, other_client_name):
    client = user.client
    other_client = Client.objects.get(name=other_client_name)
    if client.name == other_client_name:
        raise ClientException
    if client in other_client.black_list.blocked_clients.all() or other_client in client.black_list.blocked_clients.all():
        raise InBlockedListException
    return other_client

@database_sync_to_async
def create_room_message(room, user, msg):
    room.updated = datetime.now()
    room.save()
    return RoomMessage.objects.create(room=room, client=user.client, message=msg.strip())
