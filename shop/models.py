from django.db import models
from django.core import validators
from django.contrib.auth.models import User

class Product(models.Model):
    title = models.CharField(max_length=30, 
                            validators=[validators.MinLengthValidator(3)],
                            verbose_name='Product')
    description = models.CharField(max_length=500, blank=True, 
                                    default='There is no description on this product',
                                    verbose_name='Description')
    price = models.PositiveIntegerField(verbose_name='Price')
    likes = models.PositiveIntegerField(default=0, verbose_name='Likes')
    photo = models.ImageField(verbose_name='Photo of product')
    seller = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Seller')
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, verbose_name='Category')
    published = models.DateTimeField(auto_now_add=True, db_index=True, 
                                    verbose_name='Published')


class Category(models.Model):
    title = models.CharField(max_length=20,
                            validators=[validators.MinLengthValidator(3)],
                            verbose_name='Title')
    
    