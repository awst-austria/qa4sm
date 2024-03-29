# Generated by Django 3.2.16 on 2023-07-19 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0066_datamanagementgroup_group_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='space_limit',
            field=models.CharField(blank=True, choices=[('no_data', 1), ('basic', 5000000000), ('extended', 10000000000), ('large', 200000000000), ('unlimited', None)], default='basic', max_length=25),
        ),
    ]
