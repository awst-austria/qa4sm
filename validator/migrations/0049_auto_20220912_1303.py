# Generated by Django 3.2.12 on 2022-09-12 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0048_auto_20220830_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdatasetfile',
            name='lat_name_choices',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdatasetfile',
            name='lon_name_choices',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdatasetfile',
            name='time_name_choices',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdatasetfile',
            name='variable_choices',
            field=models.JSONField(blank=True, null=True),
        ),
    ]