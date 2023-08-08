# Generated by Django 3.2.16 on 2023-06-29 08:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0065_userdatasetfile_user_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamanagementgroup',
            name='group_owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
