# Generated by Django 3.1.3 on 2021-07-28 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0032_auto_20210723_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafilter',
            name='disable_filter',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='datafilter',
            name='to_include',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]