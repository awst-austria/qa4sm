# Generated by Django 3.2.16 on 2023-06-26 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0064_datamanagementgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdatasetfile',
            name='user_groups',
            field=models.ManyToManyField(null=True, blank=True, related_name='custom_datasets', to='validator.DataManagementGroup'),
        ),
    ]