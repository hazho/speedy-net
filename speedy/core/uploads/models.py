import os

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from speedy.core.base.models import TimeStampedModel, RegularUDIDField
from speedy.core.base.utils import generate_regular_udid
from .utils import uuid_dir


class File(TimeStampedModel):
    id = RegularUDIDField()
    owner = models.ForeignKey(to='accounts.Entity', verbose_name=_('owner'), on_delete=models.SET_NULL, blank=True, null=True)
    file = models.FileField(verbose_name=_('file'), upload_to=uuid_dir)
    is_stored = models.BooleanField(verbose_name=_('is stored'), default=False)
    size = models.PositiveIntegerField(verbose_name=_('file size'), default=0)

    @cached_property
    def basename(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('uploaded files')

    def __init__(self, *args, **kwargs):
        if (not (kwargs.get('id'))):
            kwargs['id'] = generate_regular_udid()
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.basename

    def save(self, *args, **kwargs):
        self.size = self.file.size
        return super().save(*args, **kwargs)

    def store(self):
        self.is_stored = True
        self.save(update_fields={'is_stored', 'size'})


class Image(File):
    class Meta:
        verbose_name = _('images')
        verbose_name_plural = _('uploaded images')


