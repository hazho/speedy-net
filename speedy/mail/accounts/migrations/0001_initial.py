# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-12 09:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import speedy.core.base.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_auto_20190812_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteProfile',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('last_visit', models.DateTimeField(auto_now_add=True, verbose_name='last visit')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='speedy_mail_site_profile', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Speedy Mail Profile',
                'verbose_name_plural': 'Speedy Mail Profiles',
            },
            bases=(speedy.core.base.models.ValidateModelMixin, models.Model),
        ),
    ]
