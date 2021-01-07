from registration.models import Client
from channels.generic.websocket import AsyncWebsocketConsumer

from .utils import get_client_or_error, get_or_create_room, create_room_message

from .exceptions import InBlockedListException

import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.other_client_name = self.scope['url_route']['kwargs']['client_name']
        try:
            await get_client_or_error(user, self.other_client_name)
        except (Client.DoesNotExist, InBlockedListException):
            self.room_name = 'Error'
            self.close()
        else:
            self.room_name = f'room_with_{self.other_client_name}'
            if user.is_anonymous:
                await self.close()
            else:
                #Join room group
                self.room_obj = await get_or_create_room(user, self.other_client_name)
                await self.channel_layer.group_add(
                    self.room_name,
                    self.channel_name
                )
                await self.accept()

    async def disconnect(self, close_code):
        #Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await create_room_message(self.room_obj, self.scope['user'], message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))