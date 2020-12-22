
from registration.models import Client
from django.db import models
from django.core import validators
from django.contrib.auth.models import User



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
                                validators=[validators.MinValueValidator(0)])
    likes = models.ManyToManyField('registration.Client', verbose_name='Likes', null=True, blank=True)
    main_photo = models.ImageField(default=r'F:\RetelShop\images\default_main_photo.png', null=True, blank=True)
    thumbnail_main_photo = models.ImageField(default='default_main_photo.png', null=True, blank=True)
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

class ProductImage(models.Model):
    image = models.ImageField(null=True)
    thumbnail_image = models.ImageField(null=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='images')

class CartProduct(models.Model):
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    cart = models.ForeignKey(to='Cart', on_delete=models.CASCADE, related_name='related_cart')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=13, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.product.title} in cart'

class Cart(models.Model):
    owner = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    products = models.ManyToManyField(to=CartProduct, blank=True, related_name='related_products')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=13, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.owner.name}\'s cart'