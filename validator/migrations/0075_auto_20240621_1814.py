# Generated by Django 3.2.16 on 2024-06-21 18:14

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0074_auto_20241002_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationrun',
            name='intra_annual_metrics',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='validationrun',
            name='intra_annual_overlap',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='validationrun',
            name='intra_annual_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
