import ast

from django.http.response import HttpResponseBase
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls.base import reverse_lazy
from registration.models import Client
from shop.models import Product, Category, SubCategory


class PuchaseHistoryAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(username='TestName', password='TestPassword', email='testmail@gmail.com')
        user.save()

        client = Client(
                user=user,
                name='TestName',
                email='testmail@gmail.com',
            )
        client.save()

        category = Category(
            title='Test',
            slug='test'
        )
        category.save()

        subcategory = SubCategory(
            title='Test',
            slug='test',
            category=Category.objects.get(pk=category.pk)
        )
        subcategory.save()

        product = Product(
                title='Test',
                description='Test',
                price='3232',
                seller=client,
                category=Category.objects.get(pk=category.pk),
                subcategory=SubCategory.objects.get(pk=subcategory.pk)
            )
        product.save()

        client.bought_products.add(product)
        client.save()

    def test_get(self):
        product = Product.objects.get(pk=1)
        User = get_user_model()
        self.client.login(username='TestName', password='TestPassword')
        url = reverse_lazy('registration:purchase_history')
        response = self.client.get(url, follow=True).content
        dict_response = response.decode('UTF-8')
        mydata = ast.literal_eval(dict_response)
        self.assertEqual(mydata[0]['title'], product.title)