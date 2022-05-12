from typing import Optional

from django.db import models

from rest_auth.authentication import User
from rest_auth.models.base import BaseModel, NamedModel


ALLOW_OR_DENY = [(True, 'allow'), (False, 'deny')]


class Plugin(BaseModel, NamedModel):
    pass


class Action(BaseModel, NamedModel):
    default_permission = models.BooleanField(choices=ALLOW_OR_DENY)
    owner_applicability = models.BooleanField()
    plugin = models.ForeignKey(Plugin, related_name='actions', on_delete=models.CASCADE)


class ActionsToPermit(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    permit = models.ForeignKey('Permit', on_delete=models.CASCADE)
    permission = models.BooleanField(choices=ALLOW_OR_DENY, null=False, blank=False)
    by_owner_only = models.BooleanField(null=False, default=False, blank=False)

    @property
    def allows(self):
        return self.permission


class Permit(BaseModel):
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='permits')
    actions = models.ManyToManyField(Action,
                                     related_name='permit',
                                     through=ActionsToPermit,
                                     through_fields=('permit', 'action'))

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

        actions = ActionsToPermit.objects.filter(action=act, permit=self)  # what if always one?

        results = set()
        for action in actions:
            if action.by_owner_only and by_owner is True:
                results.add(action.allows)
            elif not action.by_owner_only:
                results.add(action.allows)

        if results:
            return all(results)

    def __str__(self):
        return f'{self.plugin} [{", ".join((act.name for act in self.actions.all()))}]'