from .models import Room, RoomMessage
from rest_framework.serializers import ModelSerializer

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['first', 'second', 'updated']

class RoomMessageSerializer(ModelSerializer):
    class Meta:
        model = RoomMessage
        fields = ['message', 'edited', 'client', 'timestamp']