# Generated by Django 3.2.16 on 2024-10-11 11:55

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0075_auto_20240621_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationrun',
            name='stability_metrics',
            field=models.BooleanField(default=False),
        ),
    ]
