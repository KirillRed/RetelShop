from django.db.models import fields
from rest_framework import serializers
from . import models

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ['name', 'email', 'phone', 'balance', 'profile_pic']

class ProfilePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ['name', 'profile_pic']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['rating', 'title', 'text', 'author', 'date_created']