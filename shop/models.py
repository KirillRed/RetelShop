
from django.db import models
from django.core import validators
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=30,
                            validators=[validators.MinLengthValidator(3)],
                            verbose_name='Title')
    def __str__(self) -> str:
        return self.title





class Product(models.Model):
    title = models.CharField(max_length=30, 
                            validators=[validators.MinLengthValidator(3)],
                            verbose_name='Product')
    description = models.CharField(max_length=500, blank=True, 
                                    default='There is no description on this product',
                                    verbose_name='Description')
    price = models.DecimalField(max_digits=13,
                                decimal_places=2,
                                validators=[validators.MinValueValidator(0)],
                                verbose_name='Price')
    likes = models.PositiveIntegerField(default=0, verbose_name='Likes')
    photo = models.ImageField(verbose_name='Photo of product', null=True, blank=True)
    seller = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               verbose_name='Seller')
    category = models.ForeignKey(to=Category,
                                default='Fashion and style',
                                on_delete=models.CASCADE,
                                verbose_name='Category')
    published = models.DateTimeField(auto_now_add=True, db_index=True, 
                                    verbose_name='Published')

    def __str__(self) -> str:
        return self.title
