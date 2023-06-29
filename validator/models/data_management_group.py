from django.contrib.auth.models import Group, Permission
from django.db import models


class DataManagementGroup(Group):
    group_owner = models.ForeignKey('User', related_name='group_owner', on_delete=models.CASCADE, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
