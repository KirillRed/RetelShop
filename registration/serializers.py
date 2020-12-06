from django.db.models import fields
from rest_framework import serializers
from . import models

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ['name', 'email', 'phone', 'profile_pic']