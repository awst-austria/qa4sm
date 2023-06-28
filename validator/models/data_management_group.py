from django.contrib.auth.models import Group, Permission


class DataManagementGroup(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self,  *args, **kwargs):
        super().save(*args, **kwargs)
