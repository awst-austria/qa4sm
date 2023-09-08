from django.core.files.storage import FileSystemStorage
from django.db import models

from valentina.settings_conf import USER_DATA_DIR
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion
from validator.models.dataset import Dataset
from validator.models.custom_user import User
from validator.models.dataset_configuration import DatasetConfiguration
from os import path
import uuid
from django.db.models.signals import post_delete, pre_delete
from django.dispatch.dispatcher import receiver
from shutil import rmtree
import os

key_store = FileSystemStorage(location=USER_DATA_DIR)


def upload_directory(instance, filename):
    # this is a temporarily fixed path, I'll update it with the proper one later:
    storage_path = path.join(str(instance.owner), str(instance.id), filename)
    return storage_path


class UserDatasetFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(null=True, blank=True, storage=key_store, upload_to=upload_directory)
    file_name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='user_datasets', on_delete=models.CASCADE, null=True)
    dataset = models.ForeignKey(Dataset, related_name='user_dataset', on_delete=models.SET_NULL, null=True)
    version = models.ForeignKey(DatasetVersion, related_name='user_version', on_delete=models.SET_NULL, null=True)
    variable = models.ForeignKey(DataVariable, related_name='user_variable', on_delete=models.SET_NULL, null=True)
    all_variables = models.JSONField(blank=True, null=True)
    upload_date = models.DateTimeField()
    metadata_submitted = models.BooleanField(default=False)
    # user_groups = models.ManyToManyField(to='DataManagementGroup', related_name='custom_datasets', null=True,
    #                                      blank=True)

    def get_user_data_configs(self):
        return DatasetConfiguration.objects.filter(dataset=self.dataset)

    @property
    def get_raw_file_path(self):
        return self.file.path.rstrip(self.file_name) if self.file else ""

    @property
    def is_used_in_validation(self):
        return len(self.get_user_data_configs()) != 0

    @property
    def owner_validation_list(self):
        return [{'val_id': config.validation.pk, 'val_name': config.validation.user_data_panel_label()} for config in
                self.get_user_data_configs().filter(validation__user=self.owner)]

    @property
    def number_of_other_users_validations(self):
        return len(self.get_user_data_configs().exclude(validation__user=self.owner))

    @property
    def file_size(self):
        if self.file_name is not None:
            return self.file.size
        else:
            return

    def delete_dataset_file(self):
        # # set storage path to an empty string
        # clear all the user management groups if there are no validations run by other users
        if self.number_of_other_users_validations == 0:
            self.dataset.user_groups.clear()
        # remove the file
        if self.file:
            rundir = path.dirname(self.file.path)
            if path.isdir(rundir):
                rmtree(rundir)

        # set file and file name to None
        self.file = None
        self.file_name = None
        self.save()

    def save(self, *args, **kwargs):
        self.dataset.storage_path = "" if not self.file else self.file.path
        self.dataset.save()

        super(UserDatasetFile, self).save(*args, **kwargs)


@receiver(pre_delete, sender=UserDatasetFile)
def auto_delete_dataset_version_variable(sender, instance, **kwargs):
    if instance.dataset and len(instance.dataset.versions.all().exclude(id=instance.version.id)) == 0:
        instance.dataset.delete()
    if instance.version and len(instance.version.versions.all()) == 0:
        instance.version.delete()
    if instance.variable and len(instance.variable.variables.all()) == 0:
        instance.variable.delete()

@receiver(post_delete, sender=UserDatasetFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        rundir = path.dirname(instance.file.path)
        if path.isdir(rundir):
            rmtree(rundir)
