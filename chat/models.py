from registration.models import Client

from django.conf import settings
from django.db import models
from django.db.models import Q


class RoomManager(models.Manager):
    def by_client(self, client):
        qlookup = Q(first=client) | Q(second=client)
        qlookup2 = Q(first=client) & Q(second=client)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return reversed(qs.order_by('updated'))

    def get_or_new(self, client, other_client_name): # get_or_create
        client_name = client.name
        if client_name == other_client_name:
            return None, False
        qlookup1 = Q(first__name=client_name) & Q(second__name=other_client_name)
        qlookup2 = Q(first__name=other_client_name) & Q(second__name=client_name)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = client.__class__
            client2 = Klass.objects.get(name=other_client_name)
            if client != client2:
                obj = self.model(
                        first=client, 
                        second=client2
                    )
                obj.save()
                return obj, True
            return None, False


class Room(models.Model):
    first        = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='room_first')
    second       = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='room_second')
    updated      = models.DateTimeField(auto_now=True)
    timestamp    = models.DateTimeField(auto_now_add=True)
    
    objects      = RoomManager()

    @property
    def room_group_name(self):
        return f'chat_{self.id}'

class RoomMessage(models.Model):
    room      = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL, related_name='messages')
    client        = models.ForeignKey(Client, verbose_name='sender', on_delete=models.CASCADE, related_name='messages')
    message     = models.TextField()
    edited = models.BooleanField(default=False)
    timestamp   = models.DateTimeField(auto_now_add=True)

class BlackList(models.Model):
    owner = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='black_list')
    blocked_clients = models.ManyToManyField(Client, blank=True)

    def get_blocked_clients(self):
        return [client for client in self.blocked_clients.all()]

    def get_blocked_clients_names(self):
        return [client.name for client in self.blocked_clients.all()]