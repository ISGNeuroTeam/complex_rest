from django.db import models

from rest_auth.authentication import User
from rest_auth.models import BaseModel, NamedModel, Permit, Action


class SecurityZone(BaseModel, NamedModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='zones', null=True, blank=True)
    permits = models.ManyToManyField(Permit, related_name='zones', blank=True)
    security_keychain = models.ForeignKey('KeyChain', on_delete=models.CASCADE, null=True,
                                          blank=True)  # should be null=False

    @property
    def effective_permissions(self):
        return self.permits.all().union(self.parent.effective_permissions if self.parent else Permit.objects.none())


class KeyChain(BaseModel):
    zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='keychains', null=True, blank=True)
    permits = models.ManyToManyField(Permit, related_name='keychains', blank=True)

    @property
    def permissions(self):
        return self.permits.all().union(self.zone.effective_permissions if self.zone else Permit.objects.none())

    def allows(self, user: User, act: Action, by_owner: bool = None):
        return any([
            permit.allows(user, act, by_owner) for permit in self.permissions
        ])
