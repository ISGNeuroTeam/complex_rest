from typing import Iterable

from django.db import models
from django.utils import timezone

from rest_auth.authorization import auth_covered_method
from rest_auth.models import AuthCoveredModel

from rest_auth.models import KeyChainModel, AuthCoveredModel


class PluginKeychain(KeyChainModel):
    @classmethod
    def get_objects(cls) -> Iterable['IKeyChain']:
        return cls.objects.all()


class SomePluginAuthCoveredModel(AuthCoveredModel):
    keychain_model = PluginKeychain

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @auth_covered_method(action_name='test.protected_action1')
    def test_method1(self):
        print('calling test auth covered method1')

    @auth_covered_method(action_name='test.protected_action2')
    def test_method2(self):
        print('calling test auth covered method2')


