from django.db import models
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion
from validator.models.dataset import Dataset
from validator.models.custom_user import User
from os import path
import uuid

def upload_directory(instance, filename):
    # this is a temporarily fixed path, I'll update it with the proper one later:
    storage_path = path.join('testdata/user_data', str(instance.owner), str(instance.id), filename)
    return storage_path


class UserDatasetFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(null=True, blank=True, upload_to=upload_directory)
    file_name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE, null=True)
    dataset = models.ForeignKey(Dataset, related_name='dataset', on_delete=models.CASCADE)
    version = models.ForeignKey(DatasetVersion, related_name='version', on_delete=models.CASCADE)
    variable = models.ForeignKey(DataVariable, related_name='variable', on_delete=models.CASCADE)