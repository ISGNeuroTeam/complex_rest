import uuid
from typing import Optional, Iterable
from django.db import models

from rest_auth.authorization import auth_covered_method, authz_integration
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

    @classmethod
    @authz_integration(authz_action='create', unique_name_func=lambda x: x.auth_name)
    def create(cls, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        obj = SomePluginAuthCoveredModelUUID(*args, **kwargs)
        obj.id = uuid.uuid4()
        obj.owner = owner
        obj.save()
        return obj

    @property
    def auth_id(self) -> str:
        return str(self.id)

    @property
    def auth_name(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)
