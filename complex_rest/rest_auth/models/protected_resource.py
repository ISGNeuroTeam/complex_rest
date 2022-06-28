from django.db import models
from mixins.models import NamedModel
from rest_auth.authentication import User
from rest_auth.models.base import BaseModel
from rest_auth.models import KeyChain


class ProtectedResource(BaseModel, NamedModel):
    object_id = models.CharField(max_length=256, blank=True, null=False, unique=True)
    owner = models.ForeignKey(User, related_name='protected_resources', on_delete=models.CASCADE)
    keychain = models.ForeignKey(KeyChain, related_name='protected_resources', on_delete=models.CASCADE)
