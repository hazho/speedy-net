# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-21 11:21
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import speedy.core.models
import speedy.net.accounts.managers
import speedy.net.accounts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('id', speedy.core.models.RegularUDIDField(db_index=True, default=speedy.core.models.generate_regular_udid, max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters', regex='[0-9]')], verbose_name='ID')),
                ('username', models.CharField(max_length=120, unique=True, validators=[django.core.validators.RegexValidator(message='Username contains illegal characters.', regex='[a-z0-9]')])),
                ('slug', models.CharField(max_length=120, unique=True, validators=[django.core.validators.RegexValidator(message='Slug contains illegal characters.', regex='[a-z0-9\\-]')])),
            ],
            options={
                'verbose_name': 'entity',
                'verbose_name_plural': 'entity',
            },
        ),
        migrations.CreateModel(
            name='UserEmailAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('is_confirmed', models.BooleanField(default=False, verbose_name='is confirmed')),
                ('is_primary', models.BooleanField(default=False, verbose_name='is primary')),
                ('confirmation_token', models.CharField(blank=True, max_length=32, verbose_name='confirmation token')),
                ('confirmation_sent', models.IntegerField(default=0, verbose_name='confirmation sent')),
            ],
            options={
                'verbose_name': 'email address',
                'verbose_name_plural': 'email addresses',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='accounts.Entity')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=75, verbose_name='first name')),
                ('first_name_en', models.CharField(max_length=75, null=True, verbose_name='first name')),
                ('first_name_he', models.CharField(max_length=75, null=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=75, verbose_name='last name')),
                ('last_name_en', models.CharField(max_length=75, null=True, verbose_name='last name')),
                ('last_name_he', models.CharField(max_length=75, null=True, verbose_name='last name')),
                ('date_of_birth', models.DateField(verbose_name='date of birth')),
                ('gender', models.SmallIntegerField(choices=[(1, 'Female'), (2, 'Male'), (3, 'Other')], verbose_name='I am')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'swappable': 'AUTH_USER_MODEL',
            },
            bases=('accounts.entity', models.Model),
            managers=[
                ('objects', speedy.net.accounts.managers.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='useremailaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_addresses', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.CreateModel(
            name='SiteProfile',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='+', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_active', models.BooleanField(default=False, verbose_name='indicates if a user has ever logged in to the site')),
                ('access_account', speedy.net.accounts.models.AccessField(choices=[(1, 'Only me'), (2, 'Me and my friends'), (4, 'Anyone')], default=4, verbose_name='who can view my account')),
                ('notify_on_message', models.PositiveIntegerField(choices=[(1, 'Notify'), (0, "Don't notify")], default=1, verbose_name='on new messages')),
                ('public_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='accounts.UserEmailAddress', verbose_name='public email')),
            ],
            options={
                'verbose_name': 'Speedy Net Profile',
                'verbose_name_plural': 'Speedy Net Profiles',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
