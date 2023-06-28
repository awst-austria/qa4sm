from django.contrib.auth.models import Group, Permission


class DataManagementGroup(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self,  *args, **kwargs):
        super().save(*args, **kwargs)
        self.assign_permissions()

    def assign_permissions(self):
        permissions = [
            ('delete_datamanagementgroup', 'Can delete dataset'),
            ('publish_datamanagementgroup', 'Can publish validations with dataset'),
            ('download_datamanagementgroup', 'Can download dataset file')
        ]

        for codename, name in permissions:
            permission = Permission.objects.get(codename=codename)
            self.permissions.add(permission)