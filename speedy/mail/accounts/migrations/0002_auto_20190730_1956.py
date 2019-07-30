# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-30 16:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='speedy_mail_site_profile', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
