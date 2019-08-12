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
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('date_viewed', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes_from_user', to=settings.AUTH_USER_MODEL, verbose_name='from user')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes_to_user', to=settings.AUTH_USER_MODEL, verbose_name='to user')),
            ],
            options={
                'verbose_name': 'user like',
                'verbose_name_plural': 'user likes',
            },
            bases=(speedy.core.base.models.ValidateModelMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='userlike',
            unique_together=set([('from_user', 'to_user')]),
        ),
    ]
