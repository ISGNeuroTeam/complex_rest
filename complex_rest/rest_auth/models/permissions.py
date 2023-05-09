from typing import Optional

from django.db import models

from mixins.models import NamedModel, TimeStampedModel
from rest_auth.authentication import User


ALLOW_OR_DENY = [(True, 'allow'), (False, 'deny')]


class Plugin(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class AuthCoveredClass(TimeStampedModel):
    class_import_str = models.CharField(max_length=1024)  # dotted path for import
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='auth_covered_classes')

    def __str__(self):
        return self.class_import_str


class Action(TimeStampedModel, NamedModel):
    default_rule = models.BooleanField(choices=ALLOW_OR_DENY, default=True)
    # define whether by_owner_only field in AccessRule is used
    owner_applicability = models.BooleanField(default=True)
    plugin = models.ForeignKey(Plugin, related_name='actions', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plugin', 'name')


class AccessRule(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='access_rules')
    permit = models.ForeignKey('Permit', on_delete=models.CASCADE, related_name='access_rules')
    rule = models.BooleanField(choices=ALLOW_OR_DENY, null=False, blank=False)
    by_owner_only = models.BooleanField(null=False, default=False, blank=False)

    @property
    def allows(self):
        return self.rule


class PermitKeychain(models.Model):
    keychain_id = models.CharField(
        max_length=256
    )
    auth_covered_class = models.ForeignKey(AuthCoveredClass, on_delete=models.CASCADE, related_name='permit_keychain')
    permit = models.ForeignKey('rest_auth.Permit', on_delete=models.CASCADE, related_name='permit_keychain')

    @classmethod
    def add_permit_to_keychain(cls, auth_covered_class: str, keychain_id: str, permit: 'Permit'):
        auth_covered_class = AuthCoveredClass.objects.get(class_import_str=auth_covered_class)
        permit_keychain, created = PermitKeychain.objects.get_or_create(
                auth_covered_class=auth_covered_class,
                keychain_id=keychain_id,
                permit=permit
        )

    @classmethod
    def get_keychain_permits(cls, auth_covered_class: str, keychain_id: str):
        permit_keychains = PermitKeychain.objects.filter(
            auth_covered_class__class_import_str=auth_covered_class,
            keychain_id=keychain_id
        )
        return list(map(
            lambda permit_keychain: permit_keychain.permit,
            permit_keychains
        ))

    @classmethod
    def get_permit_keychains(cls,  permit: 'Permit'):
        permit_keychains = PermitKeychain.objects.filter(
            permit=permit,
        )
        return list(map(
            lambda permit_keychain: permit_keychain.keychain_id,
            permit_keychains
            )
        )

    @classmethod
    def delete_permissions(cls, auth_covered_class: str, keychain_id: str):
        PermitKeychain.objects.filter(
            keychain_id=keychain_id, auth_covered_class__class_import_str=auth_covered_class
        ).delete()


class Permit(TimeStampedModel):
    actions = models.ManyToManyField(Action,
                                     related_name='permits',
                                     through=AccessRule,
                                     through_fields=('permit', 'action'))

    @property
    def keychain_ids(self):
        return PermitKeychain.get_permit_keychains(self)

    def affects_on(self, user: User):
        for role in self.roles.all():
            if role.contains_user(user):
                return True
        return False

    def allows(self, user: User, act: Action, by_owner: bool = None) -> Optional[bool]:

        if not self.affects_on(user):
            return

        if act not in self.actions.all():
            return

        actions = AccessRule.objects.filter(action=act, permit=self)  # what if always one?

        results = set()
        for action in actions:
            if not action.by_owner_only or by_owner:
                results.add(action.allows)

        if results:
            return all(results)

    def __str__(self):
        return f'[{", ".join((act.name for act in self.actions.all()))}]'
