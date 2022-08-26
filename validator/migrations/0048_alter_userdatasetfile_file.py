# Generated by Django 3.2.12 on 2022-08-26 07:14

import django.core.files.storage
from django.db import migrations, models
import validator.models.user_dataset_file


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0047_alter_userdatasetfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdatasetfile',
            name='file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/var/lib/qa4sm-web-val/valentina/data/user_data'), upload_to=validator.models.user_dataset_file.upload_directory),
        ),
    ]
