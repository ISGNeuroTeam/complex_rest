import uuid
from typing import Optional, Iterable
from django.db import models

from rest_auth.authorization import auth_covered_method
from rest_auth.models import KeyChainModel, AuthCoveredModel, List


class PluginKeychain(KeyChainModel):
    auth_covered_class_import_str = 'rolemodel_test.models.SomePluginAuthCoveredModel'


class SomePluginAuthCoveredModel(AuthCoveredModel):
    keychain_model = PluginKeychain

    @auth_covered_method(action_name='test.protected_action1')
    def test_method1(self):
        print('calling test auth covered method1')

    @auth_covered_method(action_name='test.protected_action2')
    def test_method2(self):
        print('calling test auth covered method2')


class PluginKeychainUUID(KeyChainModel):
    auth_covered_class_import_str = 'rolemodel_test.models.SomePluginAuthCoveredModelUUID'
    id = models.UUIDField(primary_key=True, editable=False)

    @classmethod
    def get_keychain(cls, obj_id: str) -> Optional['IKeyChain']:
        return cls.objects.get(id=obj_id)

    @classmethod
    def delete_object(cls, obj_id: str):
        cls.objects.filter(id=obj_id).delete()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)


class SomePluginAuthCoveredModelUUID(AuthCoveredModel):
    keychain_model = PluginKeychainUUID

    id = models.UUIDField(primary_key=True, editable=False)
    _keychain_id = models.UUIDField(null=True, blank=True)

    @auth_covered_method(action_name='test.protected_action1')
    def test_method1(self):
        print('calling test auth covered method1')

    @auth_covered_method(action_name='test.protected_action2')
    def test_method2(self):
        print('calling test auth covered method2')

    @classmethod
    def get_auth_object(cls, obj_id: str) -> 'IAuthCovered':
        return cls.objects.get(pk=obj_id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)
