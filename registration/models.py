from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = PhoneNumberField(null=True, unique=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default='default_picture.png' ,null=True)
    data_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name