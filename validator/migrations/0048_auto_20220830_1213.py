# Generated by Django 3.2.12 on 2022-08-30 12:13

import django.core.files.storage
from django.db import migrations, models
import validator.models.user_dataset_file


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0047_alter_userdatasetfile_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdatasetfile',
            name='latname',
            field=models.CharField(blank=True, default='lat', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='userdatasetfile',
            name='lonname',
            field=models.CharField(blank=True, default='lon', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='userdatasetfile',
            name='timename',
            field=models.CharField(blank=True, default='time', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userdatasetfile',
            name='file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/home/tercjak/Projects/qa4sm/testdata/user_data'), upload_to=validator.models.user_dataset_file.upload_directory),
        ),
    ]
