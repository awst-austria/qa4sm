from django.core.files.storage import FileSystemStorage
from django.db import models

from valentina.settings import USER_DATA_DIR
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion
from validator.models.dataset import Dataset
from validator.models.custom_user import User
from os import path
import uuid
from django.db.models.signals import post_delete
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
    owner = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE, null=True)
    dataset = models.ForeignKey(Dataset, related_name='dataset', on_delete=models.SET_NULL, null=True)
    version = models.ForeignKey(DatasetVersion, related_name='version', on_delete=models.SET_NULL, null=True)
    variable = models.ForeignKey(DataVariable, related_name='variable', on_delete=models.SET_NULL, null=True)
    lonname = models.CharField(max_length=10, blank=True, null=True, default='lon')
    latname = models.CharField(max_length=10, blank=True, null=True, default='lat')
    timename = models.CharField(max_length=10, blank=True, null=True, default='time')

    @property
    def get_raw_file_path(self):
        return self.file.path.rstrip(self.file_name)

@receiver(post_delete, sender=UserDatasetFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        rundir = path.dirname(instance.file.path)
        if path.isdir(rundir):
            rmtree(rundir)
