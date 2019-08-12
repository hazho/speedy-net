# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-12 09:51
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import speedy.core.base.models
import speedy.core.uploads.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('id', speedy.core.base.models.RegularUDIDField(db_index=True, max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters.', regex='^[1-9][0-9]{19}$')], verbose_name='ID')),
                ('file', models.FileField(upload_to=speedy.core.uploads.utils.uuid_dir, verbose_name='file')),
                ('is_stored', models.BooleanField(default=False, verbose_name='is stored')),
                ('size', models.PositiveIntegerField(default=0, verbose_name='file size')),
            ],
            options={
                'verbose_name': 'file',
                'verbose_name_plural': 'uploaded files',
            },
            bases=(speedy.core.base.models.ValidateModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('file_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.File')),
            ],
            options={
                'verbose_name': 'images',
                'verbose_name_plural': 'uploaded images',
            },
            bases=('uploads.file',),
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Entity', verbose_name='owner'),
        ),
    ]
