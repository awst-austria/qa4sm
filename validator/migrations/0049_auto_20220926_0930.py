# Generated by Django 3.2.12 on 2022-09-26 09:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0048_auto_20220830_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdatasetfile',
            name='all_variables',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdatasetfile',
            name='upload_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
