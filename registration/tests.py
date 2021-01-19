import ast

from django.http.response import HttpResponseBase
from django.test import TestCase
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls.base import reverse_lazy
from registration.models import Client, Review
from shop.models import Cart, CartProduct, Product, Category, SubCategory


def byte_response_to_dict(byte_response):
    decoded_response = byte_response.decode('UTF-8')
    dict_response = ast.literal_eval(decoded_response)
    return dict_response


def user_set_up(name, password, email):
    User = get_user_model()
    user = User.objects.create_user(username=name, password=password, email=email)
    user.save()
    return user


def client_set_up(user):
    client = Client(
            user=user
        )
    client.save()
    return client


def category_set_up(title):
    category = Category(
        title=title,
        slug=title.lower().replace('_', ' ')
    )
    category.save()
    return category


def subcategory_set_up(title, category):
    subcategory = SubCategory(
        title=title,
        slug=title.lower().replace('_', ' '),
        category=category
    )
    subcategory.save()
    return subcategory

def review_set_up(rating, title, text, target, author):
    review = Review(
        rating=rating,
        title=title,
        text=text,
        target=target,
        author=author
    )
    review.save()
    return review


def product_set_up(title, description, price, seller, category, subcategory):
    product = Product(
            title=title,
            description=description,
            price=price,
            seller=seller,
            category=category,
            subcategory=subcategory
        )
    product.save()
    return product


def cart_product_set_up(client, cart, product, qty):
    cart_product = CartProduct(
        cart=cart,
        client=client,
        product=product,
        qty=qty
    )
    cart_product.save()
    return cart_product


def cart_set_up(owner):
    cart = Cart(owner=owner)
    cart.save()
    return cart

class PuchaseHistoryAPITest(APITestCase):
    def setUp(self):
        user = user_set_up('TestPuchaseHistory', 'TestPassword', 'testmail@gmail.com')

        client = client_set_up(user)

        self.client_ = client

        category = category_set_up('Test')

        subcategory = subcategory_set_up('Test', category)

        product = product_set_up('Test', 'Test', 1234, client, category, subcategory)

        self.product = product

        cart = cart_set_up(client)

        cart_product = cart_product_set_up(client, cart, product, 1)

        client.bought_products.add(cart_product)
        client.save()

    def test_get(self):
        product = Product.objects.get(pk=self.product.pk)
        self.client.login(username=self.client_.name, password='TestPassword')
        url = reverse_lazy('registration:purchase_history')
        response = self.client.get(url, follow=True).content
        dict_response = byte_response_to_dict(response)
        self.assertEqual(dict_response[0]['product_title'], product.title)


class AverageRatingAPITest(APITestCase):
    def setUp(self):
        group = Group(
            name='verified_email'
        )
        group.save()

        user_author = user_set_up('TestAverageRating', 'TestPassword', 'testmail@gmail.com')

        group.user_set.add(user_author)

        client_author = client_set_up(user_author)

        self.client_author = client_author

        user_target = user_set_up('TestAverageRating2', 'TestPassword', 'testmail@gmail.com')

        client_target = client_set_up(user_target)

        self.client_target = client_target

        review_set_up(5, 'Test', 'Test', client_target, client_author)

        review_set_up(1, 'Test', 'Test', client_target, client_author)

    def test_get(self):
        expected_result = 3.0
        self.client.login(username=self.client_author.name, password='TestAuthorPassword')
        url = reverse_lazy('registration:average_rating') + f'?pk={self.client_target.pk}'
        response = self.client.get(url, follow=True).content
        dict_response = byte_response_to_dict(response)
        self.assertEqual(dict_response['average_rating'], expected_result)

class ProfilePageAPITest(APITestCase):
    def setUp(self):
        user_author = user_set_up('TestProfilePageAuthor', 'TestAuthorPassword', 'testauthormail@gmail.com')

        group = Group(
            name='verified_email'
        )
        group.save()

        group.user_set.add(user_author)

        client_author = client_set_up(user_author)

        self.client_author = client_author

        user_target = user_set_up('TestProfilePageTarget', 'TestTargetPassword', 'testtargetmail@gmail.com')

        client_target = client_set_up(user_target)

        self.client_target = client_target

        review_set_up(5, 'Test', 'Test', client_target, client_author)

    def test_get(self):
        self.client.login(username=self.client_author.name, password='TestAuthorPassword')
        url = reverse_lazy('registration:profile_page') + f'?pk={self.client_target.pk}'
        response = self.client.get(url, follow=True).content
        dict_response = byte_response_to_dict(response)
        self.assertEqual(dict_response['client']['name'], 'TestProfilePageTarget')
        self.assertEqual(dict_response['reviews'][0]['title'], 'Test')