# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-19 15:04
from __future__ import unicode_literals

from django.db import migrations
import speedy.net.accounts.managers


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_auto_20161019_1448'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', speedy.net.accounts.managers.UserManager()),
            ],
        ),
    ]
