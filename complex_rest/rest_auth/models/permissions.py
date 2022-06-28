from typing import Optional

from django.db import models

from mixins.models import NamedModel, TimeStampedModel
from rest_auth.authentication import User


ALLOW_OR_DENY = [(True, 'allow'), (False, 'deny')]


class Plugin(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Action(TimeStampedModel, NamedModel):
    default_rule = models.BooleanField(choices=ALLOW_OR_DENY, default=True)
    owner_applicability = models.BooleanField(default=True)
    plugin = models.ForeignKey(Plugin, related_name='actions', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plugin', 'name')


class AccessRule(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    permit = models.ForeignKey('Permit', on_delete=models.CASCADE)
    rule = models.BooleanField(choices=ALLOW_OR_DENY, null=False, blank=False)
    by_owner_only = models.BooleanField(null=False, default=False, blank=False)

    @property
    def allows(self):
        return self.rule


class Permit(TimeStampedModel):
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='permits')
    actions = models.ManyToManyField(Action,
                                     related_name='permit',
                                     through=AccessRule,
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

        actions = AccessRule.objects.filter(action=act, permit=self)  # what if always one?

        results = set()
        for action in actions:
            if not action.by_owner_only or by_owner:
                results.add(action.allows)

        if results:
            return all(results)

    def __str__(self):
        return f'{self.plugin} [{", ".join((act.name for act in self.actions.all()))}]'
