import uuid
from typing import List
from rest_auth.models import User
from django.test import TransactionTestCase as DjangoTransactionTestCase, TestCase as DjangoTestCase
from rest_framework.test import APIClient, APITestCase as DjangoAPITestCase


class TestCase(DjangoTestCase):
    databases = '__all__'


class TransactionTestCase(DjangoTransactionTestCase):
    databases = '__all__'


class APITestCase(DjangoAPITestCase):
    databases = "__all__"

    def login(self, login: str, password: str):
        response = self.client.post('/auth/login/', data={'login': login, 'password': password})
        ordinary_user_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(ordinary_user_token))


TEST_USER_PASSWORD = 'user11q2w3e4r5t'


def create_test_users(ordinary_users: int = 1) -> (User, List[User]):
    """
    Creates and returns admin user and several ordinary users with names test_user1, test_user2 ...
    Args:
        ordinary_users: number of ordinary users
    """

    admin_user = User.objects.create_superuser('admin', '', 'admin')
    admin_user.set_password('admin')
    admin_user.guid = uuid.uuid4()
    admin_user.save()
    test_users = []
    for i in range(ordinary_users):
        test_user = User(username=f'test_user{i+1}')
        test_user.set_password(TEST_USER_PASSWORD)
        test_user.guid = uuid.uuid4()
        test_user.save()
        test_users.append(test_user)
    return admin_user, test_users
