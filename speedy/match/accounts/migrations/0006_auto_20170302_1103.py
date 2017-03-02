# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0005_auto_20170302_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteprofile',
            name='men_to_match',
        ),
        migrations.RemoveField(
            model_name='siteprofile',
            name='other_to_match',
        ),
        migrations.RemoveField(
            model_name='siteprofile',
            name='women_to_match',
        ),
        migrations.AlterField(
            model_name='siteprofile',
            name='max_age_match',
            field=models.SmallIntegerField(default=180, null=True, verbose_name='maximal age to match'),
        ),
        migrations.AlterField(
            model_name='siteprofile',
            name='min_age_match',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='minial age to match'),
        ),
    ]
