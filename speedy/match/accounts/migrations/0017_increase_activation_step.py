# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import F


def forwards_func(apps, schema_editor):
    SiteProfile = apps.get_model('match_accounts', 'SiteProfile')
    SiteProfile.objects.update(activation_step=F('activation_step') + 2)


def backwards_func(apps, schema_editor):
    SiteProfile = apps.get_model('match_accounts', 'SiteProfile')
    SiteProfile.objects.update(activation_step=F('activation_step') - 2)


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0016_auto_20170724_1513'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
