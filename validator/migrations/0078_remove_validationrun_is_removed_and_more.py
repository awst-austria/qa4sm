# Generated by Django 5.1.6 on 2025-03-24 07:53

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0077_validationrun_status_alter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='validationrun',
            name='is_removed',
        ),
    ]
