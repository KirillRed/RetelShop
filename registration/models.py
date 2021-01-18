from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField



class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    profile_pic = models.ImageField(default='default_profile_pic.png', blank=True)
    balance = models.PositiveIntegerField(default=0)
    bought_products = models.ManyToManyField(to='shop.CartProduct', related_name='client_buyers', blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.user.username

    @name.setter
    def set_name(self, value: str):
        if len(value) > 20:
            raise ValidationError('Name must be maximum 20 characters')
        if len(value) < 3:
            raise ValidationError('Name must be at least 3 characters')
        self.user.username = value

    @property
    def email(self):
        return self.user.email

    @email.setter
    def set_email(self, value: str):
        self.user.email = value

    def get_bought_products(self):
        return [cart_product for cart_product in self.bought_products.all()]

class Review(models.Model):
    #From 1 star to 5 stars
    rating = models.PositiveIntegerField(validators=[validators.MaxValueValidator(5)])
    title = models.CharField(max_length=50, validators=[validators.MinLengthValidator(2)])
    text = models.CharField(max_length=500, validators=[validators.MinLengthValidator(5)])
    #Client-recipient
    target = models.ForeignKey(to=Client, on_delete=models.CASCADE, related_name='review_about_client')
    #Client-author
    author = models.ForeignKey(to=Client, on_delete=models.CASCADE,related_name='client_reviews' )
    date_created = models.DateTimeField(auto_now_add=True)
     
