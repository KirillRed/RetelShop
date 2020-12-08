from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = PhoneNumberField(null=True, unique=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default='default_picture.png' ,null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    #From 1 star to 5 stars
    rating = models.PositiveIntegerField(validators=[validators.MaxValueValidator(5)])
    title = models.CharField(max_length=50, validators=[validators.MinLengthValidator(2)])
    text = models.CharField(max_length=500, validators=[validators.MinLengthValidator(5)])
    #Client-recipient
    target = models.ForeignKey(to=Client, on_delete=models.CASCADE, related_name='+')
    #Client-author
    author = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
     
