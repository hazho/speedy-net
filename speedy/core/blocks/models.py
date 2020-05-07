from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.base.models import TimeStampedModel
from speedy.core.accounts.models import Entity
from .managers import BlockManager


class Block(TimeStampedModel):
    blocker = models.ForeignKey(to=Entity, verbose_name=_('user'), on_delete=models.CASCADE, related_name='blocked_entities')
    blocked = models.ForeignKey(to=Entity, verbose_name=_('blocked user'), on_delete=models.CASCADE, related_name='blocking_entities')

    objects = BlockManager()

    class Meta:
        verbose_name = _('block')
        verbose_name_plural = _('user blocks')
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return "User {} blocked {}".format(self.blocker, self.blocked)

    def save(self, *args, **kwargs):
        # Ensure users can't block themselves.
        if (self.blocker == self.blocked):
            raise ValidationError(_("Users cannot block themselves."))
        return super().save(*args, **kwargs)


