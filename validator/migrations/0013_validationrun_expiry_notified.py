# Generated by Django 2.2.8 on 2020-05-07 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0012_auto_20200506_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationrun',
            name='expiry_notified',
            field=models.BooleanField(default=False),
        ),
    ]
