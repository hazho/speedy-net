# Generated by Django 4.0.7 on 2022-09-05 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0012_alter_siteprofile_likes_to_user_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteprofile',
            name='likes_to_user_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
