# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-03 15:24
from __future__ import unicode_literals

from django.db import migrations
import speedy.net.accounts.managers


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20161103_1524'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', speedy.net.accounts.managers.UserManager()),
            ],
        ),
    ]
