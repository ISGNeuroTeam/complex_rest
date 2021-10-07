from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

class TestCase(DjangoTestCase):
    databases = '__all__'

