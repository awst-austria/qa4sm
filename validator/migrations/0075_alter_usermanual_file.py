# Generated by Django 3.2.16 on 2024-06-21 18:14

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0074_alter_userdatasetfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermanual',
            name='file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='./docs/'), upload_to='./user_manual'),
        ),
    ]
