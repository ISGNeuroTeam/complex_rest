from django.test import TransactionTestCase as DjangoTransactionTestCase, TestCase as DjangoTestCase
from rest_framework.test import APIClient


class TestCase(DjangoTestCase):
    databases = '__all__'


class TransactionTestCase(DjangoTransactionTestCase):
    databases = '__all__'




