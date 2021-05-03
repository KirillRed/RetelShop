
from registration.models import Client
from django.db import models
from django.core import validators
from decimal import Decimal, getcontext

import eav



class Category(models.Model):
    title = models.CharField(max_length=30,
                            validators=[validators.MinLengthValidator(3)])
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.title

class SubCategory(models.Model):
    title = models.CharField(max_length=30,
                            validators=[validators.MinLengthValidator(3)])
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title




class Product(models.Model):
    title = models.CharField(max_length=30, 
                            validators=[validators.MinLengthValidator(3)])
    description = models.CharField(max_length=500, blank=True, 
                                    default='There is no description on this product')
    price = models.DecimalField(max_digits=13,
                                decimal_places=2,
                                validators=[validators.MinValueValidator(0), validators.MaxValueValidator(999999)])
    likes = models.ManyToManyField('registration.Client', verbose_name='Likes', blank=True)
    main_photo = models.ImageField(default='default_main_photo.png', blank=True)
    thumbnail_main_photo = models.ImageField(default='default_main_photo.png', blank=True)
    seller = models.ForeignKey(to=Client, related_name='+', default='', on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category,
                                default='Fashion and style',
                                on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=SubCategory,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    default=None,
                                    related_name='subcategories')
    published = models.DateTimeField(auto_now_add=True, db_index=True, 
                                    verbose_name='Published')

    def likes_count(self):
        count = self.likes.count()
        return count

    def get_likes(self):
        return '\n'.join([cl.name for cl in self.likes.all()]) 

    def get_images(self):
        return [img.image for img in self.images.all()]       
     

    def __str__(self) -> str:
        return self.title


eav.register(Product)


class ProductImage(models.Model):
    image = models.ImageField(null=True, blank=True)
    thumbnail_image = models.ImageField(null=True, blank=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='images')

class CartProduct(models.Model):
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    cart = models.ForeignKey(to='Cart', on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.product.title} in cart'

    def final_price(self):
        final_price = format(Decimal(self.product.price * self.qty), '.17')
        getcontext().prec = len(final_price)
        return Decimal(final_price)

    def product_image(self):
        return self.product.thumbnail_main_photo.name

    def product_title(self):
        return self.product.title

    def product_price(self):
        return self.product.price

class Cart(models.Model):
    owner = models.OneToOneField(to=Client, on_delete=models.CASCADE, related_name='cart')
    products = models.ManyToManyField(to=CartProduct, blank=True, related_name='related_cart')

    def __str__(self) -> str:
        return f'{self.owner.name}\'s cart'

    def final_price(self):
        final_price = 0
        for cart_product in self.get_products():
            final_price += cart_product.final_price()
        final_price = format(Decimal(final_price), '.17')
        getcontext().prec = len(final_price)
        return Decimal(final_price)

    def total_products(self):
        total_products = 0
        for cart_product in self.products.all():
            total_products += cart_product.qty
        return total_products

    def get_products(self):
        return [cart_product for cart_product in self.related_products.all()]


class ListOfComparisons(models.Model):
    owner = models.ForeignKey(to=Client, on_delete=models.CASCADE, related_name='list_of_compraisons')
    products = models.ManyToManyField(to=Product, blank=True)
    subcategory = models.ForeignKey(to=SubCategory, on_delete=models.CASCADE)

    def get_products(self):
        return [product for product in self.products.all()]