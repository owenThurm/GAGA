# Generated by Django 3.1.5 on 2021-02-06 02:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20210201_0020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promo_account',
            name='target_account',
        ),
        migrations.AddField(
            model_name='promo_account',
            name='target_accounts',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), default=list, size=8),
            preserve_default=False,
        ),
    ]
