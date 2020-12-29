import ast

from django.http.response import HttpResponseBase
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls.base import reverse_lazy
from registration.models import Client, Review
from shop.models import Product, Category, SubCategory


def byte_response_to_dict(byte_response):
    decoded_response = byte_response.decode('UTF-8')
    dict_response = ast.literal_eval(decoded_response)
    return dict_response

class PuchaseHistoryAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(username='TestName', password='TestPassword', email='testmail@gmail.com')
        user.save()

        client = Client(
                user=user,
                name=user.username,
                email=user.email
            )
        client.save()

        self.client_ = client

        category = Category(
            title='Test',
            slug='test'
        )
        category.save()

        subcategory = SubCategory(
            title='Test',
            slug='test',
            category=category
        )
        subcategory.save()

        product = Product(
                title='Test',
                description='Test',
                price='3232',
                seller=client,
                category=category,
                subcategory=subcategory
            )
        product.save()

        self.product = product

        client.bought_products.add(product)
        client.save()

    def test_get(self):
        product = Product.objects.get(pk=self.product.pk)
        self.client.login(username=self.client_.name, password='TestPassword')
        url = reverse_lazy('registration:purchase_history')
        response = self.client.get(url, follow=True).content
        dict_response = byte_response_to_dict(response)
        self.assertEqual(dict_response[0]['title'], product.title)


class AvarageRatingAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        user_author = User.objects.create_user(username='TestAuthor', password='TestAuthorPassword', email='testauthormail@gmail.com')
        user_author.save()

        group = Group(
            name='verified_email'
        )
        group.save()

        group.user_set.add(user_author)

        client_author = Client(
                user=user_author,
                name=user_author.username,
                email=user_author.email
            )
        client_author.save()

        self.client_author = client_author

        user_target = User.objects.create_user(username='TestTarget', password='TestTargetPassword', email='testtargetmail@gmail.com')
        user_target.save()

        client_target = Client(
                user=user_target,
                name=user_target.username,
                email=user_target.email
            )
        client_target.save()

        self.client_target = client_target

        review_positive = Review(
            rating=5,
            title='Test',
            text='Test',
            target=client_target,
            author=client_author
        )
        review_positive.save()

        review_negative = Review(
            rating=1,
            title='Test',
            text='Test',
            target=client_target,
            author=client_author
        )
        review_negative.save()

    def test_get(self):
        expected_result = 3.0
        self.client.login(username=self.client_author.name, password='TestAuthorPassword')
        url = reverse_lazy('registration:avarage_rating') + '?pk=2'
        response = self.client.get(url, follow=True).content
        dict_response = byte_response_to_dict(response)
        self.assertEqual(dict_response['avarage_rating'], expected_result)

class ProfilePageAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        user_author = User.objects.create_user(username='TestAuthor', password='TestAuthorPassword', email='testauthormail@gmail.com')
        user_author.save()

        group = Group(
            name='verified_email'
        )
        group.save()

        group.user_set.add(user_author)

        client_author = Client(
                user=user_author,
                name=user_author.username,
                email=user_author.email
            )
        client_author.save()

        self.client_author = client_author

        user_target = User.objects.create_user(username='TestTarget', password='TestTargetPassword', email='testtargetmail@gmail.com')
        user_target.save()

        client_target = Client(
                user=user_target,
                name=user_target.username,
                email=user_target.email
            )
        client_target.save()

        self.client_target = client_target

        review = Review(
            rating=5,
            title='Test',
            text='Test',
            target=client_target,
            author=client_author
        )
        review.save()

    def test_get(self):
        self.client.login(username=self.client_author.name, password='TestAuthorPassword')
        url = reverse_lazy('registration:profile_page') + f'?pk={self.client_target.pk}'
        response = self.client.get(url, follow=True).content
        dict_response = byte_response_to_dict(response)
        self.assertEqual(dict_response['client']['name'], 'TestTarget')
        self.assertEqual(dict_response['reviews'][0]['title'], 'Test')