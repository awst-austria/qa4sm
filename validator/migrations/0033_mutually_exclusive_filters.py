# Generated by Django 3.1.3 on 2021-07-15 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0032_auto_20210531_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafilter',
            name='disable_filter',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='validationrun',
            name='upscaling_method',
            field=models.CharField(blank=True, choices=[('none', 'Do not upscale point measurements'), ('average', 'Average point measurements')], default='none', max_length=50),
        ),
    ]
