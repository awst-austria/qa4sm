# Generated by Django 3.2.12 on 2022-11-15 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0052_auto_20221115_1418'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='is_only_reference',
            new_name='is_spatial_reference',
        ),
    ]
