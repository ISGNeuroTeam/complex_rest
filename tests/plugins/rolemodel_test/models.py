from django.db import models
from django.utils import timezone

from rest_auth.models import KeyChainModel, AuthCoveredModel


class PluginKeychain(KeyChainModel):
    pass


class SomePluginAuthCoveredModel(AuthCoveredModel):
    keychain_model = PluginKeychain
