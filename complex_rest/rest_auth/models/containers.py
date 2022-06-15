from django.db import models
from rest_auth.authentication import User
from rest_auth.exceptions import SecurityZoneCircularInheritance
from rest_auth.models import BaseModel, NamedModel, Permit, Action


class SecurityZone(BaseModel, NamedModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='zones', null=True, blank=True)
    permits = models.ManyToManyField(Permit, related_name='zones', blank=True)
    security_keychain = models.ForeignKey('KeyChain', on_delete=models.CASCADE, null=True,
                                          blank=True)  # should be null=False

    @property
    def effective_permissions(self):
        return self.permits.all().union(self.parent.effective_permissions if self.parent else Permit.objects.none())

    def save(self, *args, **kwargs):
        """
        Prevent of assignment successor security zone as a parent
        """

        if self.pk:
            if self.parent and self.parent.pk == self.pk:
                raise SecurityZoneCircularInheritance()  # zone inherits from itself
            children = SecurityZone.objects.raw(
                f"""
                WITH RECURSIVE children(id) AS (
                    SELECT id FROM rest_auth_securityzone WHERE parent_id = {self.pk}
                    UNION 
                    SELECT r.id FROM rest_auth_securityzone r, children p
                    WHERE r.parent_id = p.id
                    )
                SELECT id FROM children;
                """
            )  # Get all the child security zones with a recursive query

            if self.parent in children:
                raise SecurityZoneCircularInheritance()
        else:
            current_parent = self.parent
            heritage = {self.id}
            while current_parent:
                if current_parent.id in heritage:
                    raise SecurityZoneCircularInheritance()
                heritage.add(current_parent.id)
                current_parent = current_parent.parent

        super().save(*args, **kwargs)


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


class ProtectedResource(BaseModel, NamedModel):
    # path to protected resource
    title = models.CharField(max_length=512, blank=True, null=True)
    object_id = models.CharField(max_length=256, blank=True, null=False, unique=True)
    owner = models.ForeignKey(User, related_name='protected_resources', on_delete=models.CASCADE)
    keychain = models.ForeignKey(KeyChain, related_name='protected_resources', on_delete=models.CASCADE)
