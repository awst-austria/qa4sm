# Generated by Django 2.2.8 on 2020-05-12 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0013_archiving_20200511_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationrun',
            name='doi',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
