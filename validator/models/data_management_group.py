from django.contrib.auth.models import Group, Permission
from django.db import models
from django.db.models import ProtectedError


# from validator.models import User


class DataManagementGroup(Group):
    group_owner = models.ForeignKey('User', related_name='group_owner', on_delete=models.CASCADE, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_list_of_group_ds_used_by_group_users(self):
        return self.custom_datasets.all().filter(dataset_configurations__validation__user__in=self.user_set.all())

    def get_list_of_group_users_using_group_ds(self):
        return self.user_set.all().filter(validationrun__dataset_configurations__dataset__in=
                                          self.get_list_of_group_ds_used_by_group_users())

    def delete(self, using=None, keep_parents=False):
        if self.get_list_of_group_ds_used_by_group_users().exists():
            raise ProtectedError(
                "Cannot delete the group as users have used assigned datasets.",
                self.__class__,
            )
        else:
            super().delete(using=using, keep_parents=keep_parents)
