# Generated by Django 3.1.3 on 2021-07-23 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0031_auto_20210505_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetversion',
            name='geographical_range',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uptimeping',
            name='time',
            field=models.DateTimeField(),
        ),
    ]